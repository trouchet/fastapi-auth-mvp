#auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer 
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from jose import JWTError, jwt
from typing import Annotated
from dotenv import load_dotenv
from os import getenv

from backend.app.exceptions import (
    CredentialsException, 
    PrivilegesException, 
    InexistentUsernameException,
)
from backend.app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for encoding and decoding JWT
load_dotenv('.env')

SECRET_KEY = getenv("SECRET_KEY", 'secret12345')
ALGORITHM = getenv("ALGORITHM", 'HS256')

# Function to get the user from the database
# NOTE: Provided database is a list of dictionaries. 
# Change implementation to actual database call
def get_user(database, username: str):
    for user in database:
        if user["username"] == username:
            return User(**user)

    return None


def authenticate_user(database, username: str, plain_password: str):
    user = get_user(database, username)
    
    if not user:
        return False
    
    is_password_correct = pwd_context.verify(plain_password, user.hashed_password)
    if not is_password_correct:
        return False 
    
    return user


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    current_time=datetime.now(timezone.utc)

    # Set the expiration time
    extra_time = expires_delta if expires_delta else timedelta(minutes=15)
    expire = current_time + extra_time

    to_encode.update(
        {   
            "exp": expire,
            "iat": datetime.now()
        }
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


TokenDependency=Annotated[str, Depends(oauth2_scheme)]
async def get_current_user(users_db, token: TokenDependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")

        if username is None:
            raise CredentialsException()

    except JWTError:
        raise CredentialsException()

    # Get the user from the database
    user = get_user(users_db, username=username)

    if user is None:
        raise InexistentUsernameException()

    return user


async def validate_refresh_token(
    users_db, refresh_tokens, 
    token: TokenDependency):
    unauthorized_code=status.HTTP_401_UNAUTHORIZED
    credentials_exception = HTTPException(
        status_code=unauthorized_code, 
        detail="Could not validate credentials"
    )

    try:
        if token in refresh_tokens:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            
            empty_entry=username is None or role is None
            
            if empty_entry:
                raise CredentialsException()
        else:
            raise CredentialsException()

    except (JWTError, ValidationError):
        raise CredentialsException()

    user = get_user(users_db, username=username)

    if user is None:
        raise CredentialsException()

    return user, token


# Dependency for checking the role
UserDependency=Annotated[User, Depends(get_current_user)]
def get_current_active_user(current_user: UserDependency):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

# Dependency for current user
CurrentUserDependency=Annotated[User, Depends(get_current_active_user)]
class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: CurrentUserDependency):
        if user.role in self.allowed_roles:
            return True

        raise PrivilegesException()