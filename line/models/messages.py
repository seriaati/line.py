from __future__ import annotations

from typing import TYPE_CHECKING

from linebot.v3 import messaging

from ..utils import find_indexes

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .emoji import Emoji


class TextMessage(messaging.TextMessage):
    """https://developers.line.biz/en/reference/messaging-api/#text-message."""

    def __init__(
        self,
        text: str,
        *,
        quick_reply: messaging.QuickReply | None = None,
        emojis: Sequence[Emoji] | None = None,
        quote_token: str | None = None,
    ) -> None:
        if len(text) > 5000:
            msg = "text must be less than or equal to 5000 characters"
            raise ValueError(msg)

        line_emojis: Sequence[messaging.Emoji] | None = None
        if emojis:
            line_emojis = []
            indexes = find_indexes(text, "$")
            for i, emoji in enumerate(emojis):
                line_emojis.append(
                    messaging.Emoji(
                        index=indexes[i], productId=emoji.product_id, emojiId=emoji.emoji_id
                    )
                )

        super().__init__(
            text=text, quickReply=quick_reply, emojis=line_emojis, quoteToken=quote_token
        )


class TemplateMessage(messaging.TemplateMessage):
    """https://developers.line.biz/en/reference/messaging-api/#template-messages."""

    def __init__(
        self,
        alt_text: str,
        *,
        template: messaging.Template,
        quick_reply: messaging.QuickReply | None = None,
    ) -> None:
        if len(alt_text) > 400:
            msg = "altText must be less than or equal to 400 characters"
            raise ValueError(msg)

        super().__init__(altText=alt_text, template=template, quickReply=quick_reply)  # type: ignore


class ImageMessage(messaging.ImageMessage):
    """https://developers.line.biz/en/reference/messaging-api/#image-message."""

    def __init__(
        self,
        original_content_url: str,
        preview_image_url: str,
        *,
        quick_reply: messaging.QuickReply | None = None,
    ) -> None:
        if len(original_content_url) > 2000:
            msg = "originalContentUrl must be less than or equal to 2000 characters"
            raise ValueError(msg)
        if len(preview_image_url) > 2000:
            msg = "previewImageUrl must be less than or equal to 2000 characters"
            raise ValueError(msg)

        super().__init__(
            originalContentUrl=original_content_url,
            previewImageUrl=preview_image_url,
            quickReply=quick_reply,
        )
