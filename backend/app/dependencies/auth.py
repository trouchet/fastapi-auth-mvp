from typing import Annotated, Tuple

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends


from backend.app.base.auth import validate_refresh_token
from backend.app.models.users import User
from backend.app.repositories.auth import get_role_repository, RoleRepository
from backend.app.services.auth import JWTService

OAuthDependency = Annotated[
    OAuth2PasswordRequestForm, Depends()
]

RefreshTokenDependency = Annotated[
    Tuple[User, str], Depends(validate_refresh_token)
]

RoleRepositoryDependency = Annotated[
    RoleRepository, Depends(get_role_repository)
]

CurrentUserDependency=Annotated[
    User, Depends(JWTService.get_current_user)
]