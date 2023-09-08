from typing import Literal, Optional

from linebot.v3 import messaging as messaging


class PostbackAction(messaging.PostbackAction):
    """
    https://developers.line.biz/en/reference/messaging-api/#postback-action
    """

    def __init__(
        self,
        label: str,
        *,
        data: str,
        display_text: Optional[str] = None,
        input_option: Optional[
            Literal["closeRichMenu", "openRichMenu", "openKeyboard", "openVoice"]
        ] = None,
        fill_in_text: Optional[str] = None,
    ) -> None:
        if len(data) > 300:
            raise ValueError("data must be less than or equal to 300 characters")
        if len(display_text or "") > 300:
            raise ValueError("displayText must be less than or equal to 300 characters")
        if len(fill_in_text or "") > 300:
            raise ValueError("fillInText must be less than or equal to 300 characters")
        if fill_in_text and input_option != "openKeyboard":
            raise ValueError(
                "fillInText can only be specified when inputOption is openKeyboard"
            )

        super().__init__(
            data=data,
            label=label,
            displayText=display_text,
            inputOption=input_option,
            fillInText=fill_in_text,
        )


class MessageAction(messaging.MessageAction):
    """
    https://developers.line.biz/en/reference/messaging-api/#message-action
    """

    def __init__(self, label: str, *, text: str) -> None:
        if len(text) > 300:
            raise ValueError("text must be less than or equal to 300 characters")

        super().__init__(text=text, label=label)


class URIAction(messaging.URIAction):
    """
    https://developers.line.biz/en/reference/messaging-api/#uri-action
    """

    def __init__(
        self, label: str, *, uri: str, desktop_alt_uri: Optional[str] = None
    ) -> None:
        if len(uri) > 1000:
            raise ValueError("uri must be less than or equal to 1000 characters")
        if len(desktop_alt_uri or "") > 1000:
            raise ValueError(
                "desktopAltUri must be less than or equal to 1000 characters"
            )

        super().__init__(
            uri=uri, label=label, altUri=messaging.AltUri(desktop=desktop_alt_uri)
        )
