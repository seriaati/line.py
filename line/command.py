from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


def command(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
    """A decorator that marks a function as a command.

    Args:
        func: The function to mark as a command.

    Returns:
        The decorated function.
    """

    async def wrapper(*args: Any, **kwargs: Any) -> None:
        await func(*args, **kwargs)

    wrapper.__is_command__ = True  # pyright: ignore[reportFunctionMemberAccess]
    wrapper.original_function = func  # pyright: ignore[reportFunctionMemberAccess]

    return wrapper
