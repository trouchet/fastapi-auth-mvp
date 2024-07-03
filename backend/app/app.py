from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from backend.app.middlewares.request import RequestLoggingMiddleware
from backend.app.middlewares.throttling import init_rate_limiter
from backend.app.middlewares.throttling import RateLimitMiddleware
from backend.app.middlewares.bundler import add_middlewares
from backend.app.routes.bundler import api_router
from backend.app.core.config import settings
from backend.app.core.auth import get_current_user
from backend.app.scheduler.bundler import start_schedulers
from backend.app.database.initial_data import insert_initial_data
from backend.app.middlewares.bundler import add_middlewares
from backend.app.core.config import settings, is_docker

@asynccontextmanager
async def lifespan(app: FastAPI):
    if is_docker(settings.ENVIRONMENT): 
        await init_rate_limiter()
    
    start_schedulers()
    insert_initial_data()
    yield

# Create the FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    summary=settings.DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Include routers in the app
app.include_router(api_router)

# Add middlewares
add_middlewares(app)

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
