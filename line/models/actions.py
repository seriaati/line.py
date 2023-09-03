from typing import Literal, Optional

from linebot.v3 import messaging as messaging


class PostbackAction(messaging.PostbackAction):
    def __init__(
        self,
        data: str,
        label: str,
        *,
        display_text: Optional[str] = None,
        input_option: Optional[
            Literal["closeRichMenu", "openRichMenu", "openKeyboard", "openVoice"]
        ] = None,
        fill_in_text: Optional[str] = None,
    ) -> None:
        if fill_in_text and input_option != "openKeyboard":
            raise ValueError(
                "fill_in_text can only be specified when input_option is openKeyboard"
            )
        super().__init__(
            data=data,
            label=label,
            displayText=display_text,
            inputOption=input_option,
            fillInText=fill_in_text,
        )


class MessageAction(messaging.MessageAction):
    def __init__(self, text: str, label: str) -> None:
        super().__init__(text=text, label=label)


class URIAction(messaging.URIAction):
    def __init__(
        self, uri: str, label: str, *, desktop_alt_uri: Optional[str] = None
    ) -> None:
        super().__init__(
            uri=uri, label=label, altUri=messaging.AltUri(desktop=desktop_alt_uri)
        )
