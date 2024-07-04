import pytest
import respx
import httpx
from unittest.mock import AsyncMock

from backend.app.utils.misc import (
    get_cat_image_url, 
    fetch_image,
    try_do,
)
from unittest.mock import patch

def test_get_cat_image_url_valid_code():
    """Tests if a valid status code generates the expected URL."""
    status_code = 200
    expected_url = f"https://http.cat/images/{status_code}.jpg"
    actual_url = get_cat_image_url(status_code)
    assert actual_url == expected_url

def test_get_cat_image_url_invalid_code():
    """Tests if an invalid status code returns None."""
    invalid_code = 999
    
    expected_url = f"https://http.cat/images/{invalid_code}.jpg"
    actual_url = get_cat_image_url(invalid_code)
    assert actual_url == expected_url

    
async def test_try_do_success(capsys):
    """Tests if successful execution doesn't log errors."""

    def do_nothing():
        pass

    await try_do(do_nothing, "test_action")
    captured = capsys.readouterr()

    assert captured.out == ""  # No output on success
    assert captured.err == ""  # No errors logged

@patch('backend.app.utils.misc.logger')
async def test_try_do_exception(logger_mocker):
    """Tests if exceptions are logged with the action message."""

    def raise_exception():
        raise ValueError("Test exception")

    await try_do(raise_exception, "test_action")

    assert logger_mocker.error.called


@pytest.mark.asyncio
async def test_fetch_image_success():
    # Mock the response
    url = "https://example.com/image.jpg"
    content = b'image data'

    async with respx.mock:
        respx.get(url).respond(200, content=content)
        
        result = await fetch_image(url)

        assert result == content

@pytest.mark.asyncio
async def test_fetch_image_non_200_status():
    # Mock the response with a 404 status
    url = "https://example.com/image.jpg"

    async with respx.mock:
        respx.get(url).respond(404)

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_image(url)

@pytest.mark.asyncio
async def test_fetch_image_exception():
    # Mock a network error
    url = "https://example.com/image.jpg"

    async with respx.mock:
        respx.get(url).side_effect = httpx.RequestError("Network error")

        with pytest.raises(httpx.RequestError):
            await fetch_image(url)