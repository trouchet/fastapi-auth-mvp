# auth.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Annotated
from functools import wraps

from backend.app.constants import DEFAULT_ACCESS_TIMEOUT_MINUTES

from backend.app.exceptions import (
    CredentialsException,
    PrivilegesException,
    InexistentUsernameException,
    ExpiredTokenException,
    InactiveUserException,
)
from backend.app.repositories.users import (
    get_user_repo,
)
from backend.app.models.users import User
from backend.app.database.models.users import UserDB

from backend.app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


async def validate_refresh_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        user_repo = get_user_repo()

        user_has_token, user = user_repo.refresh_token_exists(token)

        if user_has_token:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            username: str = payload.get("sub")
            roles: str = payload.get("roles")
            expiration_date_int = payload.get("exp")

            expiration_date = datetime.fromtimestamp(expiration_date_int)

            if expiration_date < datetime.now():
                raise ExpiredTokenException()

            empty_entry = username is None or roles is None

            if empty_entry or user.user_username != username:
                raise CredentialsException()
        else:
            raise CredentialsException()

    except JWTError:
        raise ExpiredTokenException()

    current_user = user_repo.get_user_by_username(username)

    if current_user is None:
        raise CredentialsException()

    if not current_user.user_is_active:
        raise InactiveUserException(current_user.user_username)

    return current_user, token


# Function to get the user from the database
async def get_user(username: str) -> UserDB | None:
    user_repository = get_user_repo()
    user = await user_repository.get_user_by_username(username)

    if not user:
        return

    return user


def create_token(
    data: dict, expires_delta: timedelta | None = DEFAULT_ACCESS_TIMEOUT_MINUTES
):
    to_encode = data.copy()
    current_time = datetime.now(timezone.utc)

    # Set the expiration time
    expire = current_time + expires_delta

    time_data = {"exp": expire, "iat": datetime.now()}
    to_encode.update(time_data)

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user_repo = get_user_repo()

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise CredentialsException()

    except JWTError:
        raise CredentialsException()

    # Get the user from the database
    user = user_repo.get_user_by_username(username=username)

    if user is None:
        raise InexistentUsernameException(username)

    if not user.user_is_active:
        raise InactiveUserException(user.user_username)

    return user


# Decorator to check the role
def role_checker(allowed_roles):
    def wrapper(func):
        @wraps(func)
        async def decorated_view(
            *args, current_user: User = Depends(get_current_user), **kwargs
        ):
            current_user = await get_current_user()

            user_roles_set = set(current_user.roles)
            allowed_roles_set = set(allowed_roles)

            user_has_permission = not user_roles_set.isdisjoint(allowed_roles_set)

            if not user_has_permission:
                raise PrivilegesException()

            return await func(*args, **kwargs)

        return decorated_view

    return wrapper
