from fastapi import Depends
from typing import Annotated 

from backend.app.repositories.users import UsersRepository, get_user_repository

UsersRepositoryDepends = Annotated[UsersRepository, Depends(get_user_repository)]
