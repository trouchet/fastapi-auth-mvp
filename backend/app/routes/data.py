from fastapi import APIRouter

from backend.app.auth import role_checker

router=APIRouter()

@router.get("/data/admin")
@role_checker(["admin"])
def admin_endpoint():
    return {"data": "This is admin data"}

@router.get("/data/user")
@role_checker(["user"])
def admin_endpoint():
    return {"data": "This is user data"}