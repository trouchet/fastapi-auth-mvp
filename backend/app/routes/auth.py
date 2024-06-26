from typing import Annotated, Tuple

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.core.auth import create_token
from backend.app.models.users import User, Token
from backend.app.core.auth import validate_refresh_token

from backend.app.repositories.users import get_user_repo
from backend.app.core.exceptions import (
    InexistentUsernameException, 
    CredentialsException,
)
from backend.app.core.config import settings

# Create an instance of the FastAPI class
router=APIRouter(prefix='/auth', tags=["Authorization"])

OAuthDependency = Annotated[OAuth2PasswordRequestForm, Depends()]


DEFAULT_ACCESS_TIMEOUT_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_REFRESH_TIMEOUT_MINUTES=settings.REFRESH_TOKEN_EXPIRE_MINUTES

DEFAULT_ACCESS_TIMEOUT_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_REFRESH_TIMEOUT_MINUTES=settings.REFRESH_TOKEN_EXPIRE_MINUTES

@router.post("/token")
async def login_for_access_token(
    form_data: OAuthDependency,
    user_repo=Depends(get_user_repo)
) -> Token:
    try: 
        username, password = form_data.username, form_data.password
        user = user_repo.get_user_by_username(username)
        
        if not user:
            raise InexistentUsernameException(username=username)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    is_authentic=user_repo.is_user_credentials_authentic(username, password)
    if not is_authentic:
        raise CredentialsException()

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
    user_repo.update_user_last_login(username)
    user_repo.update_user_access_token(username, access_token)
    user_repo.update_user_refresh_token(username, refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token)


RefreshTokenDependency = Annotated[Tuple[User, str], Depends(validate_refresh_token)]


@router.post("/refresh")
async def refresh_access_token(
    token_data: RefreshTokenDependency,
    user_repo = Depends(get_user_repo)
):    
    user, token = token_data
    auth_data = {"sub": user.user_username, "roles": user.user_roles}

    # Create new tokens
    access_token = create_token(data=auth_data, expires_delta=DEFAULT_ACCESS_TIMEOUT_MINUTES)
    refresh_token = create_token(data=auth_data, expires_delta=DEFAULT_REFRESH_TIMEOUT_MINUTES)
    
    # Update user's tokens
    user_repo.update_user_access_token(user.user_username, access_token)
    user_repo.update_user_refresh_token(user.user_username, refresh_token)
    
    return Token(access_token=access_token, refresh_token=refresh_token)
