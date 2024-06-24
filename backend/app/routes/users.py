from fastapi import APIRouter, Depends
from typing import List, Dict

from backend.app.repositories.users import get_user_repo
from backend.app.database.models.users import UserDB
from backend.app.repositories.users import UsersRepository
from backend.app.exceptions import (
    InexistentUserIDException,
    InactiveUserException,
    CredentialsException,
)
from backend.app.models.users import UpdateUser

router = APIRouter(tags=["users"])


def userbd_to_user(user: UserDB):
    return {
        "user_id": user.user_id,
        "user_created_at": user.user_created_at,
        "user_updated_at": user.user_updated_at,
        "user_username": user.user_username,
        "user_email": user.user_email,
        "user_roles": user.user_roles,
        "user_is_active": user.user_is_active,
    }


@router.get("/")
def read_user(
    limit: int = 10,
    offset: int = 0,
    user_repo: UsersRepository = Depends(get_user_repo),
) -> List[Dict]:
    users = user_repo.get_users(limit=limit, offset=offset)

    return list(map(userbd_to_user, users))


@router.get("/{user_id}")
def read_user_by_id(user_id: str, user_repo: UsersRepository = Depends(get_user_repo)):
    user = user_repo.get_user_by_id(user_id)

    return userbd_to_user(user)


@router.delete("/{user_id}")
def delete_user(user_id: str, user_repo: UsersRepository = Depends(get_user_repo)):
    user_repo.delete_user_by_id(user_id)


@router.patch("/{user_id}")
def update_user(
    user_id: str, user: UpdateUser, user_repo: UsersRepository = Depends(get_user_repo)
) -> Dict:
    user = user_repo.update_user(user_id, user)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/username")
def update_username(
    user_id: str, new_username: str, user_repo: UsersRepository = Depends(get_user_repo)
) -> Dict:
    user = user_repo.update_user_username(user_id, new_username)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/email")
def update_email(
    user_id: str, new_email: str, user_repo: UsersRepository = Depends(get_user_repo)
) -> Dict:
    user = user_repo.update_user_email(user_id, new_email)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/password")
def update_password(
    user_id: str,
    old_password: str,
    new_password: str,
    user_repo: UsersRepository = Depends(get_user_repo),
) -> Dict:
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise InexistentUserIDException(user_id)

    if not user.user_is_active:
        raise InactiveUserException(user.user_username)

    is_authentic = user_repo.is_user_credentials_authentic(
        user.user_username, old_password
    )

    if not is_authentic:
        raise CredentialsException()
    else:
        user = user_repo.update_user_password(user_id, new_password)

    return userbd_to_user(user)


@router.patch("/{user_id}/activate")
def activate_user(
    user_id: str, user_repo: UsersRepository = Depends(get_user_repo)
) -> Dict:
    user = user_repo.update_user_active_status(user_id)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: str, user_repo: UsersRepository = Depends(get_user_repo)
) -> Dict:
    user = user_repo.activate_user(user_id)

    if not user:
        raise InexistentUserIDException(user_id)
    else:
        return userbd_to_user(user)


@router.get("/role/{role}")
def read_users_by_role(
    role: str, user_repo: UsersRepository = Depends(get_user_repo)
) -> List[Dict]:
    users = user_repo.get_users_by_role(role)

    return list(map(userbd_to_user, users))
