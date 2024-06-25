from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_csrf_protect import CsrfProtect

from backend.app.routes import (
    auth_router, data_router, misc_router, users_router,
)
from backend.app.core.config import settings
from backend.app.models.auth import CsrfSettings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    summary=settings.DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Include routers in the app
prefix=f"{settings.API_V1_STR}"

app.include_router(auth_router, prefix=prefix)
app.include_router(misc_router, prefix=prefix)
app.include_router(data_router, prefix=prefix)
app.include_router(users_router, prefix=prefix)

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# Add static files
obj = StaticFiles(directory="backend/static")
app.mount("/static", obj, name="static")

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("backend/static/fastapi.svg")

@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc: HTTPException):
    """Redirects to docs or redoc on 404 Not Found."""
    # Choose between docs or redoc based on your preference
    redirect_url = f"{settings.API_V1_STR}/docs"  # Or "/redoc"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

