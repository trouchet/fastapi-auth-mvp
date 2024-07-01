from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from backend.app.middlewares.throttling import init_rate_limiter
from backend.app.routes.bundler import api_router
from backend.app.core.config import settings
from backend.app.middlewares.request import RequestLoggingMiddleware
from backend.app.scheduler.bundler import start_schedulers
from backend.app.database.instance import database
from backend.app.database.initial_data import insert_initial_data
from backend.app.middlewares.bundler import middlewares

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_rate_limiter(app)
    await start_schedulers()
    insert_initial_data(database)

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

# Middlewares
for middleware in middlewares:
    app.add_middleware(middleware)

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
