from typing import Annotated, Tuple
from fastapi import Depends
from backend.app.base.auth import validate_refresh_token

from backend.app.models.users import User
from backend.app.repositories.auth import get_role_repository

RefreshTokenDependency = Annotated[
    Tuple[User, str], Depends(validate_refresh_token)
]

RoleRepositoryDepends = Depends(get_role_repository)
