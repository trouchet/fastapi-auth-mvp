from fastapi import APIRouter, Depends

from backend.app.core.auth import role_checker
from backend.app.core.auth import get_current_user
from backend.app.models.users import User

router = APIRouter(
    tags=["data"],
)


@router.get("/data/admin")
@role_checker(["admin"])
def admin_endpoint():
    return {"message": "admin data"}


@router.get("/data/user")
@role_checker(["admin", "user"])
def admin_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": "This is user data"}
