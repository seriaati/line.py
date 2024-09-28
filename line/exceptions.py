from __future__ import annotations

from typing import Any


class LineAPIError(Exception):
    pass


class LineError(Exception):
    pass


class CommandExecError(LineError):
    def __init__(self, command_name: str, e: Exception) -> None:
        self.command_name = command_name
        self.e = e

    def __str__(self) -> str:
        return f"An error occurred while executing the command {self.command_name}: {self.e}"


class ParamParseError(LineError):
    def __init__(self, command_name: str, e: Exception) -> None:
        self.command_name = command_name
        self.e = e

    def __str__(self) -> str:
        return f"An error occurred while parsing the parameters of the command {self.command_name}: {self.e}"


class IntConvertError(LineError):
    def __init__(self, param_name: str, value: Any) -> None:
        self.param_name = param_name
        self.value = value

    def __str__(self) -> str:
        return f"The parameter {self.param_name} is type hinted as int, but the value {self.value} cannot be converted to int"


class FloatConvertError(LineError):
    def __init__(self, param_name: str, value: Any) -> None:
        self.param_name = param_name
        self.value = value

    def __str__(self) -> str:
        return f"The parameter {self.param_name} is type hinted as float, but the value {self.value} cannot be converted to float"


class CogLoadError(LineError):
    def __init__(self, cog_path: Any, e: Exception | str) -> None:
        self.cog_path = cog_path
        self.e = e

    def __str__(self) -> str:
        return f"An error occurred while loading the cog {self.cog_path}: {self.e}"


class BadRequestError(LineAPIError):
    def __str__(self) -> str:
        return "400: There was a problem with the request. Check the request parameters and JSON format."


class UnauthorizedError(LineAPIError):
    def __str__(self) -> str:
        return "401: Check that the authorization header is correct."


class ForbiddenError(LineAPIError):
    def __str__(self) -> str:
        return "403: You are not authorized to use the API. Confirm that your account or plan is authorized to use the API."


class PayloadTooLargeError(LineAPIError):
    def __str__(self) -> str:
        return "413: Request exceeds the max size of 2MB. Make the request smaller than 2MB and try again."


class TooManyRequestsError(LineAPIError):
    def __str__(self) -> str:
        return "429: Temporarily restricting requests because rate-limit has been exceeded by a large number of requests."


class InternalServerError(LineAPIError):
    def __str__(self) -> str:
        return "500: There was a temporary error on the API server."


def raise_for_status(status_code: int) -> None:
    """Raises an exception if the status code of the response is not 200.

    Args:
        status_code (int): The status code of the response.

    Raises:
        BadRequestError: If the status code is 400.
        UnauthorizedError: If the status code is 401.
        ForbiddenError: If the status code is 403.
        PayloadTooLargeError: If the status code is 413.
        TooManyRequestsError: If the status code is 429.
        InternalServerError: If the status code is 500.
    """
    if status_code == 400:
        raise BadRequestError
    if status_code == 401:
        raise UnauthorizedError
    if status_code == 403:
        raise ForbiddenError
    if status_code == 413:
        raise PayloadTooLargeError
    if status_code == 429:
        raise TooManyRequestsError
    if status_code == 500:
        raise InternalServerError
