from typing import Optional, Sequence

from linebot.v3 import messaging

from ..utils import find_indexes
from .emoji import Emoji


class TextMessage(messaging.TextMessage):
    """
    https://developers.line.biz/en/reference/messaging-api/#text-message
    """

    def __init__(
        self,
        text: str,
        *,
        quick_reply: Optional[messaging.QuickReply] = None,
        emojis: Optional[Sequence[Emoji]] = None,
    ) -> None:
        if len(text) > 5000:
            raise ValueError("text must be less than or equal to 5000 characters")

        line_emojis: Optional[Sequence[messaging.Emoji]] = None
        if emojis:
            line_emojis = []
            indexes = find_indexes(text, "$")
            for i, emoji in enumerate(emojis):
                line_emojis.append(
                    messaging.Emoji(
                        index=indexes[i],
                        productId=emoji.product_id,
                        emojiId=emoji.emoji_id,
                    )
                )

        super().__init__(text=text, quickReply=quick_reply, emojis=line_emojis)


class TemplateMessage(messaging.TemplateMessage):
    """
    https://developers.line.biz/en/reference/messaging-api/#template-messages
    """

    def __init__(
        self,
        alt_text: str,
        *,
        template: messaging.Template,
        quick_reply: Optional[messaging.QuickReply] = None,
    ) -> None:
        if len(alt_text) > 400:
            raise ValueError("altText must be less than or equal to 400 characters")

        super().__init__(altText=alt_text, template=template, quickReply=quick_reply)  # type: ignore


class ImageMessage(messaging.ImageMessage):
    """
    https://developers.line.biz/en/reference/messaging-api/#image-message
    """

    def __init__(
        self,
        original_content_url: str,
        preview_image_url: str,
        *,
        quick_reply: Optional[messaging.QuickReply] = None,
    ) -> None:
        if len(original_content_url) > 2000:
            raise ValueError(
                "originalContentUrl must be less than or equal to 2000 characters"
            )
        if len(preview_image_url) > 2000:
            raise ValueError(
                "previewImageUrl must be less than or equal to 2000 characters"
            )

        super().__init__(
            originalContentUrl=original_content_url,
            previewImageUrl=preview_image_url,
            quickReply=quick_reply,
        )
