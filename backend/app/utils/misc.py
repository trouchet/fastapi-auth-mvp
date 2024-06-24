from fastapi import Depends, HTTPException, status
from fastapi.requests import Request
from httpx import AsyncClient as HTTPClient

from backend.app.logging import logger 

async def get_status_code(request: Request):
  # Extract status code from request 
  status_code = request.status_code
  if status_code is None:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
  return status_code


async def get_cat_image_url(status_code: int = Depends(get_status_code)):
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