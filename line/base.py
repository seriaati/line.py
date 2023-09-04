import asyncio
import importlib
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Type, TypeVar

from aiohttp import web
from aiohttp.web_runner import TCPSite
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    AsyncMessagingApiBlob,
    Configuration,
)
from linebot.v3.webhook import Event, InvalidSignatureError, WebhookParser
from linebot.v3.webhooks import MessageEvent, PostbackEvent

from .context import Context
from .exceptions import CogLoadError, CommandExecError, IntConvertError, ParamParseError

pathOrClass = TypeVar("pathOrClass", str, Type["Cog"])


class Bot:
    def __init__(self, *, channel_secret: str, access_token: str) -> None:
        self.channel_secret = channel_secret
        self.access_token = access_token
        self.cogs: List["Cog"] = []
        self.app = web.Application()

        if not (self.channel_secret and self.access_token):
            raise ValueError("Channel secret and channel access token must be provided")
        configuration = Configuration(access_token=self.access_token)
        self.async_api_client = AsyncApiClient(configuration)
        self.line_bot_api = AsyncMessagingApi(self.async_api_client)
        self.blob_api = AsyncMessagingApiBlob(self.async_api_client)
        self.parser = WebhookParser(self.channel_secret)

    @staticmethod
    def setup_logging() -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(),
            ],
        )

    @staticmethod
    def data_parser(param_string: str) -> Dict[str, Optional[str]]:
        param_dict = {}
        if param_string:
            params = param_string.split("&")
            for param in params:
                key_value = param.split("=")
                if len(key_value) >= 2:
                    key = key_value[0]
                    value = "=".join(key_value[1:])
                    if value:
                        if value == "None":
                            value = None
                        param_dict[key] = value

        return param_dict

    @staticmethod
    def param_parser(
        params: Dict[str, inspect.Parameter], data: Dict[str, Optional[str]]
    ) -> Tuple[List[Any], Dict[str, Any]]:
        args: List[Any] = []
        kwargs: Dict[str, Any] = {}
        for param in params.values():
            if param.name in ("self", "ctx"):
                continue
            default = (
                None if param.default == inspect.Parameter.empty else param.default
            )
            value = data.get(param.name, default)
            if param.annotation == int or param.annotation == Optional[int]:
                if value is None:
                    raise IntConvertError(param.name, value)
                if not value.isdigit():
                    raise IntConvertError(param.name, value)
                value = int(value)
            if param.kind == inspect.Parameter.KEYWORD_ONLY:
                kwargs[param.name] = value
            else:
                args.append(value)
        return args, kwargs

    @staticmethod
    async def error_handler(exception: Exception) -> None:
        logging.exception(exception)

    async def command_handler(self, request: web.Request) -> web.Response:
        try:
            signature = request.headers["X-Line-Signature"]
            body = await request.text()

            try:
                events: List[Event] = self.parser.parse(body, signature)  # type: ignore
            except InvalidSignatureError:
                logging.error("Invalid signature")
                return web.Response(status=400, text="Invalid signature")

            for event in events:
                if isinstance(event, PostbackEvent):
                    if event.postback is None:
                        logging.error("Postback event has no postback data")
                        continue
                    text = event.postback.data
                elif isinstance(event, MessageEvent):
                    if not hasattr(event.message, "text"):
                        logging.error("Message event has no text")
                        continue
                    text = event.message.text  # type: ignore
                else:
                    logging.error("Event type is not supported")
                    continue

                data = self.data_parser(text)
                cmd = data.get("cmd")
                if cmd is None:
                    continue

                user_id = event.source.user_id  # type: ignore
                reply_token = event.reply_token
                ctx = Context(
                    user_id=user_id, api=self.line_bot_api, reply_token=reply_token
                )
                for cog in self.cogs:
                    for name, func in cog.commands.items():
                        if name != cmd:
                            continue
                        sig = inspect.signature(func.original_function)
                        params = sig.parameters
                        try:
                            args, kwargs = self.param_parser(params, data)  # type: ignore
                        except Exception as e:
                            raise ParamParseError(name, e)

                        try:
                            await func(ctx, *args, **kwargs)
                        except Exception as e:
                            raise CommandExecError(name, e)
                        return web.Response(text="OK", status=200)
            return web.Response(text="OK", status=200)
        except Exception as e:
            await self.error_handler(e)
            return web.Response(text="Internal server error", status=500)

    async def setup_hook(self) -> None:
        pass

    async def on_close(self) -> None:
        pass

    async def run_tasks(self) -> None:
        pass

    async def run(self, port: int = 8000) -> None:
        self.setup_logging()
        await self.setup_hook()
        self.app.add_routes([web.post("/line", self.command_handler)])
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = TCPSite(runner=runner, port=port)
        await site.start()
        logging.info("Server started at port %d", port)
        try:
            while True:
                # run tasks every minute
                await self.run_tasks()
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            logging.info("Server shutting down")
            await self.on_close()
            await site.stop()
            await self.app.shutdown()
            await self.async_api_client.close()
            await runner.cleanup()

    def add_cog(self, cog_path_or_cog_class: pathOrClass) -> None:
        try:
            if isinstance(cog_path_or_cog_class, str):
                # cog path, example: bot.cogs.info
                module = importlib.import_module(cog_path_or_cog_class)
                # get all classes in the module that is subclass of Cog and not Cog itself
                classes = inspect.getmembers(module, inspect.isclass)
                classes = [
                    class_
                    for class_ in classes
                    if issubclass(class_[1], Cog) and class_[1] != Cog
                ]
                if not classes:
                    raise CogLoadError(cog_path_or_cog_class, "No Cog subclass found")
                if len(classes) > 1:
                    raise CogLoadError(
                        cog_path_or_cog_class, "Multiple Cog subclasses found"
                    )
                cog_class = classes[0][1]
                self.cogs.append(cog_class(self))
            else:
                self.cogs.append(cog_path_or_cog_class(self))
        except Exception as e:
            raise CogLoadError(cog_path_or_cog_class, e)


class Cog:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.commands: Dict[str, Callable[..., Awaitable[None]]] = {}
        self.__initialize_commands()

    def __initialize_commands(self) -> None:
        funcs = inspect.getmembers(self, inspect.ismethod)
        funcs = [func for func in funcs if getattr(func[1], "__is_command__", False)]
        self.commands = {func[0]: func[1] for func in funcs}


def command(func: Callable[..., Awaitable[None]]):
    async def wrapper(*args, **kwargs):
        await func(*args, **kwargs)

    setattr(wrapper, "__is_command__", True)
    wrapper.original_function = func

    return wrapper
