import pytest

from fastapi import HTTPException
from unittest.mock import patch
import aiohttp

from backend.app.base.config import settings

@pytest.mark.asyncio
async def test_hello_func(test_client):
    response = await test_client.get(f"{settings.API_V1_STR}/public/hello")
    assert response.status_code == 200
    assert response.json() == "Hello World"

@pytest.mark.asyncio
async def test_cat_by_status_success(test_client):
    response = await test_client.get(f"{settings.API_V1_STR}/public/cat/200")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

@pytest.mark.asyncio
async def test_cat_by_status_http_exception(test_client):
    response = await test_client.get(f"{settings.API_V1_STR}/public/cat/404")
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cat_by_status_exception(test_client):
    response = await test_client.get(f"{settings.API_V1_STR}/public/cat/500")
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cat_page(test_client):
    response = await test_client.get(f"{settings.API_V1_STR}/public/cat/page/200")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

@pytest.mark.asyncio
async def test_cat_by_status_http_exception(test_client):
    with patch("backend.app.routes.public.get_cat_image_url") as mock_get_url:
        with patch("backend.app.routes.public.fetch_image") as mock_fetch_image:
            mock_get_url.return_value = "http://example.com/cat.jpg"
            mock_fetch_image.side_effect = HTTPException(status_code=404, detail="Not Found")

            response = await test_client.get(f"{settings.API_V1_STR}/public/cat/404")

            assert response.status_code == 404
            assert response.json() == "Not Found"


@pytest.mark.asyncio
async def test_cat_by_status_generic_exception(test_client):
    with patch("backend.app.routes.public.get_cat_image_url") as mock_get_url:
        with patch("backend.app.routes.public.fetch_image") as mock_fetch_image:
            mock_get_url.return_value = "http://example.com/cat.jpg"
            mock_fetch_image.side_effect = Exception("Something went wrong")

            response = await test_client.get(f"{settings.API_V1_STR}/public/cat/500")

            assert response.status_code == 500
            assert response.json() == "Internal Server Error"