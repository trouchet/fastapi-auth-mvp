# auth.py
from fastapi import Depends, Request, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Annotated, Tuple
from functools import wraps
from contextlib import asynccontextmanager
from time import time

from backend.app.models.auth import Token
from backend.app.base.exceptions import (
    CredentialsException, 
    PrivilegesException, 
    InexistentUsernameException,
    ExpiredTokenException,
    InactiveUserException,
    MalformedTokenException,
    MissingRequiredClaimException,
)
from backend.app.repositories.users import (
    UsersRepository, get_users_repository_cmanager, get_users_repository,
)
from backend.app.models.users import User
from backend.app.database.models.users import User
from backend.app.utils.misc import is_async

from backend.app.base.config import settings

token_url = f"{settings.API_V1_STR}/auth/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)
tokenDependency = Annotated[str, Depends(oauth2_scheme)]

JWT_ALGORITHM=settings.JWT_ALGORITHM
JWT_SECRET_KEY=settings.JWT_SECRET_KEY

DEFAULT_ACCESS_TIMEOUT_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_REFRESH_TIMEOUT_MINUTES=settings.REFRESH_TOKEN_EXPIRE_MINUTES


def create_token(
    data: dict, expires_delta: timedelta | None = DEFAULT_ACCESS_TIMEOUT_MINUTES,
):
    """
    Create a JSON Web Token (JWT) with the provided data and expiration time.
    
    Args:
        data (dict): The data to be encoded in the JWT.
        expires_delta (timedelta | None, optional): The expiration time for the JWT. 
        Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.
    
    Returns:
        str: The encoded JWT.
    
    """
    to_encode = data.copy()
    current_time = datetime.now(timezone.utc)

    # Set the expiration time
    expire = current_time + expires_delta

    time_data = {"exp": expire, "iat": datetime.now()}
    to_encode.update(time_data)

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


async def get_current_user_from_refresh_token(token: str):
    """
    Validates the refresh token and returns the current user and the token.

    Args:
        token (str): The refresh token to be validated.

    Returns:
        Tuple[User, str]: A tuple containing the current user object and the token.

    Raises:
        ExpiredTokenException: If the token has expired.
        CredentialsException: If the token is invalid or the user credentials are incorrect.
        InactiveUserException: If the user is inactive.
    """
    async with get_users_repository_cmanager() as user_repository:
        try:
            user_has_token, user = await user_repository.refresh_token_exists(token)
            
            if user_has_token:
                payload = jwt.decode(
                    token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
                )
                username: str = payload.get("sub")
                expiration_date_int = payload.get("exp")
                expiration_date = datetime.fromtimestamp(expiration_date_int)

                if expiration_date < datetime.now():
                    raise ExpiredTokenException()

                invalid_credentials = username is None or \
                    user.user_username != username
                
                if invalid_credentials:
                    raise CredentialsException()
            else:
                raise CredentialsException()

        except JWTError:
            raise ExpiredTokenException()

        current_user = await user_repository.get_user_by_username(username)

        if current_user is None:
            raise CredentialsException()

        if not current_user.user_is_active:
            raise InactiveUserException(current_user.user_username)
    print(current_user)
    return current_user


async def get_current_user(token: tokenDependency) -> User:
    """
    Retrieves the current user based on the provided token.

    Args:
        token (str): The JWT token used for authentication.

    Returns:
        User: The user object representing the current user.

    Raises:
        ExpiredTokenException: If the token has expired.
        MissingRequiredClaimException: If the 'sub' claim is missing in the token.
        CredentialsException: If the username is missing in the token.
        MalformedTokenException: If the token is malformed.
        InexistentUsernameException: If the username does not exist in the database.
        InactiveUserException: If the user is inactive.
    """
    async with get_users_repository_cmanager() as user_repository:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            if payload['exp'] <= time():
                raise ExpiredTokenException()
            
            if 'sub' in payload:
                username: str = payload.get("sub")
            else:
                raise MissingRequiredClaimException("sub")
            
            if username is None:
                raise CredentialsException()

        except JWTError:
            raise MalformedTokenException()

        # Get the user from the database
        user = await user_repository.get_user_by_username(username=username)
        
        # Check if the user exists and is active
        if user is None:
            raise InexistentUsernameException(username)

        if not user.user_is_active:
            raise InactiveUserException(user.user_username)

    return user

class AuthService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def login_for_access_token(
        self, request: Request, form_data: OAuth2PasswordBearer
    ):
        try: 
            username, password = form_data.username, form_data.password
            user = await self.user_repository.get_user_by_username(username)

            if not user:
                # TODO: Implement logging with database
                print(f"User not found: {username}")

                raise InexistentUsernameException(username=username)

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        
        is_authentic=await self.user_repository.is_user_credentials_authentic(username, password)
        
        if not is_authentic:
            raise CredentialsException()

        auth_data={
            "sub": user.user_username
        }
        access_token = create_token(
            data=auth_data, expires_delta=DEFAULT_ACCESS_TIMEOUT_MINUTES
        )
        refresh_token = create_token(
            data=auth_data, expires_delta=DEFAULT_REFRESH_TIMEOUT_MINUTES
        )

        # Update user's last login and tokens
        await self.user_repository.update_user_last_login(username)
        await self.user_repository.update_user_access_token(username, access_token)
        await self.user_repository.update_user_refresh_token(username, refresh_token)

        token=Token(access_token=access_token, refresh_token=refresh_token)

        return token
    
    async def refresh_access_token(self, refresh_token: str):
        user = await get_current_user_from_refresh_token(refresh_token)

        # Validate the refresh token
        auth_data = {"sub": user.user_username}

        # Access token 
        access_token = create_token(
            data=auth_data, expires_delta=DEFAULT_ACCESS_TIMEOUT_MINUTES
        )
        await self.user_repository.update_user_access_token(
            user.user_username, access_token
        )

        # Refresh token
        refresh_token = create_token(
            data=auth_data, expires_delta=DEFAULT_REFRESH_TIMEOUT_MINUTES
        )
        await self.user_repository.update_user_refresh_token(
            user.user_username, refresh_token
        )
        
        token=Token(access_token=access_token, refresh_token=refresh_token)
        
        return token

@asynccontextmanager
async def get_auth_service():
    async with get_users_repository_cmanager() as user_repository:
        try:
            yield AuthService(user_repository)
        finally:
            pass
    

async def get_auth_service():
    async with get_users_repository_cmanager() as user_repository:
        try:
            yield AuthService(user_repository)
        finally:
            pass


def role_checker(required_roles: Tuple[str]):
    def wrapper(func):
        @wraps(func)
        async def decorated_view(*args, current_user: User, **kwargs):
            if not current_user.has_roles(required_roles):
                raise PrivilegesException()

            if await is_async(func):
                return await func(*args, current_user=current_user, **kwargs)
            else:
                return func(*args, current_user=current_user, **kwargs)
            
        return decorated_view
    
    return wrapper

def permissions_checker(required_permissions: Tuple[str]):
    def wrapper(func):
        @wraps(func)
        async def decorated_view(*args, current_user: User, **kwargs):
            if not current_user.has_permissions(required_permissions):
                raise PrivilegesException()

            if await is_async(func):
                return await func(*args, current_user=current_user, **kwargs)
            else:
                return func(*args, **kwargs)
            
        return decorated_view
    
    return wrapper

