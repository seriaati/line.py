from typing import Awaitable, Callable


def command(func: Callable[..., Awaitable[None]]):
    async def wrapper(*args, **kwargs):
        await func(*args, **kwargs)

    setattr(wrapper, "__is_command__", True)
    wrapper.original_function = func

    return wrapper
