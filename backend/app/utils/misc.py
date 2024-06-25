from httpx import AsyncClient as HTTPClient

from backend.app.core.logging import logger 

def get_cat_image_url(status_code: int):
    return f"https://http.cat/images/{status_code}.jpg"


async def fetch_image(image_url: str):
    async with HTTPClient() as client:
        response = await client.get(image_url)
    
    # Raise exception for non-200 status codes
    response.raise_for_status()  
    
    return await response.aread()

def try_do(func, action, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error {action}: {e}")