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

from backend.app.data import refresh_tokens, fake_users_db
from backend.app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for encoding and decoding JWT
load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")

def get_user(database, username: str):
    for user in database:
        if user["username"] == username:
            return User(**user)

    return None


def authenticate_user(database, username: str, plain_password: str):
    user = get_user(database, username)    
    hashed_password = user.hashed_password
    
    user_not_found=not user
    is_password_wrong=not pwd_context.verify(plain_password, hashed_password)
    
    invalid_authentication=user_not_found or is_password_wrong
    
    return None if invalid_authentication else user


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=username)
    
    if user is None:
        raise credentials_exception
    
    return user

# Dependency for checking the role
UserDependency=Annotated[User, Depends(get_current_user)]

async def get_current_active_user(current_user: UserDependency):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


# Dependency for checking the refresh token
TokenValidatorDependency=Annotated[str, Depends(oauth2_scheme)]

async def validate_refresh_token(token: TokenValidatorDependency):
    unauthorized_code=status.HTTP_401_UNAUTHORIZED
    credentials_exception = HTTPException(
        status_code=unauthorized_code, 
        detail="Could not validate credentials")

    try:
        if token in refresh_tokens:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            
            if username is None or role is None:
                raise credentials_exception
        else:
            raise credentials_exception

    except (JWTError, ValidationError):
        raise credentials_exception

    user = get_user(fake_users_db, username=username)

    if user is None:
        raise credentials_exception

    return user, token

# Dependency for current user
CurrentUserDependency=Annotated[User, Depends(get_current_active_user)]

class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: CurrentUserDependency):
        if user.role in self.allowed_roles:
            return True

        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="You don't have enough permissions"
            )