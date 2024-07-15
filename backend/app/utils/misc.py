from httpx import AsyncClient
import inspect

from backend.app.base.logging import logger 

def get_cat_image_url(status_code: int):
    return f"https://http.cat/images/{status_code}.jpg"


async def fetch_image(image_url: str):
    async with AsyncClient() as client:
        response = await client.get(image_url)

    # Raise exception for non-200 status codes
    response.raise_for_status()  

    return await response.aread()


async def is_async(func):
    """
    Checks if a function is asynchronous.

    Args:
        func: The function to check.

    Returns:
        bool: True if the function is asynchronous, False otherwise.
    """
    return (
        inspect.iscoroutinefunction(func)
        or inspect.isasyncgenfunction(func)
        or hasattr(func, "__await__")
    )


async def try_do(func, action, *args, **kwargs):
    try:
        if(await is_async(func)):
            return await func(*args, **kwargs)
        else:
            return  func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error {action}: {e}")

