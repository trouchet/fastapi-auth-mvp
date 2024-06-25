import pytest
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

    
def test_try_do_success(capsys):
    """Tests if successful execution doesn't log errors."""

    def do_nothing():
        pass

    try_do(do_nothing, "test_action")
    captured = capsys.readouterr()

    assert captured.out == ""  # No output on success
    assert captured.err == ""  # No errors logged

@patch('backend.app.utils.misc.logger')
def test_try_do_exception(logger_mocker):
    """Tests if exceptions are logged with the action message."""

    def raise_exception():
        raise ValueError("Test exception")

    try_do(raise_exception, "test_action")

    assert logger_mocker.error.called
