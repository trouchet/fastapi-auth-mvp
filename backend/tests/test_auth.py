import pytest

from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError
from unittest.mock import patch


from backend.app.auth import (
    get_user, 
    get_current_user,
    validate_refresh_token,
    get_current_active_user,
    authenticate_user, 
    create_token,
    ALGORITHM, SECRET_KEY,
)

def test_get_user_existing(test_users_db, test_user):
    username=test_user['username']
    test_users_db.append(test_user)
    
    user = get_user(test_users_db, username)
    
    assert user.username == username


def test_get_user_nonexistent(test_users_db, test_user):
    username = "janedoe"
    user = get_user(test_users_db, username)
    
    assert user is None


def test_authenticate_user_correct_credentials(
    test_users_db, test_user, test_user_password
):
    username=test_user['username']

    test_users_db.append(test_user)
    is_user = authenticate_user(test_users_db, username, test_user_password)

    assert is_user


def test_authenticate_user_incorrect_password(
    test_users_db, test_user
):
    username=test_user['username']
    incorrect_password='any_password'

    test_users_db.append(test_user)

    with pytest.raises(HTTPException) as excinfo:
        authenticate_user(test_users_db, username, incorrect_password)
    
    assert "Incorrect password" in str(excinfo.value)


def test_authenticate_user_nonexistent_user(
    test_users_db, 
    test_user, test_user_password, 
    test_admin, test_admin_password
):   
    username=test_user['username']    
    test_users_db.append(test_admin)

    with pytest.raises(HTTPException) as excinfo:
        authenticate_user(test_users_db, username, test_user_password)

    assert "Username does not exist" in str(excinfo.value)


def test_create_token_with_custom_expiry(test_users_db, test_user):
    custom_expiry = timedelta(minutes=30)

    test_user['roles']=list(test_user['roles'])
    token = create_token(test_user, custom_expiry)

    # decode the token and check expiration
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    expire_time = datetime.fromtimestamp(decoded_token["exp"])
    
    assert expire_time > datetime.now() + timedelta(minutes=25)


def test_create_token_default_expiry(test_users_db, test_user):
    test_user['roles']=list(test_user['roles'])
    token = create_token(test_user)
    
    # decode the token and check expiration (should be 15 minutes)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expire_time = datetime.fromtimestamp(decoded_token["exp"])
    
    assert expire_time > datetime.now() + timedelta(minutes=12)

@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_users_db, test_user, test_user_password):
    username = test_user['username']
    test_users_db.append(test_user)

    user = authenticate_user(test_users_db, username, test_user_password)

    user.roles=list(user.roles)
    user_dict={
        'sub': user.username
    }
    user_dict.update(dict(user))
    token = create_token(user_dict)

    current_user = await get_current_user(test_users_db, token)

    assert current_user.username == username


