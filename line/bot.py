from __future__ import annotations

import asyncio
import importlib
import inspect
import logging
from enum import IntEnum
from types import UnionType
from typing import TYPE_CHECKING, Any, TypeVar, Union, get_args, get_origin

import aiofiles
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
from linebot.v3.webhooks import FollowEvent, MessageEvent, PostbackEvent, UnfollowEvent

from .context import Context
from .exceptions import (
    CogLoadError,
    CommandExecError,
    FloatConvertError,
    IntConvertError,
    ParamParseError,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from linebot.v3.webhooks.models.source import Source

PathOrClass = TypeVar("PathOrClass", str, type["Cog"])
LOGGER = logging.getLogger(__name__)


class ParamType(IntEnum):
    INTEGER = 1
    FLOAT = 2
    STRING = 3
    BOOLEAN = 4
    UNKNOWN = 5


class BaseBot:
    def __init__(self, *, channel_secret: str, access_token: str) -> None:
        configuration = Configuration(access_token=access_token)

        self.async_api_client = AsyncApiClient(configuration)
        self.line_bot_api = AsyncMessagingApi(self.async_api_client)
        self.blob_api = AsyncMessagingApiBlob(self.async_api_client)
        self.webhook_parser = WebhookParser(channel_secret)

        self.cogs: list[Cog] = []
        self.app = web.Application()
        self.session = self.async_api_client.rest_client.pool_manager
        self.task_interval = 60
        self.task: asyncio.Task | None = None

    @staticmethod
    def _setup_logging(log_to_stream: bool) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler("bot.log", encoding="utf-8"), logging.StreamHandler()],
        )
        if not log_to_stream:
            logging.getLogger().removeHandler(logging.StreamHandler())

    @staticmethod
    def _parse_data(param_string: str) -> dict[str, str | None]:
        """Parses a string of parameters into a dictionary.

        Args:
            param_string: The string of parameters.

        Returns:
            The dictionary of parameters.
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
    def __get_param_type(annotation: Any) -> ParamType:
        # Check if it's an Optional or Union with None
        origin = get_origin(annotation)
        args = get_args(annotation)

        is_optional = False

        if (origin is Union or origin is UnionType) and type(None) in args:
            is_optional = True

        if is_optional:
            annotation = next((arg for arg in args if arg is not type(None)), None)

        # Now check the base type
        if annotation == "int":
            return ParamType.INTEGER
        if annotation == "bool":
            return ParamType.BOOLEAN
        if annotation == "float":
            return ParamType.FLOAT
        if annotation == "str":
            return ParamType.STRING
        return ParamType.UNKNOWN

    @staticmethod
    def _parse_params(
        params: dict[str, inspect.Parameter],
        data: dict[str, str | None],
        annotations: dict[str, Any],
    ) -> tuple[Sequence[Any], dict[str, Any]]:
        args: Sequence[Any] = []
        kwargs: dict[str, Any] = {}

        for param in list(params.values())[2:]:
            default = None if param.default == inspect.Parameter.empty else param.default
            value = data.get(param.name, default)

            if value is not None:
                param_type = BaseBot.__get_param_type(annotations[param.name])

                if param_type is ParamType.INTEGER:
                    if not value.isdigit():
                        raise IntConvertError(param.name, value)
                    value = int(value)
                elif param_type is ParamType.FLOAT:
                    try:
                        value = float(value)
                    except ValueError as e:
                        raise FloatConvertError(param.name, value) from e
                elif param_type is ParamType.BOOLEAN:
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False

            if param.kind in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }:
                kwargs[param.name] = value
            else:
                args.append(value)

        return args, kwargs

    async def _handle_request(self, request: web.Request) -> web.Response:
        try:
            signature = request.headers["X-Line-Signature"]
            body = await request.text()

            try:
                events: list[Event] = self.webhook_parser.parse(body, signature)  # type: ignore
            except InvalidSignatureError:
                LOGGER.exception("Invalid signature")
                return web.Response(status=400, text="Invalid signature")

            for event in events:
                if isinstance(event, PostbackEvent):
                    await self.on_postback(event)
                elif isinstance(event, MessageEvent):
                    await self.on_message(event)
                elif isinstance(event, FollowEvent):
                    await self.on_follow(event)
                elif isinstance(event, UnfollowEvent):
                    await self.on_unfollow(event)
                else:
                    LOGGER.error("Event type %s is not supported", type(event))
                    continue
        except Exception as e:
            await self.on_error(e)
            return web.Response(text="Internal server error", status=500)
        else:
            return web.Response(text="OK", status=200)

    # event handlers

    async def on_postback(self, event: PostbackEvent) -> None:
        """Handles a postback event.

        Args:
            event: The postback event.

        Raises:
            ValueError: If the event source is None.
        """
        if event.source is None:
            msg = "Event source is None"
            raise ValueError(msg)

        await self.process_command(
            event.postback.data,
            event.source,
            event.reply_token,  # type: ignore
        )

    async def on_message(self, event: MessageEvent) -> None:
        """Handles a message event.

        Args:
            event: The message event.

        Raises:
            ValueError: If the event source is None.
        """
        if event.source is None:
            msg = "Event source is None"
            raise ValueError(msg)

        await self.process_command(
            event.message.text,  # type: ignore
            event.source,
            event.reply_token,  # type: ignore
        )

    async def on_follow(self, event: FollowEvent) -> None:
        """Handles a follow event.

        Args:
            event: The follow event.
        """

    async def on_unfollow(self, event: UnfollowEvent) -> None:
        """Handles an unfollow event.

        Args:
            event: The unfollow event.
        """

    async def on_error(self, error: Exception) -> None:
        """Handles an error.

        Args:
            error: The error that occurred.
        """
        LOGGER.error(error)

    # command processing

    async def process_command(self, text: str, source: Source, reply_token: str) -> Any:
        """Processes a command from the user.

        Args:
            text: The text of the command.
            source: The source of the command.
            reply_token: The reply token for the command.

        Raises:
            CommandExecError: If an error occurs while executing the command.
            ParamParseError: If an error occurs while parsing the parameters of the command.

        Returns:
            The result of the command.
        """
        data = self._parse_data(text)
        ctx = Context(
            user_id=source.user_id,  # type: ignore
            api=self.line_bot_api,
            reply_token=reply_token,
            group_id=getattr(source, "group_id", None),
            room_id=getattr(source, "room_id", None),
        )

        cmd = data.get("cmd")
        if not cmd:
            return None

        for cog in self.cogs:
            func = cog.commands.get(cmd)
            if func:
                sig = inspect.signature(func.original_function)  # pyright: ignore[reportFunctionMemberAccess]
                params = sig.parameters
                try:
                    args, kwargs = self._parse_params(
                        dict(params),
                        data,
                        func.original_function.__annotations__,  # pyright: ignore[reportFunctionMemberAccess]
                    )
                except Exception as e:
                    raise ParamParseError(cmd, e) from e

                try:
                    await func(ctx, *args, **kwargs)
                except Exception as e:
                    raise CommandExecError(cmd, e) from e

                break

    # rich menu

    async def create_rich_menu(
        self, request: RichMenuRequest, image_path: str, *, alias: str | None = None
    ) -> str:
        """Creates a new rich menu with the specified request and image, and returns the ID of the created rich menu.

        Args:
            request: The request object containing the details of the rich menu to be created.
            image_path: The file path of the image to be used as the rich menu image.
            alias: The alias to be created for the rich menu.

        Returns:
            The ID of the created rich menu.
        """
        result = await self.line_bot_api.create_rich_menu(request)
        async with aiofiles.open(image_path, "rb") as f:
            await self.blob_api.set_rich_menu_image(
                result.rich_menu_id, body=await f.read(), _headers={"Content-Type": "image/png"}
            )

        if alias:
            try:
                await self.create_rich_menu_alias(result.rich_menu_id, alias)
            except ApiException as e:
                if e.status == 400:
                    await self.update_rich_menu_alias(result.rich_menu_id, alias)
        return result.rich_menu_id

    async def link_rich_menu_to_users(self, rich_menu_id: str, user_ids: list[str]) -> None:
        """Links the specified rich menu to the specified users.

        Args:
            rich_menu_id: The ID of the rich menu to be linked.
            user_ids: The list of user IDs to be linked to the rich menu.
        """
        await self.line_bot_api.link_rich_menu_id_to_users(
            RichMenuBulkLinkRequest(richMenuId=rich_menu_id, userIds=user_ids)
        )

    async def create_rich_menu_alias(self, rich_menu_id: str, alias: str) -> None:
        """Creates an alias for the specified rich menu.

        Args:
            rich_menu_id: The ID of the rich menu to be aliased.
            alias: The alias to be created.
        """
        await self.line_bot_api.create_rich_menu_alias(
            CreateRichMenuAliasRequest(richMenuAliasId=alias, richMenuId=rich_menu_id)
        )

    async def update_rich_menu_alias(self, rich_menu_id: str, alias: str) -> None:
        """Updates the alias of the specified rich menu.

        Args:
            rich_menu_id: The ID of the rich menu to be aliased.
            alias: The alias to be created.
        """
        await self.line_bot_api.update_rich_menu_alias(
            rich_menu_alias_id=alias,
            update_rich_menu_alias_request=UpdateRichMenuAliasRequest(richMenuId=rich_menu_id),
        )

    async def delete_all_rich_menus(self) -> None:
        """Deletes all rich menus."""
        rich_menus = await self.get_rich_menu_list()
        for rich_menu in rich_menus:
            await self.delete_rich_menu(rich_menu.rich_menu_id)

    async def delete_rich_menu(self, rich_menu_id: str) -> None:
        """Deletes the specified rich menu.

        Args:
            rich_menu_id: The ID of the rich menu to be deleted.
        """
        await self.line_bot_api.delete_rich_menu(rich_menu_id=rich_menu_id)

    async def get_rich_menu_list(self) -> list[RichMenuResponse]:
        """Gets the list of rich menus.

        Returns:
            A list of rich menus.
        """
        return (await self.line_bot_api.get_rich_menu_list()).richmenus

    # user-defined methods

    async def setup_hook(self) -> None:
        """This method is ran before the server starts."""

    async def on_close(self) -> None:
        """This method is ran before the server shuts down."""

    async def run_tasks(self) -> None:
        """This method is ran every task_interval seconds."""

    # cog management

    def add_cog(self, path_or_class: PathOrClass) -> None:
        """Adds a cog to the bot.

        Args:
            path_or_class: The path to the cog or the cog class itself.

        Raises:
            CogLoadError: If the cog cannot be loaded.
        """
        try:
            if isinstance(path_or_class, str):
                # cog path, example: bot.cogs.info
                module = importlib.import_module(path_or_class)
                # get all classes in the module that is subclass of Cog and not Cog itself
                classes = inspect.getmembers(module, inspect.isclass)
                classes = [
                    class_ for class_ in classes if issubclass(class_[1], Cog) and class_[1] != Cog
                ]
                if not classes:
                    raise CogLoadError(path_or_class, "No Cog subclass found")  # noqa: TRY301
                if len(classes) > 1:
                    raise CogLoadError(path_or_class, "Multiple Cog subclasses found")  # noqa: TRY301
                cog_class = classes[0][1]
                self.cogs.append(cog_class(self))
            else:
                self.cogs.append(path_or_class(self))  # type: ignore
        except CogLoadError:
            raise
        except Exception as e:
            raise CogLoadError(path_or_class, e) from e

    # messaging api

    async def push_message(
        self,
        to: str,
        messages: Sequence[Message],
        *,
        notification_disabled: bool = False,
        custom_aggregation_units: Sequence[str] | None = None,
    ) -> None:
        """Sends a push message to a user or group.

        Args:
            to (str): The ID of the user or group to send the message to.
            messages (Sequence[Message]): A list of Message objects to send.
            notification_disabled (bool, optional): Whether to disable notification for the message. Defaults to False.
            custom_aggregation_units (Optional[Sequence[str]], optional): A list of aggregation units for the message. Defaults to None.

        Raises:
            ValueError: If the number of messages is greater than 5.
        """
        if len(messages) > 5:
            msg = "The number of messages must be less than or equal to 5"
            raise ValueError(msg)

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
        self, *, port: int = 8000, custom_route: str | None = None, log_to_stream: bool = True
    ) -> None:
        """Runs the server on the specified port and sets up the necessary routes and hooks.

        Args:
            port (int): The port number to run the server on. Defaults to 8000.
            custom_route (Optional[str]): The custom route to use for handling commands. Defaults to "/line".
            log_to_stream (bool): Whether to log to stdout. Defaults to True.
        """
        self._setup_logging(log_to_stream)
        await self.setup_hook()
        self.app.add_routes([web.post(custom_route or "/line", self._handle_request)])
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = TCPSite(runner=runner, port=port)
        await site.start()
        LOGGER.info("Bot started at port %d", port)
        try:
            while True:
                self.task = asyncio.create_task(self.run_tasks())
                await asyncio.sleep(self.task_interval)
        except asyncio.CancelledError:
            LOGGER.info("Bot shutting down")

            if self.task is not None:
                self.task.cancel()

            await self.on_close()
            await site.stop()
            await self.app.shutdown()
            await self.async_api_client.close()
            await runner.cleanup()


class Bot(BaseBot): ...


class Cog:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.commands: dict[str, Callable[..., Awaitable[None]]] = {}
        self.__initialize_commands()

    def __initialize_commands(self) -> None:
        funcs = inspect.getmembers(self, inspect.ismethod)
        funcs = [func for func in funcs if getattr(func[1], "__is_command__", False)]
        self.commands = {func[0]: func[1] for func in funcs}
