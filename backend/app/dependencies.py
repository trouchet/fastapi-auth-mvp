from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from auth import (
    RoleChecker, 
    validate_refresh_token,
    get_current_user,
)
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

RoleDependency=Annotated[bool, Depends(RoleChecker(allowed_roles=["admin"]))]
PasswordDependency=Annotated[OAuth2PasswordRequestForm, Depends()]
AuthDependency=Annotated[str, Depends(oauth2_scheme)]
RefreshTokenDependency=Annotated[tuple[User, str], Depends(validate_refresh_token)]
CurrentUserDependency=Annotated[User, Depends(get_current_user)]
