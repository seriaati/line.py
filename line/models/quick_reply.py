from __future__ import annotations

from typing import TYPE_CHECKING

from linebot.v3 import messaging

if TYPE_CHECKING:
    from collections.abc import Sequence


class QuickReplyItem(messaging.QuickReplyItem):
    """https://developers.line.biz/en/reference/messaging-api/#quick-reply-button-object."""

    def __init__(self, action: messaging.Action, *, image_url: str | None = None) -> None:
        if len(image_url or "") > 2000:
            msg = "imageUrl must be less than or equal to 2000 characters"
            raise ValueError(msg)

        super().__init__(action=action, imageUrl=image_url, type="action")


class QuickReply(messaging.QuickReply):
    """https://developers.line.biz/en/reference/messaging-api/#quick-reply."""

    def __init__(self, items: Sequence[QuickReplyItem]) -> None:
        if len(items) > 13:
            msg = "The number of items must be less than or equal to 13"
            raise ValueError(msg)

        super().__init__(items=items)
