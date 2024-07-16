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

# backend/app/routes/auth.py                    42     24    43%   34-63, 72-83
# backend/app/routes/bundler.py                  8      0   100%
# backend/app/routes/data.py                    13      2    85%   17, 25
# backend/app/routes/email.py                    8      3    62%   18-27
# backend/app/routes/health.py                  16      7    56%   18-22, 30-34, 43
# backend/app/routes/public.py                  28      0   100%
# backend/app/routes/roles_bundler.py            4      0   100%
# backend/app/routes/system.py                  20      8    60%   13-16, 28-35
# backend/app/routes/users.py                  152     95    38%   42, 60-62, 72-80, 90-111, 124-141, 153-159, 166-172, 183-191, 202-210, 221-232, 244-265, 275-283, 293-301, 311-319, 329-331