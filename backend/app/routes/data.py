from fastapi import APIRouter, Depends

from backend.app.models.users import User
from backend.app.core.auth import role_checker, get_current_user


router=APIRouter(prefix='/data', tags=["Data"])

@router.get("/admin-data")
@role_checker(["admin"])
def admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": "This is admin data"}

@router.get("/user-data")
@role_checker(["admin", "user"])
def admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": "This is user data"}
