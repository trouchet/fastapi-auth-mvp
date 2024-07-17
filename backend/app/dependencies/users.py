from fastapi import Depends
from typing import Annotated

from backend.app.repositories.users import (
    get_users_repository, UsersRepository,
)
from backend.app.services.users import (
    get_users_service, UserService,
)

UsersRepositoryDependency = Annotated[
    UsersRepository, Depends(get_users_repository)
]

UsersServiceDependency=Annotated[
    UserService, Depends(get_users_service)
]

