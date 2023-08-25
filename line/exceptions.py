from typing import Any


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
