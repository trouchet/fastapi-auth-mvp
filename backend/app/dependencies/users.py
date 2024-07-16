from fastapi import Depends

from backend.app.repositories.users import get_users_repository

UsersRepositoryDepends = Depends(get_users_repository)