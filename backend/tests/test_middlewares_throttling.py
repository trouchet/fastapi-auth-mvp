import pytest

from asynctest import MagicMock, CoroutineMock, patch
from backend.app.middlewares.throttling import RateLimitMiddleware

# Helper function to set up mocks
def setup_mocks(mock_get_user_repo, mock_get_log_repo, rate_limit_policy):
    # Mock the user repository
    mock_user_repo_instance = MagicMock()
    mock_user_repo_instance.get_user_rate_limit_policy = CoroutineMock(
        return_value=rate_limit_policy
    )
    mock_get_user_repo.return_value.__aenter__.return_value = mock_user_repo_instance

    # Mock the log repository
    mock_log_repo_instance = MagicMock()
    mock_log_repo_instance.create_rate_limit_log = CoroutineMock()
    mock_get_log_repo.return_value.__aenter__.return_value = mock_log_repo_instance

@pytest.mark.asyncio
@patch("backend.app.middlewares.throttling.get_user_repository")
@patch("backend.app.middlewares.throttling.get_log_repository")
async def test_rate_limit_exceeded(mock_get_user_repo, mock_get_log_repo, async_client):
    rate_limit_policy = {
        "times": 1,
        "hours": 0,
        "minutes": 1,
        "seconds": 0,
        "milliseconds": 0
    }
    setup_mocks(mock_get_user_repo, mock_get_log_repo, rate_limit_policy)

    # Make the first request, which should pass
    response = await async_client.get(
        "/test", headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "success"}

    # Make the second request, which should be rate limited
    response = await async_client.get(
        "/test", headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 429

    # Ensure the rate limit log was created
    mock_log_repo_instance = mock_get_log_repo.return_value.__aenter__.return_value
    mock_log_repo_instance.create_rate_limit_log.assert_called_once_with(1, "/test")

@pytest.mark.asyncio
@patch("backend.app.middlewares.throttling.get_user_repository")
@patch("backend.app.middlewares.throttling.get_log_repository")
async def test_missing_token(mock_get_user_repo, mock_get_log_repo, async_client):
    rate_limit_policy = {
        "times": 5,
        "hours": 0,
        "minutes": 1,
        "seconds": 0,
        "milliseconds": 0
    }
    setup_mocks(mock_get_user_repo, mock_get_log_repo, rate_limit_policy)

    # Make a request without an authorization header
    response = await async_client.get("/test")
    assert response.status_code == 400  # Assuming your middleware returns 400 for missing tokens

@pytest.mark.asyncio
@patch("backend.app.middlewares.throttling.get_user_repository")
@patch("backend.app.middlewares.throttling.get_log_repository")
async def test_valid_request(mock_get_user_repo, mock_get_log_repo, async_client):
    rate_limit_policy = {
        "times": 5,
        "hours": 0,
        "minutes": 1,
        "seconds": 0,
        "milliseconds": 0
    }
    setup_mocks(mock_get_user_repo, mock_get_log_repo, rate_limit_policy)

    # Make a valid request
    response = await async_client.get(
        "/test", headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "success"}

    # Ensure the rate limit log was not created
    mock_log_repo_instance = mock_get_log_repo.return_value.__aenter__.return_value
    mock_log_repo_instance.create_rate_limit_log.assert_not_called()

@pytest.mark.asyncio
@patch("backend.app.middlewares.throttling.get_user_repository")
@patch("backend.app.middlewares.throttling.get_log_repository")
async def test_different_rate_limits(mock_get_user_repo, mock_get_log_repo, async_client):
    rate_limit_policy_user = {
        "times": 5,
        "hours": 0,
        "minutes": 1,
        "seconds": 0,
        "milliseconds": 0
    }
    rate_limit_policy_admin = {
        "times": 10,
        "hours": 0,
        "minutes": 1,
        "seconds": 0,
        "milliseconds": 0
    }
    setup_mocks(mock_get_user_repo, mock_get_log_repo, rate_limit_policy_user)

    # Test user rate limit
    response = await async_client.get(
        "/test", headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200

    # Mock admin role
    async def mock_admin_identifier_callable(token: str):
        class MockAdminUser:
            user_username = "admin_user"
            user_id = 2
            user_roles = ["Admin"]
        return MockAdminUser

    app_with_middleware.add_middleware(
        RateLimitMiddleware, identifier_callable=mock_admin_identifier_callable
    )

    setup_mocks(mock_get_user_repo, mock_get_log_repo, rate_limit_policy_admin)

    # Test admin rate limit
    response = await async_client.get(
        "/test", headers={"Authorization": "Bearer admin_token"}
    )
    assert response.status_code == 200