@pytest.mark.asyncio
async def test_get_current_user_inexistent_user(test_users_db, test_user, test_user_password):
    username = test_user['username']
    test_users_db.append(test_user)

    user = authenticate_user(test_users_db, username, test_user_password)

    user.roles=list(user.roles)
    user_dict={
        'sub': "inexistent user"
    }
    user_dict.update(dict(user))
    token = create_token(user_dict)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(test_users_db, token)

    assert "Username does not exist" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_user_incomplete_data(test_users_db, test_user, test_user_password):
    username = test_user['username']
    test_users_db.append(test_user)

    user = authenticate_user(test_users_db, username, test_user_password)

    user.roles=list(user.roles)
    user_dict={} # inexistent claim
    user_dict.update(dict(user))
    token = create_token(user_dict)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(test_users_db, token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_users_db):
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(test_users_db, invalid_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_user_missing_username_in_token(test_users_db, test_user):
    test_user['roles']=list(test_user['roles'])
    
    token = create_token(test_user)

    # modify token to remove username claim
    user_len=len(f".username:{test_user['username']}")
    modified_token = token[:-user_len]

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(test_users_db, modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_current_active_user(test_users_db, test_user, test_user_password):
    # Use a valid token for an active user
    username = test_user['username']

    test_users_db.append(test_user)

    user = authenticate_user(test_users_db, username, test_user_password)
    
    user.roles=list(user.roles)
    user_dict={
        'sub': user.username
    }
    user_dict.update(dict(user))
    token = create_token(user_dict)

    current_user = await get_current_user(test_users_db, token)
    active_user = get_current_active_user(current_user)

    assert active_user.username == username

@pytest.mark.asyncio
async def test_get_current_active_user_inactive_user(
    test_users_db, test_user, test_user_password
):
    # Use a valid token for an inactive user
    username = test_user['username']
    test_users_db.append(test_user)

    # Create copy with modified is_active
    inactive_user = {**test_users_db[0], "is_active": False}  

    # Temporarily modify fake_db for test
    test_users_db[0] = inactive_user

    user = authenticate_user(test_users_db, username, test_user_password)

    user.roles=list(user.roles)
    user_dict={
        'sub': user.username
    }
    user_dict.update(dict(user))
    token = create_token(user_dict)

    current_user = await get_current_user(test_users_db, token)

    with pytest.raises(HTTPException) as excinfo:
        get_current_active_user(current_user)

    assert "Inactive user" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_valid_token(
    test_users_db, test_user, test_user_password, test_refresh_tokens
):
    # Create a refresh token for a user
    username=test_user['username']
    test_users_db.append(test_user)

    user = authenticate_user(test_users_db, username, test_user_password)

    user.roles=list(user.roles)
    user_dict={
        'sub': user.username
    }
    user_dict.update(dict(user))
    refresh_token = create_token(user_dict)

    # Add token to the list
    test_refresh_tokens.append(refresh_token)  
    validated_user, _ = await validate_refresh_token(
        test_users_db, test_refresh_tokens, refresh_token 
    )

    assert validated_user.username == username

@pytest.mark.asyncio
@patch('backend.app.auth.jwt.decode')
async def test_validate_refresh_token_JWT_error(
    mock_jwt_decode, test_users_db, test_refresh_tokens
):
    # Mock jwt.decode to raise JWTError
    mock_jwt_decode.side_effect = JWTError

    token = "invalid_token"
    
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, token)
    
    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_invalid_token(test_users_db, test_refresh_tokens):
    invalid_token = "invalid_refresh_token"

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, invalid_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_missing_username_in_token(test_users_db, test_refresh_tokens, test_user):
    # Assuming this creates a refresh token (modify for your implementation)
    test_user['roles']=list(test_user['roles'])
    token = create_token(test_user)

    username=test_user["username"]
    user_len=len(f".username:{username}")
    modified_token = token[:-user_len]
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_missing_role_in_token(
    test_users_db, test_refresh_tokens, test_user
):
    test_user['roles']=list(test_user['roles'])
    token = create_token(test_user)
    modified_token = token[:-len(f".roles:{test_user['roles']}")]

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, modified_token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_vaildate_refresh_token_inexistent_user(
    test_users_db, test_user, test_user_password, test_refresh_tokens
):
    # Create a refresh token for a user
    username=test_user['username']
    test_users_db.append(test_user)

    user = authenticate_user(test_users_db, username, test_user_password)

    user.roles=list(user.roles)
    user_dict={
        'sub': 'inexistent user'
    }
    user_dict.update(dict(user))
    refresh_token = create_token(user_dict)

    # Add token to the list
    test_refresh_tokens.append(refresh_token)  
    
    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(
            test_users_db, test_refresh_tokens, refresh_token 
        )

    assert "Could not validate credentials" in str(excinfo.value)

@pytest.mark.asyncio
async def test_validate_refresh_token_expired_token(
    test_users_db, test_refresh_tokens, test_user
):
    test_user['roles']=list(test_user['roles'])
    
    # Simulate an expired refresh token by modifying the expiry in the payload
    custom_expiry = timedelta(seconds=0)
    token = create_token(test_user, custom_expiry)
    
    test_refresh_tokens.append(token)

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_nonexistent_user(
    test_users_db, test_refresh_tokens, test_user
):
    test_user['roles']=list(test_user['roles'])
    
    # Create a refresh token with a username not in the test_users_db
    token = create_token(test_user)
    test_refresh_tokens.append(token)

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, token)

    assert "Could not validate credentials" in str(excinfo.value)


@pytest.mark.asyncio
async def test_validate_refresh_token_nonexistent_user(
    test_users_db, test_refresh_tokens, test_user
):
    test_user['roles']=list(test_user['roles'])
    
    # Create a refresh token with a username not in the test_users_db
    token = create_token(test_user)
    test_refresh_tokens.append(token)

    with pytest.raises(HTTPException) as excinfo:
        await validate_refresh_token(test_users_db, test_refresh_tokens, token)

    assert "Could not validate credentials" in str(excinfo.value)
