from __future__ import annotations

from typing import TYPE_CHECKING

from linebot.v3.messaging import (
    AsyncMessagingApi,
    Message,
    QuickReply,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest,
    Template,
)

from .models.messages import ImageMessage, TemplateMessage, TextMessage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .models.emoji import Emoji


class Context:
    def __init__(
        self, *, user_id: str, api: AsyncMessagingApi, reply_token: str | None = None
    ) -> None:
        self.user_id = user_id
        self.api = api
        self.reply_token = reply_token

    async def defer(self, duration: int = 5) -> None:
        """Shows a loading animation for the specified duration.

        Args:
            duration: The duration of the loading animation in seconds.

        Raises:
            ValueError: If the duration is not between 5 and 60 seconds.
        """
        if 5 <= duration <= 60:
            await self.api.show_loading_animation(
                ShowLoadingAnimationRequest(chatId=self.user_id, loadingSeconds=duration)
            )
        else:
            msg = "Duration must be between 5 and 60 seconds."
            raise ValueError(msg)

    async def reply_text(
        self,
        text: str,
        *,
        quick_reply: QuickReply | None = None,
        notification_disabled: bool = False,
        emojis: Sequence[Emoji] | None = None,
    ) -> None:
        """Replies with a text message.

        Args:
            text: The text to send.
            quick_reply: The quick reply to send with the message.
            notification_disabled: Whether to disable notification for the message.
            emojis: The emojis to send with the message.

        Raises:
            ValueError: If the reply token is not provided.
        """
        if self.reply_token is None:
            raise ValueError("reply_token must be provided")

        await self.api.reply_message(
            ReplyMessageRequest(
                replyToken=self.reply_token,
                messages=[TextMessage(text=text, quick_reply=quick_reply, emojis=emojis)],
                notificationDisabled=notification_disabled,
            )
        )

    async def reply_template(
        self,
        alt_text: str,
        *,
        template: Template,
        quick_reply: QuickReply | None = None,
        notification_disabled: bool = False,
    ) -> None:
        """Replies with a template message.

        Args:
            alt_text: The alternative text to display if the client does not support the template message.
            template: The template to send.
            quick_reply: The quick reply to send with the message.
            notification_disabled: Whether to disable notification for the message.

        Raises:
            ValueError: If the reply token is not provided.
        """
        if self.reply_token is None:
            raise ValueError("reply_token must be provided")

        await self.api.reply_message(
            ReplyMessageRequest(
                replyToken=self.reply_token,
                messages=[
                    TemplateMessage(alt_text=alt_text, template=template, quick_reply=quick_reply)
                ],
                notificationDisabled=notification_disabled,
            )
        )

    async def reply_multiple(
        self, messages: Sequence[Message], *, notification_disabled: bool = False
    ) -> None:
        """Replies with multiple messages.

        Args:
            messages: The messages to send.
            notification_disabled: Whether to disable notification for the message.

        Raises:
            ValueError: If the reply token is not provided.
        """
        if self.reply_token is None:
            raise ValueError("reply_token must be provided")

        await self.api.reply_message(
            ReplyMessageRequest(
                replyToken=self.reply_token,
                messages=messages,
                notificationDisabled=notification_disabled,
            )
        )

    async def reply_image(
        self,
        image_url: str,
        *,
        preview_image_url: str | None = None,
        quick_reply: QuickReply | None = None,
        notification_disabled: bool = False,
    ) -> None:
        """Replies with an image message.

        Args:
            image_url: The URL of the image.
            preview_image_url: The URL of the preview image.
            quick_reply: The quick reply to send with the message.
            notification_disabled: Whether to disable notification for the message.

        Raises:
            ValueError: If the reply token is not provided.
        """
        if self.reply_token is None:
            raise ValueError("reply_token must be provided")

        await self.api.reply_message(
            ReplyMessageRequest(
                replyToken=self.reply_token,
                messages=[
                    ImageMessage(
                        original_content_url=image_url,
                        preview_image_url=preview_image_url or image_url,
                        quick_reply=quick_reply,
                    )
                ],
                notificationDisabled=notification_disabled,
            )
        )
