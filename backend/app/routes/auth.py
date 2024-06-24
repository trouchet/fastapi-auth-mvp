from datetime import timedelta
from typing import Annotated, Tuple

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.auth import create_token
from backend.app.data import refresh_tokens
from backend.app.models.users import User, Token
from backend.app.auth import validate_refresh_token
from backend.app.constants import (
    DEFAULT_ACCESS_TIMEOUT_MINUTES,
    DEFAULT_REFRESH_TIMEOUT_MINUTES,
)
from backend.app.repositories.users import get_user_repo

# Create an instance of the FastAPI class
router=APIRouter(
    tags=["auth"],
)

OAuthDependency=Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/token")
async def login_for_access_token(
    form_data: OAuthDependency,
    user_repo=Depends(get_user_repo)
) -> Token:    
    try: 
        username, password = form_data.username, form_data.password
        user = user_repo.is_user_credentials_authentic(username, password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    auth_data={
        "sub": user.user_username, 
        "roles": user.user_roles
    }
    access_token = create_token(
        data=auth_data, expires_delta=DEFAULT_ACCESS_TIMEOUT_MINUTES
    )
    refresh_token = create_token(
        data=auth_data, expires_delta=DEFAULT_REFRESH_TIMEOUT_MINUTES
    )
    
    # Update user's last login and tokens
    user_repo.update_user_last_login(user)
    user_repo.update_user_access_token(user, access_token)
    user_repo.update_user_refresh_token(user, refresh_token)

    refresh_tokens.append(refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token)

RefreshTokenDependency=Annotated[
    Tuple[User, str], Depends(validate_refresh_token)
]
@router.post("/refresh")
async def refresh_access_token(token_data: RefreshTokenDependency):
    user, token = token_data
    auth_data={
        "sub": user.user_username, 
        "roles": user.user_roles
    }

    # Create new tokens
    access_token = create_token(data=auth_data, expires_delta=DEFAULT_ACCESS_TIMEOUT_MINUTES)
    refresh_token = create_token(data=auth_data, expires_delta=DEFAULT_REFRESH_TIMEOUT_MINUTES)

    # Remove the old refresh token and add the new one
    refresh_tokens.remove(token)
    refresh_tokens.append(refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token)
