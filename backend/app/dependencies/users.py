from fastapi import Depends

from backend.app.repositories.users import get_user_repository

UsersRepositoryDepends = Depends(get_user_repository)