from typing import Optional, Sequence

from linebot.v3.messaging import (
    AsyncMessagingApi,
    Message,
    QuickReply,
    ReplyMessageRequest,
    Template,
)

from .models.messages import Emoji, ImageMessage, TemplateMessage, TextMessage


class Context:
    def __init__(
        self, *, user_id: str, api: AsyncMessagingApi, reply_token: Optional[str] = None
    ) -> None:
        self.user_id = user_id
        self.api = api
        self.reply_token = reply_token

    async def reply_text(
        self,
        text: str,
        *,
        quick_reply: Optional[QuickReply] = None,
        notification_disabled: bool = False,
        emojis: Optional[Sequence[Emoji]] = None,
    ) -> None:
        if self.reply_token is None:
            raise ValueError("reply_token must be provided")
        await self.api.reply_message(
            ReplyMessageRequest(
                replyToken=self.reply_token,
                messages=[
                    TextMessage(text=text, quick_reply=quick_reply, emojis=emojis)
                ],
                notificationDisabled=notification_disabled,
            )
        )

    async def reply_template(
        self,
        alt_text: str,
        *,
        template: Template,
        quick_reply: Optional[QuickReply] = None,
        notification_disabled: bool = False,
    ) -> None:
        if self.reply_token is None:
            raise ValueError("reply_token must be provided")
        await self.api.reply_message(
            ReplyMessageRequest(
                replyToken=self.reply_token,
                messages=[
                    TemplateMessage(
                        alt_text=alt_text,
                        template=template,
                        quick_reply=quick_reply,
                    )
                ],
                notificationDisabled=notification_disabled,
            )
        )

    async def reply_multiple(
        self, messages: Sequence[Message], *, notification_disabled: bool = False
    ) -> None:
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
        preview_image_url: Optional[str] = None,
        quick_reply: Optional[QuickReply] = None,
        notification_disabled: bool = False,
    ) -> None:
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
