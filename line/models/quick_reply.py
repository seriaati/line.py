from typing import List, Optional

import linebot.v3.messaging as messaging


class QuickReplyItem(messaging.QuickReplyItem):
    """
    https://developers.line.biz/en/reference/messaging-api/#quick-reply-button-object
    """

    def __init__(
        self, action: messaging.Action, *, image_url: Optional[str] = None
    ) -> None:
        if len(image_url or "") > 2000:
            raise ValueError("imageUrl must be less than or equal to 2000 characters")

        super().__init__(action=action, imageUrl=image_url, type="action")


class QuickReply(messaging.QuickReply):
    """
    https://developers.line.biz/en/reference/messaging-api/#quick-reply
    """

    def __init__(self, items: List[QuickReplyItem]) -> None:
        if len(items) > 13:
            raise ValueError("The number of items must be less than or equal to 13")

        super().__init__(items=items)
