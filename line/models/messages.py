from typing import Optional

import linebot.v3.messaging as messaging


class TextMessage(messaging.TextMessage):
    def __init__(
        self, text: str, *, quick_reply: Optional[messaging.QuickReply] = None
    ) -> None:
        super().__init__(text=text, quickReply=quick_reply)  # type: ignore


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
