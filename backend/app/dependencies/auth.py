from typing import Annotated, Tuple
from fastapi import Depends
from backend.app.services.auth import (
    get_current_user, validate_refresh_token,
)
from backend.app.base.exceptions import JWTInvalidException

from backend.app.models.users import User
from backend.app.repositories.auth import RoleRepository
from backend.app.repositories.auth import get_role_repository

RefreshTokenDependency = Annotated[
    Tuple[User, str], Depends(validate_refresh_token)
]

RoleRepositoryDependency = Annotated[
    RoleRepository, Depends(get_role_repository)
]

CurrentUserDependency = Annotated[
    User, Depends(get_current_user)
]

