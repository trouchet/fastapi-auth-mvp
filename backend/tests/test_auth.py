import pytest
from typing import List

from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError
from unittest.mock import patch


from backend.app.utils.database import model_to_dict

from backend.app.core.auth import (
    get_current_user,
    validate_refresh_token,
    create_token,
    role_checker,
    JWT_ALGORITHM, JWT_SECRET_KEY,
)

def test_get_user_existing(test_user_repository, test_user):
    username=test_user.user_username
    user = test_user_repository.get_user_by_username(username)
    
    assert user.user_username == username


def test_get_user_nonexistent(test_user_repository):
    username = "unknown_user"
    user = test_user_repository.get_user_by_username(username)
    
    assert user is None

def test_authenticate_user_correct_credentials(
    test_user_repository, test_user, test_user_password
):
    username=test_user.user_username

    is_authentic=test_user_repository.is_user_credentials_authentic(
        username, test_user_password
    )
    
    assert is_authentic


def test_authenticate_user_incorrect_password(
    test_user_repository, test_user
):
    username=test_user.user_username
    incorrect_password='any_password'

    is_authentic=test_user_repository.is_user_credentials_authentic(
        username, incorrect_password
    )
    
    assert not is_authentic


def test_create_token_with_custom_expiry(test_user):
    custom_expiry = timedelta(minutes=30)
    user_dict=model_to_dict(test_user)
    
    auth_dict={
        'sub': user_dict['user_username'], 
        'roles': user_dict['user_roles']
    }
    token = create_token(auth_dict, custom_expiry)

    # decode the token and check expiration
    decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    expire_time = datetime.fromtimestamp(decoded_token["exp"])
    
    assert expire_time > datetime.now() + timedelta(minutes=25)

def test_create_token_default_expiry(test_user):    
    auth_data={
        'sub': test_user.user_username, 
        'roles': test_user.user_roles
    }
    
    token = create_token(auth_data)
    
    # decode the token and check expiration (should be 15 minutes)
    decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    expire_time = datetime.fromtimestamp(decoded_token["exp"])
    
    assert expire_time > datetime.now() + timedelta(minutes=12)

@pytest.mark.asyncio
async def test_get_current_user_valid_token(
    test_user_repository, test_user, test_user_password
):
    username = test_user.user_username

    user_dict={
        'sub': username,
        'roles': test_user.user_roles
    }
    token = create_token(user_dict)

    current_user = await get_current_user(token)

    assert current_user.user_username == username


@pytest.mark.asyncio
async def test_get_current_user_inexistent_user(
    test_user_repository, test_user, test_user_password):

    unknown_username = "unknown_user"
    auth_dict={
        'sub': unknown_username
    }
    token = create_token(auth_dict)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert f"Username {unknown_username} does not exist" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_user_incomplete_data(
    test_user_repository, test_user, test_user_password
):

    auth_dict={} # inexistent claim
    token = create_token(auth_dict)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert "Could not validate credentials" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(invalid_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_user_missing_username_in_token(test_user):
    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)

    # modify token to remove username claim
    user_len=len(f".username:{test_user.user_username}")
    modified_token = token[:-user_len]

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_active_user(test_user):
    # Use a valid token for an active user
    username = test_user.user_username

    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)

    current_user = await get_current_user(token)

    assert current_user.user_username == username


@pytest.mark.asyncio
async def test_get_current_active_user_inactive_user(
    test_user_repository, test_inactive_user
):
    # Use a valid token for an inactive user
    username = test_inactive_user.user_username
    
    auth_dict={
        'sub': test_inactive_user.user_username,
        'roles': test_inactive_user.user_roles
    }
    
    token = create_token(auth_dict)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert f"User {username} is inactive" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_valid_token(
    test_user_repository, test_user, test_user_password
):
    # Create a refresh token for a user
    username=test_user.user_username

    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    refresh_token = create_token(auth_dict)

    validated_user = test_user_repository.update_user_refresh_token(username, refresh_token)
    
    # Add token to the list
    validated_user, _ = await validate_refresh_token(refresh_token)

    assert validated_user.user_username == username


