import pytest

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from jose import jwt


from backend.app.auth import (
    get_user, 
    get_current_user,
    validate_refresh_token,
    get_current_active_user,
    authenticate_user, 
    create_token,
    RoleChecker,
    pwd_context, ALGORITHM, SECRET_KEY,
)
from backend.app.auth import get_current_active_user

def test_get_user_existing(test_users_db, test_user):
    username=test_user['username']
    
    user = get_user(test_users_db, username)
    
    assert user.username == username


def test_get_user_nonexistent(test_users_db):
    username = "janedoe"
    user = get_user(test_users_db, username)
    
    assert user is None


def test_authenticate_user_correct_credentials(
    test_users_db, test_user, user_password
):
    username=test_user['username']
    
    test_users_db[username] = test_user
    user = authenticate_user(test_users_db, username, user_password)
    
    assert user.username == username


def test_authenticate_user_incorrect_password(
    test_users_db, test_user, user_password
):
    username=test_user['username']

    test_users_db[username] = test_user
    user = authenticate_user(test_users_db, username, user_password)
    assert user is False


def test_authenticate_user_nonexistent_user(test_users_db):
    username = "janedoe"
    password = "any_password"
    user = authenticate_user(test_users_db, username, password)
    
    assert user is False


def test_create_token_with_custom_expiry(test_users_db, test_user):
    custom_expiry = timedelta(minutes=30)

    token = create_token(test_user, custom_expiry)

    # decode the token and check expiration
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expire_time = datetime.fromtimestamp(decoded_token["exp"])

    assert expire_time > datetime.now(timezone.utc) + timedelta(minutes=25)


def test_create_token_default_expiry(test_users_db, test_user):
    token = create_token(test_user)
    
    # decode the token and check expiration (should be 15 minutes)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expire_time = datetime.fromtimestamp(decoded_token["exp"])
    
    assert expire_time > datetime.now(timezone.utc) + timedelta(minutes=12)


async def test_get_current_user_valid_token(test_users_db, test_user, user_password):
    username = test_user['username']
    
    user = authenticate_user(test_users_db, username, user_password)
    token = create_token(user)
    current_user = await get_current_user(Depends(token))
    
    assert current_user.username == username


async def test_get_current_user_invalid_token(test_users_db):
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(Depends(invalid_token))

    assert "Could not validate credentials" in str(excinfo.value)


async def test_get_current_user_missing_username_in_token(test_users_db, test_user):
    token = create_token(test_user)

    # modify token to remove username claim
    modified_token = token[:-len(".username:peterpan}")]

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(Depends(modified_token))
    
    assert "Could not validate credentials" in str(excinfo.value)


async def test_get_current_active_user(test_users_db, test_user):
    wrong_password="any_password"

    # Use a valid token for an active user
    username = test_user['username']
    user = authenticate_user(test_users_db, username, wrong_password)
    token = create_token(user)

    current_user = await get_current_user(Depends(token))
    active_user = get_current_active_user(current_user)

    assert active_user.username == username


def test_get_current_active_user_inactive_user(test_users_db, test_user):
    # Use a valid token for an inactive user
    username = test_user['username']
    test_users_db.append(test_user)

    inactive_user = {**test_users_db[0], "is_active": False}  # Create copy with modified is_active

    # Temporarily modify fake_db for test
    test_users_db[0] = inactive_user
    
    user = authenticate_user(test_users_db, username, "any_password")
    
    token = create_token(user)
    
    with pytest.raises(HTTPException) as excinfo:
        get_current_active_user(Depends(token))
    
    assert "Inactive user" in str(excinfo.value)


def test_user_checker_authorized_role(test_users_db, test_user, test_user_checker):
    username=test_user['username']
    test_users_db.append(test_user)
    
    user = get_user(test_users_db, username)
    
    # User has the allowed role
    assert test_user_checker(user) is True


def test_user_checker_unauthorized_role(test_users_db, test_user, test_admin_checker):
    username=test_user['username']
    
    test_users_db.append(test_user)
    
    user = get_user(test_users_db, username)
    
    with pytest.raises(HTTPException) as excinfo:
        test_admin_checker(user)
    
    assert "You don't have enough permissions" in str(excinfo.value)


# Assuming you've implemented refresh token generation and storage
async def test_validate_refresh_token_valid_token(test_users_db, test_refresh_tokens):
    # Create a refresh token for a user
    username = "johndoe"
    user = authenticate_user(test_users_db, username, "any_password")
    
    refresh_token = create_token(user)
    
    # Add token to the list (modify for your implementation)
    test_refresh_tokens.append(refresh_token)  
    validated_user, _ = await validate_refresh_token(Depends(refresh_token))
    
    assert validated_user.username == username


async def test_validate_refresh_token_invalid_token(test_users_db):
    invalid_token = "invalid_refresh_token"

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(Depends(invalid_token))

    assert "Could not validate credentials" in str(excinfo.value)


async def test_validate_refresh_token_missing_username_in_token(test_users_db, test_user):
    # Assuming this creates a refresh token (modify for your implementation)
    token = create_token(test_user)
    
    modified_token = token[:-len(".username:johndoe}")]
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(Depends(modified_token))
    
    assert "Could not validate credentials" in str(excinfo.value)


async def test_validate_refresh_token_missing_role_in_token(test_users_db, test_user):
    token = create_token(test_user)
    modified_token = token[:-len(".role:admin}")]

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(Depends(modified_token))

    assert "Could not validate credentials" in str(excinfo.value)


async def test_validate_refresh_token_expired_token(test_users_db, test_refresh_tokens, test_user):
    # Simulate an expired refresh token by modifying the expiry in the payload
    custom_expiry = timedelta(seconds=0)  # Set expiry to zero (already expired)
    token = create_token(test_user, custom_expiry)  # Assuming this creates a refresh token (modify for your implementation)
    
    test_refresh_tokens.append(token)

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(Depends(token))

    assert "Could not validate credentials" in str(excinfo.value)

async def test_validate_refresh_token_nonexistent_user(test_users_db, test_refresh_tokens, test_user):
    # Create a refresh token with a username not in the test_users_db
    token = create_token(test_user)
    test_refresh_tokens.append(token)

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(Depends(token))

    assert "Could not validate credentials" in str(excinfo.value)
