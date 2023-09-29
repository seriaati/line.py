from typing import Optional

import aiohttp

from ...exceptions import raise_for_status


class LineNotifyAPI:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._redirect_uri = redirect_uri

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

        Raises:
            LineAPIError: If the request fails.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://notify-bot.line.me/oauth/token", data=data
            ) as resp:
                raise_for_status(resp.status)
                access_token = (await resp.json())["access_token"]

        return access_token

    async def notify(
        self,
        token: str,
        *,
        message: str,
        image_thumbnail: Optional[str] = None,
        image_full_size: Optional[str] = None,
        notification_disabled: bool = False,
    ) -> None:
        """
        Sends a message to LINE Notify.

        Args:
            message (str): The message to be sent.
            token (str): The token of the LINE Notify channel.
            image_thumbnail (Optional[str], optional): The URL of the image thumbnail. Defaults to None.
            image_full_size (Optional[str], optional): The URL of the full-size image. Defaults to None.
            notification_disabled (bool, optional): Whether to disable notification for the message. Defaults to False.

        Returns:
            None

        Raises:
            LineAPIError: If the request fails.
        """
        data = {
            "message": message,
            "notificationDisabled": notification_disabled,
        }
        if image_thumbnail:
            data["imageThumbnail"] = image_thumbnail
        if image_full_size:
            data["imageFullsize"] = image_full_size

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://notify-api.line.me/api/notify",
                data=data,
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                raise_for_status(resp.status)