@pytest.mark.asyncio
@patch('backend.app.core.auth.jwt.decode')
async def test_validate_refresh_token_JWT_error(
    mock_jwt_decode, test_user_repository
):
    # Mock jwt.decode to raise JWTError
    mock_jwt_decode.side_effect = JWTError

    token = "invalid_token"
    
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(token)
    
    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_invalid_token(test_user_repository):
    invalid_token = "invalid_refresh_token"

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(invalid_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_user_missing_username_in_token(test_user):
    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)

    # modify token to remove username claim
    user_len=len(f".username:{test_user.user_username}")
    modified_token = token[:-user_len]

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_active_user(
    test_user_repository, test_user, test_user_password
):
    # Use a valid token for an active user
    username = test_user.user_username

    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)

    current_user = await get_current_user(token)
    
    assert current_user.user_username == username


@pytest.mark.asyncio
async def test_get_current_active_user_inactive_user(
    test_user_repository, test_inactive_user, test_user_password
):
    auth_dict={
        'sub': test_inactive_user.user_username,
        'roles': test_inactive_user.user_roles
    }
    token = create_token(auth_dict)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert "is inactive" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_valid_token(
    test_user_repository, test_user
):
    # Create a refresh token for a user
    username=test_user.user_username
    
    user_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    refresh_token = create_token(user_dict)

    test_user_repository.update_user_refresh_token(username, refresh_token)

    # Add token to the list  
    validated_user, _ = await validate_refresh_token(refresh_token)

    assert validated_user.user_username == username


@pytest.mark.asyncio
@patch('backend.app.core.auth.jwt.decode')
async def test_validate_refresh_token_JWT_error(
    mock_jwt_decode, test_users_db, test_refresh_tokens
):
    # Mock jwt.decode to raise JWTError
    mock_jwt_decode.side_effect = JWTError

    token = "invalid_token"
    
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(token)
    
    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_invalid_token(test_users_db, test_refresh_tokens):
    invalid_token = "invalid_refresh_token"

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(invalid_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_missing_username_in_token(test_users_db, test_refresh_tokens, test_user):
    # Assuming this creates a refresh token (modify for your implementation)
    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)

    username=test_user.user_username
    user_len=len(f".username:{username}")
    modified_token = token[:-user_len]
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_missing_role_in_token(test_user):
    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)
    modified_token = token[:-len(f".roles:{test_user.user_roles}")]

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_vaildate_refresh_token_inexistent_user(test_user):
    # Create a refresh token for a user

    
    user_dict={
        'sub': 'inexistent user',
        'roles': test_user.user_roles
    }
    refresh_token = create_token(user_dict)

    
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(refresh_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_expired_token(
    test_user_repository, test_user
):
    # Simulate an expired refresh token by modifying the expiry in the payload
    custom_expiry = timedelta(seconds=0)
    auth_dict={
        'sub': test_user.user_username,
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict, custom_expiry)

    test_user_repository.update_user_refresh_token(test_user.user_username, token)
    
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(token)

    assert "This token has expired" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_nonexistent_user(test_user):
    # Create a refresh token with a username not in the test_users_db
    auth_dict={
        'sub': 'unknown_user',
        'roles': test_user.user_roles
    }
    token = create_token(auth_dict)

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_role_checker_allows_authorized_role():
    """Tests if the decorator allows access with an authorized role."""
    # Mock get_current_active_user to return a user with an allowed role
    allowed_roles = ["admin"]

    with patch(
        "backend.app.auth.get_current_user", 
        return_value=MockUser(roles=["admin"])
    ):
        @role_checker(allowed_roles)
        async def protected_view():
            return "Success"
    
        # Call the decorated view and assert no exception is raised
        assert await protected_view() == "Success"


# Helper class to represent a mock user object
class MockUser:
    def __init__(self, roles: List[str]):
        self.roles = roles





