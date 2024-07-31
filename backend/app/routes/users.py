from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import List, Dict, Annotated

from backend.app.services.auth import role_checker
from backend.app.dependencies.auth import CurrentUserDependency

from backend.app.database.models.users import User
from backend.app.repositories.users import UsersRepository
from backend.app.base.exceptions import (
    InexistentUserIDException,
    InactiveUserException,
    IncorrectCurrentPasswordException,
    LastAdminRemovalException,
    InvalidEmailException,
    InvalidUUIDException,
    InvalidPasswordException,
)
from backend.app.models.users import User, UnhashedUpdateUser, CreateUser
from backend.app.utils.security import (
    is_password_valid, 
    apply_password_validity_dict, 
    is_email_valid,
    is_valid_uuid,
)
from backend.app.dependencies.users_service import UsersServiceDependency
from backend.app.services.auth import get_current_user

from backend.app.utils.security import hash_string
from .roles_bundler import (
    user_management_roles,
    user_viewer_roles,
    user_editor_roles,
)

router = APIRouter(prefix='/users', tags=["Users"])

def userbd_to_user(user: User):
    return {
        "user_id": user.user_id,
        "user_created_at": user.user_created_at,
        "user_updated_at": user.user_updated_at,
        "user_username": user.user_username,
        "user_email": user.user_email,
        "user_is_active": user.user_is_active,
    }


@router.get("/")
@role_checker(user_management_roles)
async def read_all_users(
    user_service: UsersServiceDependency,
    current_user: CurrentUserDependency,
    limit: int = 10,
    offset: int = 0
) -> List[Dict]:
    return await user_service.get_users(limit=limit, offset=offset)


@router.get("/me")
async def get_me(current_user: CurrentUserDependency):
    return current_user

@router.get("/{user_id}")
@role_checker(user_viewer_roles)
async def read_user_by_id(
    user_id: str,
    user_service: UsersServiceDependency,
    current_user: CurrentUserDependency
):
    return await user_service.get_user_by_id(user_id)


@router.delete("/{user_id}")
@role_checker(user_management_roles)
async def delete_user(
    user_id: str,
    user_service: UsersServiceDependency,
    current_user: CurrentUserDependency
):
    return await user_service.delete_user(user_id)


@router.patch("/{user_id}")
@role_checker(user_management_roles)
async def update_user(
    user_id: str, 
    update_user_info: UnhashedUpdateUser,
    users_service: UsersServiceDependency
) -> Dict:
    return await users_service.update_user(user_id, update_user_info)


@router.put("/")
@role_checker(user_management_roles)
async def create_user(
    new_user: CreateUser,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> Dict:
    return await users_service.create_user(new_user)

@router.post('/signup')
async def signup(
    new_user_info: CreateUser,
    users_service: UsersServiceDependency,
) -> Dict:
    return await users_service.create_user(new_user_info)


@router.patch("/{user_id}")
@role_checker(user_editor_roles)
async def update_user(
    user_id: str,
    user: UnhashedUpdateUser,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> Dict:
    return await users_service.update_user(user_id, user)


@router.patch("/{user_id}/username")
@role_checker(user_editor_roles)
async def update_username(
    user_id: str,
    new_username: str,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> Dict:
    return await users_service.update_user_username(user_id, new_username)


@router.patch("/{user_id}/email")
@role_checker(user_editor_roles)
async def update_email(
    user_id: str, 
    new_email: str,
    users_service: UsersServiceDependency,
    current_user: User = CurrentUserDependency
) -> Dict:
    return await users_service.update_email(user_id, new_email)


@router.patch("/{user_id}/password")
@role_checker(user_editor_roles)
async def update_password(
    user_id: str,
    old_password: str,
    new_password: str,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> Dict:
    return await users_service.update_password(user_id, old_password, new_password)

@router.get("/{user_id}/roles")
@role_checker(user_viewer_roles)
async def get_user_roles_by_id(
    user_id: str,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> List[str]:
    return await users_service.get_user_roles_by_id(user_id)


@router.patch("/{user_id}/activate")
@role_checker(user_editor_roles)
async def activate_user(
    user_id: str,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> Dict:
    return await users_service.activate_user(user_id)


@router.patch("/{user_id}/deactivate")
@role_checker(user_editor_roles)
async def deactivate_user(
    user_id: str,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency
) -> Dict:
    return await users_service.deactivate_user(user_id)


@router.get("/role/{role}")
@role_checker(user_management_roles)
async def get_users_by_role(
    role: str,
    users_service: UsersServiceDependency,
    current_user: CurrentUserDependency,
    limit: int = 10,
    offset: int = 0
) -> List[Dict]:
    return await users_service.get_users_by_role(role)

