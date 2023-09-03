from typing import List, Optional

import linebot.v3.messaging as messaging

from ..utils import find_indexes
from .emoji import Emoji


class TextMessage(messaging.TextMessage):
    def __init__(
        self,
        text: str,
        *,
        quick_reply: Optional[messaging.QuickReply] = None,
        emojis: Optional[List[Emoji]] = None,
    ) -> None:
        line_emojis: Optional[List[messaging.Emoji]] = None
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
    def __init__(
        self,
        alt_text: str,
        template: messaging.Template,
        *,
        quick_reply: Optional[messaging.QuickReply] = None,
    ) -> None:
        super().__init__(altText=alt_text, template=template, quickReply=quick_reply)  # type: ignore


class ImageMessage(messaging.ImageMessage):
    def __init__(
        self,
        original_content_url: str,
        preview_image_url: str,
        *,
        quick_reply: Optional[messaging.QuickReply] = None,
    ) -> None:
        super().__init__(
            originalContentUrl=original_content_url,
            previewImageUrl=preview_image_url,
            quickReply=quick_reply,
        )
