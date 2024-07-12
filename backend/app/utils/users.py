from fastapi import Depends
from typing import Dict

from backend.app.repositories.users import get_user_repository, UsersRepository
from backend.app.database.models.users import UserDB
from backend.app.models.users import CreateUser
from backend.app.utils.security import (
    is_password_valid, 
    apply_password_validity_dict, 
    is_email_valid,
    is_valid_uuid,
)
from backend.app.base.exceptions import (
    InexistentUserIDException,
    InactiveUserException,
    IncorrectCurrentPasswordException,
    ExistentUsernameException,
    ExistentEmailException,
    LastAdminRemovalException,
    InvalidPasswordException,
    InvalidEmailException,
    InvalidUUIDException,
    InvalidPasswordException,
)
from backend.app.utils.security import hash_string

def userbd_to_user(user: UserDB):
    return {
        "user_id": user.user_id,
        "user_created_at": user.user_created_at,
        "user_updated_at": user.user_updated_at,
        "user_username": user.user_username,
        "user_email": user.user_email,
        "user_is_active": user.user_is_active,
    }

async def create_new_user(
    user: CreateUser, user_repo: UsersRepository = Depends(get_user_repository)
) -> Dict:
    # Check if the username already exists
    user_db = user_repo.get_user_by_username(user.user_username)
    if user_db:
        raise ExistentUsernameException(user.user_username)

    # Check if email already exists
    user_db = user_repo.get_user_by_email(user.user_email)
    if user_db:
        raise ExistentEmailException(user.user_email)

    # Validate password
    password = user.user_password
    if not is_password_valid(password):
        invalidation_dict = apply_password_validity_dict(password)
        raise InvalidPasswordException(invalidation_dict)

    # Create new user
    new_user = UserDB(
        user_username=user.user_username,
        user_hashed_password=hash_string(user.user_password),
        user_email=user.user_email,
    )
    user_repo.create_user(new_user)

    return userbd_to_user(new_user)