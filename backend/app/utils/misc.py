from httpx import AsyncClient, HTTPStatusError, RequestError
import asyncio
import inspect

from backend.app.base.logging import logger 

def get_cat_image_url(status_code: int):
    return f"https://http.cat/images/{status_code}.jpg"




async def fetch_image(image_url: str, timeout: float = 10.0):
    """Fetch an image from the provided URL with a timeout and error handling."""
    async with AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(image_url)
            response.raise_for_status()  # Raises for 4xx or 5xx status codes
            print(f"Status Code: {response.status_code}")  # Log for debugging
            return await response.aread()
        except HTTPStatusError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except RequestError as req_err:
            print(f"Request error occurred: {req_err}")
        except asyncio.TimeoutError:
            print(f"Timeout occurred after {timeout} seconds.")
    return None  # Return None if the request failed


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

