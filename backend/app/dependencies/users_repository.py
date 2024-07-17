from fastapi import Depends
from typing import Annotated 

from backend.app.repositories.users import (
    get_users_repository, UsersRepository,
)

UsersRepositoryDependency = Annotated[
    UsersRepository, Depends(get_users_repository)
]
