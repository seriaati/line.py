from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Emoji:
    """https://developers.line.biz/en/docs/messaging-api/emoji-list/#line-emoji-definitions."""

    product_id: str
    emoji_id: str
