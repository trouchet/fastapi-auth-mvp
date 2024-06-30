from fastapi import APIRouter, Depends

from backend.app.models.users import User
from backend.app.core.auth import role_checker, get_current_user
from .roles_bundler import (
    user_management_roles,
    user_viewer_roles,
)

router=APIRouter(prefix='/data', tags=["Data"])

@router.get("/admin")
@role_checker(user_management_roles)
def admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": "This is admin data"}


@router.get("/public")
@role_checker(user_viewer_roles)
def admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": "This is user data"}

