import functools
from typing import Callable


def register_task(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print(f"Starting task {func.__name__}")
        result = await func(*args, **kwargs)
        print(f"Finished task {func.__name__}")
        return result

    return wrapper
