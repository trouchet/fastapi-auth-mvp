from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from typing import List, Dict
from uuid import uuid4
from passlib.context import CryptContext
from datetime import datetime

from typing import List, Dict
from uuid import uuid4
from passlib.context import CryptContext

from backend.app.core.auth import role_checker
from backend.app.repositories.users import get_user_repo
from backend.app.database.models.users import UserDB
from backend.app.repositories.users import UsersRepository
from backend.app.core.exceptions import (
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
from backend.app.models.users import User, UpdateUser, CreateUser
from backend.app.core.auth import get_current_user

from backend.app.utils.security import (
    is_password_valid, 
    apply_password_validity_dict, 
    is_email_valid,
    is_valid_uuid,
    hash_string,
)

router = APIRouter(prefix='/users', tags=["users"])


def userbd_to_user(user: UserDB):
    return {
        "user_id": user.user_id,
        "user_created_at": user.user_created_at,
        "user_updated_at": user.user_updated_at,
        "user_username": user.user_username,
        "user_email": user.user_email,
        "user_is_active": user.user_is_active,
    }


@router.get("/")
@role_checker(["admin"])
def read_all_users(
    current_user: User = Depends(get_current_user),
    user_repo: UsersRepository=Depends(get_user_repo),
    limit: int = 10,
    offset: int = 0
) -> List[Dict]:
    users = user_repo.get_users(limit=limit, offset=offset)

    return list(map(userbd_to_user, users))


@router.get("/{user_id}")
@role_checker(["admin", "user"])
def read_user_by_id(
    current_user: User = Depends(get_current_user),
    user_id: str = Path(..., description="The ID of the user to retrieve"),
    user_repo: UsersRepository=Depends(get_user_repo)
):
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    user = user_repo.get_user_by_id(user_id)
    
    if not user:
        raise InexistentUserIDException(user_id)

    return userbd_to_user(user)


@router.delete("/{user_id}")
@role_checker(["admin"])
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    user_repo: UsersRepository=Depends(get_user_repo)
):
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    user=user_repo.get_user_by_id(user_id)

    if not user:
        raise InexistentUserIDException(user_id)

    admin_users=user_repo.get_users_by_role("admin")
    last_admin=len(admin_users)==1
    last_admin_candidate = admin_users[0]
    this_last_admin=str(last_admin_candidate.user_id)==user_id
    
    forbidden_remove_last_admin=last_admin and this_last_admin

    if forbidden_remove_last_admin:
        raise LastAdminRemovalException()

    user_repo.delete_user_by_id(user_id)
    
    return JSONResponse(
        content=jsonable_encoder({"message": f"User {user_id} deleted successfully"}),
    )


@router.patch("/{user_id}")
@role_checker(["admin", "user"])
def update_user(
    user_id: str, user: UpdateUser, user_repo: UsersRepository = Depends(get_user_repo)
) -> Dict:

    if not user:
        raise InexistentUserIDException(user_id)

    admin_users=user_repo.get_users_by_role("admin")
    last_admin=len(admin_users)==1
    last_admin_candidate = admin_users[0]
    this_last_admin=last_admin_candidate.user_id==user_id

    forbidden_remove_last_admin=last_admin and this_last_admin

    if forbidden_remove_last_admin:
        raise LastAdminRemovalException()

    user_repo.delete_user_by_id(user_id)
    
    return JSONResponse(
        content=jsonable_encoder({"message": f"User {user_id} deleted successfully"}),
    )


@router.put("/")
@role_checker(["admin", "user"])
def create_user(
    user: CreateUser,
    current_user: User = Depends(get_current_user),
    user_repo: UsersRepository=Depends(get_user_repo)
) -> Dict:
    # Check if the username already exists
    user_db = user_repo.get_user_by_username(user.user_username)
    
    if user_db:
        raise ExistentUsernameException(user.user_username)
    
    # Check 
    user_db = user_repo.get_user_by_email(user.user_email)
    
    if user_db:
        raise ExistentEmailException(user.user_email)
    
    password=user.user_password
    
    if not is_password_valid(password):
        invalidation_dict=apply_password_validity_dict(password)
        raise InvalidPasswordException(invalidation_dict)

    new_user = UserDB(
        user_username=user.user_username,
        user_hashed_password=hash_string(user.user_password),
        user_email=user.user_email,
    )
    
    user_repo.create_user(new_user)

    return userbd_to_user(new_user)


@router.patch("/{user_id}")
@role_checker(["admin", "user"])
def update_user(
    user_id: str,
    user: UpdateUser,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> Dict:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    user = user_repo.update_user(user_id, user)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/username")
@role_checker(["admin", "user"])
def update_username(
    user_id: str,
    new_username: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> Dict:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    user = user_repo.update_user_username(user_id, new_username)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/email")
@role_checker(["admin", "user"])
def update_email(
    user_id: str, 
    new_email: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> Dict:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    if not is_email_valid(new_email):
        raise InvalidEmailException(new_email)
    
    user = user_repo.update_user_email(user_id, new_email)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/password")
@role_checker(["admin", "user"])
def update_password(
    user_id: str,
    old_password: str,
    new_password: str,
    user_repo: UsersRepository = Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> Dict:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    if not is_password_valid(new_password):
        invalidation_dict=apply_password_validity_dict(new_password)
        raise InvalidPasswordException(invalidation_dict)

    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise InexistentUserIDException(user_id)

    if not user.user_is_active:
        raise InactiveUserException(user.user_username)

    is_authentic=user_repo.is_user_credentials_authentic(user.user_username, old_password)

    if(is_authentic):
        user = user_repo.update_user_password(user_id, new_password)
    else:
        raise IncorrectCurrentPasswordException()

    return userbd_to_user(user)


@router.get("/{user_id}/roles")
@role_checker(["admin", "user"])
def get_user_roles(
    user_id: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> List[str]:
    return user_repo.get_user_roles(user_id)


@router.get("/{user_id}/roles")
@role_checker(["admin"])
def get_user_roles(
    user_id: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> List[str]:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    roles=user_repo.get_user_roles(user_id)
    
    if not roles:
        raise InexistentUserIDException(user_id) 
    else:
        return roles


@router.patch("/{user_id}/activate")
@role_checker(["admin"])
def activate_user(
    user_id: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> Dict:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    user = user_repo.update_user_active_status(user_id)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/deactivate")
@role_checker(["admin"])
def deactivate_user(
    user_id: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> Dict:
    if not is_valid_uuid(user_id): 
        raise InvalidUUIDException(user_id)
    
    user = user_repo.activate_user(user_id)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.get("/role/{role}")
@role_checker(["admin"])
def get_users_by_role(
    role: str,
    user_repo: UsersRepository=Depends(get_user_repo),
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    users = user_repo.get_users_by_role(role)

    return list(map(userbd_to_user, users))


