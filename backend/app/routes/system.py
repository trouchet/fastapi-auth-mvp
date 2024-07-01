from fastapi import APIRouter

from backend.app.core.auth import role_checker
from backend.app.core.config import settings

router=APIRouter(prefix='/system', tags=["Superadmin"])

@router.get("/credentials")
@role_checker(["SuperAdmin"])
async def get_credentials():
    settings_dict = settings.model_dump()

    # Anonymize secret keys
    for key in settings_dict:
        if key.endswith("KEY"):
            settings_dict[key] = "********" 

    return settings_dict

