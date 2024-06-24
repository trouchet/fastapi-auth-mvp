from fastapi import APIRouter

from backend.app.auth import role_checker

router=APIRouter(
    tags=["data"],
)

@router.get("/data/admin")
@role_checker(["admin"])
def admin_endpoint():
    return {"message": "admin data"}

@router.get("/data/user")
@role_checker(["admin", "user"])
def admin_endpoint():
    return {"message": "user data"}