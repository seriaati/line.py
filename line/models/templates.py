from typing import List, Literal, Optional

from linebot.v3 import messaging as messaging


class CarouselColumn(messaging.CarouselColumn):
    """
    https://developers.line.biz/en/reference/messaging-api/#column-object-for-carousel
    """

    def __init__(
        self,
        text: str,
        actions: List[messaging.Action],
        *,
        title: Optional[str] = None,
        default_action: Optional[messaging.Action] = None,
        thumbnail_image_url: Optional[str] = None,
        image_background_color: Optional[str] = None,
    ) -> None:
        if (title or thumbnail_image_url) and len(text) > 60:
            raise ValueError("The length of text must be less than or equal to 60")
        elif len(text) > 120:
            raise ValueError("The length of text must be less than or equal to 120")
        if len(actions) > 3:
            raise ValueError("The number of actions must be less than or equal to 3")
        if len(title or "") > 40:
            raise ValueError("The length of title must be less than or equal to 40")
        if len(thumbnail_image_url or "") > 2000:
            raise ValueError(
                "The length of thumbnailImageUrl must be less than or equal to 2000"
            )

        super().__init__(
            text=text,
            actions=actions,
            title=title,
            thumbnailImageUrl=thumbnail_image_url,
            imageBackgroundColor=image_background_color,
            defaultAction=default_action,
        )


class CarouselTemplate(messaging.CarouselTemplate):
    """
    https://developers.line.biz/en/reference/messaging-api/#carousel
    """

    def __init__(
        self,
        columns: List[CarouselColumn],
        *,
        image_aspect_raio: Literal["rectangle", "square"] = "rectangle",
        image_size: Literal["cover", "contain"] = "cover",
    ) -> None:
        if len(columns) > 10:
            raise ValueError("The number of columns must be less than or equal to 10")

        super().__init__(
            columns=columns, imageAspectRatio=image_aspect_raio, imageSize=image_size
        )


class ConfirmTemplate(messaging.ConfirmTemplate):
    """
    https://developers.line.biz/en/reference/messaging-api/#confirm
    """

    def __init__(
        self,
        text: str,
        actions: List[messaging.Action],
    ) -> None:
        if len(text) > 240:
            raise ValueError("The length of text must be less than or equal to 240")
        if len(actions) > 2:
            raise ValueError("The number of actions must be less than or equal to 2")

        super().__init__(
            text=text,
            actions=actions,
        )


class ButtonsTemplate(messaging.ButtonsTemplate):
    """
    https://developers.line.biz/en/reference/messaging-api/#buttons
    """

    def __init__(
        self,
        text: str,
        actions: List[messaging.Action],
        *,
        title: Optional[str] = None,
        thumbnail_image_url: Optional[str] = None,
        image_aspect_raio: Literal["rectangle", "square"] = "rectangle",
        image_size: Literal["cover", "contain"] = "cover",
        image_background_color: str = "#FFFFFF",
        default_action: Optional[messaging.Action] = None,
    ) -> None:
        if len(actions) > 4:
            raise ValueError("The number of actions must be less than or equal to 4")
        if (title or thumbnail_image_url) and len(text) > 60:
            raise ValueError("The length of text must be less than or equal to 60")
        elif len(text) > 160:
            raise ValueError("The length of text must be less than or equal to 160")
        if len(title or "") > 40:
            raise ValueError("The length of title must be less than or equal to 40")
        if len(thumbnail_image_url or "") > 2000:
            raise ValueError(
                "The length of thumbnailImageUrl must be less than or equal to 2000"
            )

        super().__init__(
            text=text,
            actions=actions,
            thumbnailImageUrl=thumbnail_image_url,
            imageAspectRatio=image_aspect_raio,
            imageSize=image_size,
            imageBackgroundColor=image_background_color,
            title=title,
            defaultAction=default_action,
        )
