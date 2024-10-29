from fastapi import Depends
from typing import Annotated

from backend.app.repositories.users import UsersRepository, get_users_repository

UsersRepositoryDependency = Annotated[
    UsersRepository, Depends(get_users_repository)
]
