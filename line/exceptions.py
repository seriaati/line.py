from typing import Any

import aiohttp


class CommandExecError(Exception):
    def __init__(self, command_name: str, e: Exception) -> None:
        self.command_name = command_name
        self.e = e

    def __str__(self) -> str:
        return f"An error occurred while executing the command {self.command_name}: {self.e}"


class ParamParseError(Exception):
    def __init__(self, command_name: str, e: Exception) -> None:
        self.command_name = command_name
        self.e = e

    def __str__(self) -> str:
        return f"An error occurred while parsing the parameters of the command {self.command_name}: {self.e}"


class IntConvertError(Exception):
    def __init__(self, param_name: str, value: Any) -> None:
        self.param_name = param_name
        self.value = value

    def __str__(self) -> str:
        return f"The parameter {self.param_name} is type hinted as int, but the value {self.value} cannot be converted to int"


class CogLoadError(Exception):
    def __init__(self, cog_path, e: Exception | str) -> None:
        self.cog_path = cog_path
        self.e = e

    def __str__(self) -> str:
        return f"An error occurred while loading the cog {self.cog_path}: {self.e}"


class BadRequest(Exception):
    def __str__(self) -> str:
        return "400: There was a problem with the request. Check the request parameters and JSON format."


class Unauthorized(Exception):
    def __str__(self) -> str:
        return "401: Check that the authorization header is correct."


class Forbidden(Exception):
    def __str__(self) -> str:
        return "403: You are not authorized to use the API. Confirm that your account or plan is authorized to use the API."


class PayloadTooLarge(Exception):
    def __str__(self) -> str:
        return "413: Request exceeds the max size of 2MB. Make the request smaller than 2MB and try again."


class TooManyRequests(Exception):
    def __str__(self) -> str:
        return "429: Temporarily restricting requests because rate-limit has been exceeded by a large number of requests."


class InternalServerEror(Exception):
    def __str__(self) -> str:
        return "500: There was a temporary error on the API server."


def raise_for_status(status_code: int) -> None:
    """
    Raises an exception if the status code of the response is not 200.

    Args:
        status_code (int): The status code of the response.
    """
    if status_code == 400:
        raise BadRequest
    elif status_code == 401:
        raise Unauthorized
    elif status_code == 403:
        raise Forbidden
    elif status_code == 413:
        raise PayloadTooLarge
    elif status_code == 429:
        raise TooManyRequests
    elif status_code == 500:
        raise InternalServerEror
