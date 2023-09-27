from typing import Optional

import aiohttp


class LineNotifyAPI:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._session = session

    def get_oauth_uri(self, state: str) -> str:
        """
        Returns the OAuth URI for the LINE Notify client.

        Args:
            state (str): A string that will be returned in the response to the redirect URI.

        Returns:
            str: The OAuth URI for the LINE Notify client.
        """
        base_uri = "https://notify-bot.line.me/oauth/authorize"
        return f"{base_uri}?response_type=code&scope=notify&client_id={self.__client_id}&redirect_uri={self._redirect_uri}&state={state}&response_mode=form_post"

    async def get_access_token(self, code: str) -> str:
        """
        Retrieves an OAuth token from the LINE Notify API using the provided authorization code.

        Args:
            code (str): The authorization code to use for retrieving the OAuth token.

        Returns:
            str: The access token retrieved from the LINE Notify API.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
        }
        session = self._session or aiohttp.ClientSession()
        async with session.post(
            "https://notify-bot.line.me/oauth/token", data=data
        ) as resp:
            access_token = (await resp.json())["access_token"]

        if self._session is None:
            await session.close()

        return access_token

    async def notify(
        self,
        token: str,
        *,
        message: str,
        image_thumbnail: Optional[str] = None,
        image_full_size: Optional[str] = None,
        sticker_package_id: Optional[str] = None,
        sticker_id: Optional[str] = None,
        notification_disabled: bool = False,
    ) -> None:
        """
        Sends a message to LINE Notify.

        Args:
            message (str): The message to be sent.
            token (str): The token of the LINE Notify channel.
            image_thumbnail (Optional[str], optional): The URL of the image thumbnail. Defaults to None.
            image_full_size (Optional[str], optional): The URL of the full-size image. Defaults to None.
            sticker_package_id (Optional[str], optional): The ID of the sticker package. Defaults to None. [Sticker List](https://developers.line.biz/en/docs/messaging-api/sticker-list/)
            sticker_id (Optional[str], optional): The ID of the sticker. Defaults to None.
            notification_disabled (bool, optional): Whether to disable notification for the message. Defaults to False.

        Returns:
            None
        """
        session = self._session or aiohttp.ClientSession()
        await session.post(
            "https://notify-api.line.me/api/notify",
            data={
                "message": message,
                "imageThumbnail": image_thumbnail,
                "imageFullsize": image_full_size,
                "stickerPackageId": sticker_package_id,
                "stickerId": sticker_id,
                "notificationDisabled": notification_disabled,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        if self._session is None:
            await session.close()
