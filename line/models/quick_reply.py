from typing import List, Optional

import linebot.v3.messaging as messaging


class QuickReplyItem(messaging.QuickReplyItem):
    def __init__(
        self, action: messaging.Action, *, imge_url: Optional[str] = None
    ) -> None:
        super().__init__(action=action, imageUrl=imge_url, type="action")


class QuickReply(messaging.QuickReply):
    def __init__(self, items: List[QuickReplyItem]) -> None:
        if len(items) > 13:
            raise ValueError("The number of items must be less than or equal to 13")
        super().__init__(items=items)
