from fastapi.middleware.cors import CORSMiddleware

from .request import RequestLoggingMiddleware
from backend.app.middlewares.throttling import RateLimitMiddleware
from backend.app.core.auth import get_current_user
from backend.app.core.config import settings

middlewares = [
    RequestLoggingMiddleware(),
    RateLimitMiddleware(
        identifier_callable=get_current_user
    )
]

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    cors_middleware = CORSMiddleware(
        allow_origins=[
            str(origin).strip("/") 
            for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    middlewares.append(cors_middleware)