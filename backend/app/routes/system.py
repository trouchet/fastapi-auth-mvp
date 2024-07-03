from fastapi import APIRouter

from backend.app.core.auth import role_checker
from backend.app.core.config import settings
from .roles_bundler import system_management_roles

router=APIRouter(prefix='/system', tags=["Super Admin"])

@router.get("/credentials")
@role_checker(system_management_roles)
async def get_credentials():
    settings_dict = settings.model_dump()

    # Anonymize secret keys
    for key in settings_dict:
        if key.endswith("KEY"):
            settings_dict[key] = "********" 

    return settings_dict

