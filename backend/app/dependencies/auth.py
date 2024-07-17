from typing import Annotated, Tuple
from fastapi import Depends

from backend.app.models.users import User
from backend.app.services.auth import (
    AuthService, get_auth_service,
)
from backend.app.services.auth import get_current_user
from backend.app.repositories.auth import (
    RoleRepository, get_role_repository,
)

CurrentUserDependency = Annotated[
    User, Depends(get_current_user)
]

AuthServiceDependency = Annotated[
    AuthService, Depends(get_auth_service)
]

RoleRepositoryDependency = Annotated[
    RoleRepository, Depends(get_role_repository)
]