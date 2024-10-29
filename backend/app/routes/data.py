from fastapi import APIRouter, Depends

from backend.app.models.users import User
from backend.app.services.auth import role_checker
from backend.app.dependencies.auth import CurrentUserDependency

from .roles_bundler import (
    user_management_roles,
    user_viewer_roles,
)

router=APIRouter(prefix='/data', tags=["Data"])

@router.get("/test-admin")
@role_checker(user_management_roles)
def admin_endpoint(
    current_user: CurrentUserDependency
):
    return {"message": "This is admin data"}


@router.get("/test-viewer")
@role_checker(user_viewer_roles)
def admin_endpoint(
    current_user: CurrentUserDependency
):
    return {"message": "This is user data"}
