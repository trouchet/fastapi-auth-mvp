from fastapi import APIRouter

from backend.app.routes import (
    auth_router,
    data_router,
    public_router,
    users_router,
    system_router,
)
from backend.app.core.config import settings

# Include all routers in the API
routers = [
    public_router,
    system_router,
    auth_router,
    data_router,
    users_router,
]

prefix = f"{settings.API_V1_STR}"

api_router = APIRouter()

for router in routers:
    api_router.include_router(router, prefix=prefix)