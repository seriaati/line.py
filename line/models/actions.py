from __future__ import annotations

from typing import Literal

from linebot.v3 import messaging


class PostbackAction(messaging.PostbackAction):
    """https://developers.line.biz/en/reference/messaging-api/#postback-action."""

    def __init__(
        self,
        label: str,
        *,
        data: str,
        display_text: str | None = None,
        input_option: Literal["closeRichMenu", "openRichMenu", "openKeyboard", "openVoice"]
        | None = None,
        fill_in_text: str | None = None,
    ) -> None:
        if len(data) > 300:
            msg = "data must be less than or equal to 300 characters"
            raise ValueError(msg)
        if len(display_text or "") > 300:
            msg = "displayText must be less than or equal to 300 characters"
            raise ValueError(msg)
        if len(fill_in_text or "") > 300:
            msg = "fillInText must be less than or equal to 300 characters"
            raise ValueError(msg)
        if fill_in_text and input_option != "openKeyboard":
            msg = "fillInText can only be specified when inputOption is openKeyboard"
            raise ValueError(msg)

        super().__init__(
            data=data,
            label=label,
            displayText=display_text,
            inputOption=input_option,
            fillInText=fill_in_text,
        )


class MessageAction(messaging.MessageAction):
    """https://developers.line.biz/en/reference/messaging-api/#message-action."""

    def __init__(self, label: str, *, text: str) -> None:
        if len(text) > 300:
            msg = "text must be less than or equal to 300 characters"
            raise ValueError(msg)

        super().__init__(text=text, label=label)


class URIAction(messaging.URIAction):
    """https://developers.line.biz/en/reference/messaging-api/#uri-action."""

    def __init__(self, label: str, *, uri: str, desktop_alt_uri: str | None = None) -> None:
        if len(uri) > 1000:
            msg = "uri must be less than or equal to 1000 characters"
            raise ValueError(msg)
        if len(desktop_alt_uri or "") > 1000:
            msg = "desktopAltUri must be less than or equal to 1000 characters"
            raise ValueError(msg)

        super().__init__(uri=uri, label=label, altUri=messaging.AltUri(desktop=desktop_alt_uri))


class RichMenuSwitchAction(messaging.RichMenuSwitchAction):
    """https://developers.line.biz/en/reference/messaging-api/#richmenu-switch-action."""

    def __init__(self, rich_menu_alias_id: str, *, data: str, label: str | None = None) -> None:
        if len(label or "") > 20:
            msg = "label must be less than or equal to 20 characters"
            raise ValueError(msg)
        if len(data) > 300:
            msg = "data must be less than or equal to 300 characters"
            raise ValueError(msg)
        super().__init__(data=data, label=label, richMenuAliasId=rich_menu_alias_id)
