import asyncio
import importlib
import inspect
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from aiohttp import web
from aiohttp.web_runner import TCPSite
from linebot.v3.messaging import (
    ApiException,
    AsyncApiClient,
    AsyncMessagingApi,
    AsyncMessagingApiBlob,
    Configuration,
    CreateRichMenuAliasRequest,
    Message,
    PushMessageRequest,
    RichMenuBulkLinkRequest,
    RichMenuRequest,
    RichMenuResponse,
    UpdateRichMenuAliasRequest,
)
from linebot.v3.webhook import Event, InvalidSignatureError, WebhookParser
from linebot.v3.webhooks import FollowEvent, MessageEvent, PostbackEvent

from .context import Context
from .exceptions import (
    CogLoadError,
    CommandExecError,
    FloatConvertError,
    IntConvertError,
    ParamParseError,
)

pathOrClass = TypeVar("pathOrClass", str, Type["Cog"])


class BaseBot:
    def __init__(self, *, channel_secret: str, access_token: str) -> None:
        configuration = Configuration(access_token=access_token)

        self.async_api_client = AsyncApiClient(configuration)
        self.line_bot_api = AsyncMessagingApi(self.async_api_client)
        self.blob_api = AsyncMessagingApiBlob(self.async_api_client)
        self.webhook_parser = WebhookParser(channel_secret)

        self.cogs: List[Cog] = []
        self.app = web.Application()
        self.session = self.async_api_client.rest_client.pool_manager
        self.task_interval = 60

    @staticmethod
    def _setup_logging(log_to_stream: bool) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler("bot.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        if not log_to_stream:
            logging.getLogger().removeHandler(logging.StreamHandler())

    @staticmethod
    def _parse_data(param_string: str) -> Dict[str, Optional[str]]:
        """Parses a string of parameters into a dictionary.

        Args:
            param_string (str): The string of parameters.

        Returns:
            Dict[str, Optional[str]]: The dictionary of parameters.
        """
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
    def _parse_params(
        params: Dict[str, inspect.Parameter], data: Dict[str, Optional[str]]
    ) -> Tuple[Sequence[Any], Dict[str, Any]]:
        args: Sequence[Any] = []
        kwargs: Dict[str, Any] = {}

        for param in list(params.values())[2:]:
            default = (
                None if param.default == inspect.Parameter.empty else param.default
            )
            value = data.get(param.name, default)

            if (
                param.annotation is int
                or param.annotation == Optional[int]
                or param.annotation == int | None
            ) and isinstance(value, str):
                if not value.isdigit():
                    raise IntConvertError(param.name, value)
                value = int(value)
            elif (
                param.annotation is float
                or param.annotation == Optional[float]
                or param.annotation == float | None
            ) and isinstance(value, str):
                try:
                    value = float(value)
                except ValueError as e:
                    raise FloatConvertError(param.name, value) from e
            elif (
                param.annotation is bool
                or param.annotation == Optional[bool]
                or param.annotation == bool | None
            ) and isinstance(value, str):
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False

            if param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                kwargs[param.name] = value
            else:
                args.append(value)
        return args, kwargs

    async def _handle_request(self, request: web.Request) -> web.Response:
        try:
            signature = request.headers["X-Line-Signature"]
            body = await request.text()

            try:
                events: List[Event] = self.webhook_parser.parse(body, signature)  # type: ignore
            except InvalidSignatureError:
                logging.error("Invalid signature")
                return web.Response(status=400, text="Invalid signature")

            for event in events:
                if isinstance(event, PostbackEvent):
                    await self.on_postback(event)
                elif isinstance(event, MessageEvent):
                    await self.on_message(event)
                elif isinstance(event, FollowEvent):
                    await self.on_follow(event)
                else:
                    logging.error("Event type %s is not supported", type(event))
                    continue
        except Exception as e:
            await self.on_error(e)
            return web.Response(text="Internal server error", status=500)
        else:
            return web.Response(text="OK", status=200)

    # event handlers

    async def on_postback(self, event: PostbackEvent) -> None:
        await self.process_command(
            event.postback.data,
            event.source.user_id,  # type: ignore
            event.reply_token,  # type: ignore
        )

    async def on_message(self, event: MessageEvent) -> None:
        await self.process_command(
            event.message.text,  # type: ignore
            event.source.user_id,  # type: ignore
            event.reply_token,  # type: ignore
        )

    async def on_follow(self, event: FollowEvent) -> None:
        pass

    async def on_error(self, error: Exception) -> None:
        logging.exception(error)

    # command processing

    async def process_command(self, text: str, user_id: str, reply_token: str) -> Any:
        data = self._parse_data(text)
        ctx = Context(user_id=user_id, api=self.line_bot_api, reply_token=reply_token)

        cmd = data.get("cmd")
        if not cmd:
            return

        for cog in self.cogs:
            func = cog.commands.get(cmd)
            if func:
                sig = inspect.signature(func.original_function)
                params = sig.parameters
                try:
                    args, kwargs = self._parse_params(params, data)  # type: ignore
                except Exception as e:
                    raise ParamParseError(cmd, e) from e

                try:
                    await func(ctx, *args, **kwargs)
                except Exception as e:
                    raise CommandExecError(cmd, e) from e

                break

    # rich menu

    async def create_rich_menu(
        self,
        rich_menu_request: RichMenuRequest,
        rich_menu_img_path: str,
        *,
        alias: Optional[str] = None,
    ) -> str:
        """
        Creates a new rich menu with the specified request and image, and returns the ID of the created rich menu.

        Args:
            rich_menu_request (RichMenuRequest): The request object containing the details of the rich menu to be created.
            rich_menu_img_path (str): The file path of the image to be used as the rich menu image.
            alias (Optional[str], optional): The alias to be created for the rich menu. Defaults to None.

        Returns:
            str: The ID of the created rich menu.
        """
        result = await self.line_bot_api.create_rich_menu(rich_menu_request)
        with open(rich_menu_img_path, "rb") as f:
            await self.blob_api.set_rich_menu_image(
                result.rich_menu_id,
                body=bytearray(f.read()),
                _headers={"Content-Type": "image/png"},
            )
        if alias:
            try:
                await self.create_rich_menu_alias(result.rich_menu_id, alias)
            except ApiException as e:
                if e.status == 400:
                    await self.update_rich_menu_alias(result.rich_menu_id, alias)
        return result.rich_menu_id

    async def link_rich_menu_to_users(self, rich_menu_id: str, user_ids: List[str]):
        """
        Links the specified rich menu to the specified users.

        Args:
            rich_menu_id (str): The ID of the rich menu to be linked.
            user_ids (List[str]): The list of user IDs to be linked to the rich menu.

        Returns:
            None
        """
        await self.line_bot_api.link_rich_menu_id_to_users(
            RichMenuBulkLinkRequest(richMenuId=rich_menu_id, userIds=user_ids)
        )

    async def create_rich_menu_alias(self, rich_menu_id: str, alias: str) -> None:
        """
        Creates an alias for the specified rich menu.

        Args:
            rich_menu_id (str): The ID of the rich menu to be aliased.
            alias (str): The alias to be created.

        Returns:
            None
        """
        await self.line_bot_api.create_rich_menu_alias(
            CreateRichMenuAliasRequest(richMenuAliasId=alias, richMenuId=rich_menu_id)
        )

    async def update_rich_menu_alias(self, rich_menu_id: str, alias: str) -> None:
        """
        Updates the alias of the specified rich menu.

        Args:
            rich_menu_id (str): The ID of the rich menu to be aliased.
            alias (str): The alias to be created.

        Returns:
            None
        """
        await self.line_bot_api.update_rich_menu_alias(
            rich_menu_alias_id=alias,
            update_rich_menu_alias_request=UpdateRichMenuAliasRequest(
                richMenuId=rich_menu_id
            ),
        )

    async def delete_all_rich_menus(self) -> None:
        """
        Deletes all rich menus.

        Returns:
            None
        """
        rich_menus = await self.get_rich_menu_list()
        for rich_menu in rich_menus:
            await self.delete_rich_menu(rich_menu.rich_menu_id)

    async def delete_rich_menu(self, rich_menu_id: str) -> None:
        """
        Deletes the specified rich menu.

        Args:
            rich_menu_id (str): The ID of the rich menu to be deleted.

        Returns:
            None
        """
        await self.line_bot_api.delete_rich_menu(rich_menu_id=rich_menu_id)

    async def get_rich_menu_list(self) -> List[RichMenuResponse]:
        """
        Gets the list of rich menus.

        Returns:
            List[RichMenuResponse]: The list of rich menus.
        """
        return (await self.line_bot_api.get_rich_menu_list()).richmenus

    # user-defined methods

    async def setup_hook(self) -> None:
        pass

    async def on_close(self) -> None:
        pass

    async def run_tasks(self) -> None:
        pass

    # cog management

    def add_cog(self, path_or_class: pathOrClass) -> None:
        """
        Adds a cog to the bot.

        Args:
            path_or_class (Union[str, Type[Cog]]): The path to the cog or the cog class itself.

        Raises:
            CogLoadError: If the cog cannot be loaded.

        Returns:
            None
        """
        try:
            if isinstance(path_or_class, str):
                # cog path, example: bot.cogs.info
                module = importlib.import_module(path_or_class)
                # get all classes in the module that is subclass of Cog and not Cog itself
                classes = inspect.getmembers(module, inspect.isclass)
                classes = [
                    class_
                    for class_ in classes
                    if issubclass(class_[1], Cog) and class_[1] != Cog
                ]
                if not classes:
                    raise CogLoadError(path_or_class, "No Cog subclass found")
                if len(classes) > 1:
                    raise CogLoadError(path_or_class, "Multiple Cog subclasses found")
                cog_class = classes[0][1]
                self.cogs.append(cog_class(self))
            else:
                self.cogs.append(path_or_class(self))  # type: ignore
        except Exception as e:
            raise CogLoadError(path_or_class, e) from e

    # messaging api

    async def push_message(
        self,
        to: str,
        messages: Sequence[Message],
        *,
        notification_disabled: bool = False,
        custom_aggregation_units: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Sends a push message to a user or group.

        Args:
            to (str): The ID of the user or group to send the message to.
            messages (Sequence[Message]): A list of Message objects to send.
            notification_disabled (bool, optional): Whether to disable notification for the message. Defaults to False.
            custom_aggregation_units (Optional[Sequence[str]], optional): A list of aggregation units for the message. Defaults to None.

        Raises:
            ValueError: If the number of messages is greater than 5.

        Returns:
            None
        """
        if len(messages) > 5:
            raise ValueError("The number of messages must be less than or equal to 5")

        await self.line_bot_api.push_message(
            PushMessageRequest(
                to=to,
                messages=messages,
                notificationDisabled=notification_disabled,
                customAggregationUnits=custom_aggregation_units,
            )
        )

    # server

    async def run(
        self,
        *,
        port: int = 8000,
        custom_route: Optional[str] = None,
        log_to_stream: bool = True,
    ) -> None:
        """
        Runs the server on the specified port and sets up the necessary routes and hooks.

        Args:
            port (int): The port number to run the server on. Defaults to 8000.
            custom_route (Optional[str]): The custom route to use for handling commands. Defaults to "/line".
            log_to_stream (bool): Whether to log to stdout. Defaults to True.

        Returns:
            None
        """
        self._setup_logging(log_to_stream)
        await self.setup_hook()
        self.app.add_routes([web.post(custom_route or "/line", self._handle_request)])
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = TCPSite(runner=runner, port=port)
        await site.start()
        logging.info("Bot started at port %d", port)
        try:
            while True:
                asyncio.create_task(self.run_tasks())
                await asyncio.sleep(self.task_interval)
        except asyncio.CancelledError:
            logging.info("Bot shutting down")
            await self.on_close()
            await site.stop()
            await self.app.shutdown()
            await self.async_api_client.close()
            await runner.cleanup()


class Bot(BaseBot): ...


class Cog:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.commands: Dict[str, Callable[..., Awaitable[None]]] = {}
        self.__initialize_commands()

    def __initialize_commands(self) -> None:
        funcs = inspect.getmembers(self, inspect.ismethod)
        funcs = [func for func in funcs if getattr(func[1], "__is_command__", False)]
        self.commands = {func[0]: func[1] for func in funcs}
