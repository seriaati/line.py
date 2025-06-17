from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from linebot.v3 import messaging

if TYPE_CHECKING:
    from collections.abc import Sequence


class CarouselColumn(messaging.CarouselColumn):
    """https://developers.line.biz/en/reference/messaging-api/#column-object-for-carousel."""

    def __init__(
        self,
        text: str,
        actions: Sequence[messaging.Action],
        *,
        title: str | None = None,
        default_action: messaging.Action | None = None,
        thumbnail_image_url: str | None = None,
        image_background_color: str | None = None,
    ) -> None:
        if (title or thumbnail_image_url) and len(text) > 60:
            msg = "The length of text must be less than or equal to 60"
            raise ValueError(msg)
        if len(text) > 120:
            msg = "The length of text must be less than or equal to 120"
            raise ValueError(msg)
        if len(actions) > 3:
            msg = "The number of actions must be less than or equal to 3"
            raise ValueError(msg)
        if len(title or "") > 40:
            msg = "The length of title must be less than or equal to 40"
            raise ValueError(msg)
        if len(thumbnail_image_url or "") > 2000:
            msg = "The length of thumbnailImageUrl must be less than or equal to 2000"
            raise ValueError(msg)

        super().__init__(
            text=text,
            actions=actions,
            title=title,
            thumbnailImageUrl=thumbnail_image_url,
            imageBackgroundColor=image_background_color,
            defaultAction=default_action,
        )


class CarouselTemplate(messaging.CarouselTemplate):
    """https://developers.line.biz/en/reference/messaging-api/#carousel."""

    def __init__(
        self,
        columns: Sequence[CarouselColumn],
        *,
        image_aspect_raio: Literal["rectangle", "square"] = "rectangle",
        image_size: Literal["cover", "contain"] = "cover",
    ) -> None:
        if len(columns) > 10:
            msg = "The number of columns must be less than or equal to 10"
            raise ValueError(msg)

        super().__init__(columns=columns, imageAspectRatio=image_aspect_raio, imageSize=image_size)


class ConfirmTemplate(messaging.ConfirmTemplate):
    """https://developers.line.biz/en/reference/messaging-api/#confirm."""

    def __init__(self, text: str, actions: Sequence[messaging.Action]) -> None:
        if len(text) > 240:
            msg = "The length of text must be less than or equal to 240"
            raise ValueError(msg)
        if len(actions) > 2:
            msg = "The number of actions must be less than or equal to 2"
            raise ValueError(msg)

        super().__init__(text=text, actions=actions)


class ButtonsTemplate(messaging.ButtonsTemplate):
    """https://developers.line.biz/en/reference/messaging-api/#buttons."""

    def __init__(
        self,
        text: str,
        actions: Sequence[messaging.Action],
        *,
        title: str | None = None,
        thumbnail_image_url: str | None = None,
        image_aspect_raio: Literal["rectangle", "square"] = "rectangle",
        image_size: Literal["cover", "contain"] = "cover",
        image_background_color: str = "#FFFFFF",
        default_action: messaging.Action | None = None,
    ) -> None:
        if len(actions) > 4:
            msg = "The number of actions must be less than or equal to 4"
            raise ValueError(msg)
        if (title or thumbnail_image_url) and len(text) > 60:
            msg = "The length of text must be less than or equal to 60"
            raise ValueError(msg)
        if len(text) > 160:
            msg = "The length of text must be less than or equal to 160"
            raise ValueError(msg)
        if len(title or "") > 40:
            msg = "The length of title must be less than or equal to 40"
            raise ValueError(msg)
        if len(thumbnail_image_url or "") > 2000:
            msg = "The length of thumbnailImageUrl must be less than or equal to 2000"
            raise ValueError(msg)

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


class ImageCarouselColumn(messaging.ImageCarouselColumn):
    def __init__(self, image_url: str, action: messaging.Action) -> None:
        if len(image_url) > 2000:
            msg = "The length of image_url must be less than or equal to 2000"
            raise ValueError(msg)

        super().__init__(imageUrl=image_url, action=action)


class ImageCarouselTemplate(messaging.ImageCarouselTemplate):
    def __init__(self, columns: Sequence[ImageCarouselColumn]) -> None:
        if len(columns) > 10:
            msg = "The number of columns must be less than or equal to 10"
            raise ValueError(msg)

        super().__init__(columns=columns)
