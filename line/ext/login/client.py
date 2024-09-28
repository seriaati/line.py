from __future__ import annotations

from typing import Literal

import aiohttp

from ...exceptions import raise_for_status
from .response import UserProfile


class LineLoginAPI:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._redirect_uri = redirect_uri

    def get_oauth_uri(
        self,
        state: str,
        scopes: Literal[
            "profile", "profile%20openid", "profile%20openid%20email", "openid", "openid%20email"
        ],
    ) -> str:
        """Returns the OAuth URI for LINE Login.

        Args:
            state (str): A string that will be returned in the response to the client.
            scopes (Literal): A string literal that specifies the permissions that the application requests.

        Returns:
            str: The OAuth URI for LINE Login.
        """
        base_uri = "https://access.line.me/oauth2/v2.1/authorize"
        return f"{base_uri}?response_type=code&client_id={self.__client_id}&redirect_uri={self._redirect_uri}&state={state}&scope={scopes}"

    async def issue_access_token(self, code: str) -> str:
        """Issues an access token using the authorization code.

        Args:
            code (str): The authorization code.

        Returns:
            str: The access token.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post("https://api.line.me/oauth2/v2.1/token", data=data) as resp,
        ):
            raise_for_status(resp.status)
            return (await resp.json())["access_token"]

    @staticmethod
    async def verify_access_token_validity(access_token: str) -> bool:
        """Verify the validity of an access token by sending a GET request to the LINE API.

        Args:
            access_token (str): The access token to verify.

        Returns:
            bool: True if the access token is valid, False otherwise.
        """
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                "https://api.line.me/oauth2/v2.1/verify", params={"access_token": access_token}
            ) as resp,
        ):
            return resp.status == 200

    @staticmethod
    async def get_user_profile(access_token: str) -> UserProfile:
        """Retrieves the user profile of the user associated with the given access token.

        Args:
            access_token: The access token associated with the user.

        Returns:
            UserProfile: An object representing the user's profile information.
        """
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                "https://api.line.me/v2/profile",
                headers={"Authorization": f"Bearer {access_token}"},
            ) as resp,
        ):
            raise_for_status(resp.status)
            return UserProfile(**(await resp.json()))
