from .auth import router as auth_router
from .data import router as data_router
from .public import router as public_router
from .users import router as users_router
from .system import router as system_router
from .health import router as health_router

__all__ = [
    "public_router",
    "health_router",
    "auth_router",
    "data_router",
    "users_router",
    "system_router"
]
