from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.models.auth import Token
from backend.app.services.users import UsersRepositoryDependency
from backend.app.repositories.users import (
    UsersRepository, get_users_repository
)
from backend.app.services.auth import create_token
from backend.app.models.auth import RefreshToken

from backend.app.dependencies.auth import AuthServiceDependency
from backend.app.repositories.users import get_users_repository
from backend.app.base.exceptions import (
    InexistentUsernameException, 
    CredentialsException,
)
from backend.app.base.config import settings

# Create an instance of the FastAPI class
router=APIRouter(prefix='/auth', tags=["Authorization"])

OAuthDependency = Annotated[OAuth2PasswordRequestForm, Depends()]

DEFAULT_ACCESS_TIMEOUT_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_REFRESH_TIMEOUT_MINUTES=settings.REFRESH_TOKEN_EXPIRE_MINUTES


@router.post("/token")
async def login_for_access_token(
    request: Request, 
    form_data: OAuthDependency, 
    auth_service: AuthServiceDependency
) -> Token:
    return await auth_service.login_for_access_token(request, form_data)


@router.post("/refresh")
async def refresh_access_token(
    refresh_token_obj: RefreshToken, auth_service: AuthServiceDependency
):
    refresh_token = refresh_token_obj.refresh_token
    return await auth_service.refresh_access_token(refresh_token)
