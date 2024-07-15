from fastapi import APIRouter, Depends
import toml

from backend.app.base.auth import role_checker, get_current_user
from backend.app.base.config import settings
from .roles_bundler import system_management_roles
from backend.app.models.users import User

router=APIRouter(prefix='/system', tags=["Super Admin"])

@router.get("/")
async def info():
    with open("pyproject.toml", "r", encoding="latin-1") as f:
        config = toml.load(f)

    return {
        "name": config["tool"]["poetry"]["name"],
        "version": config["tool"]["poetry"]["version"],
        "description": config["tool"]["poetry"]["description"],
    }


@router.get("/credentials")
@role_checker(system_management_roles)
async def get_credentials(
    current_user: User = Depends(get_current_user)
):
    settings_dict = settings.model_dump()

    # Anonymize secret keys
    for key in settings_dict:
        if key.endswith("KEY"):
            settings_dict[key] = "********" 

    return settings_dict

