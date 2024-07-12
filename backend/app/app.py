from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from backend.app.middlewares.request import RequestLoggingMiddleware
from backend.app.middlewares.throttling import RateLimitMiddleware
from backend.app.middlewares.throttling import init_rate_limiter
from backend.app.middlewares.bundler import add_middlewares
from backend.app.routes.bundler import api_router
from backend.app.base.auth import get_current_user
from backend.app.base.logging import logger
from backend.app.scheduler.bundler import start_schedulers

from backend.app.database.instance import init_database
from backend.app.database.initial_data import insert_initial_data

from backend.app.middlewares.bundler import add_middlewares
from backend.app.base.config import settings, is_docker

@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Database initialization
    await init_database()
    await insert_initial_data()
    
    # Rate limiter initialization
    if is_docker(settings.ENVIRONMENT): 
        await init_rate_limiter()
    
    # Start the schedulers
    start_schedulers()
    
    yield

def create_app():
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

    @app.get("/favicon.ico")
    async def get_favicon():
        return FileResponse("backend/static/fastapi.svg")
    
    return app

def configure_app(app_: FastAPI):

    # Add static files
    obj = StaticFiles(directory="backend/static")
    app_.mount("/static", obj, name="static")

    # Add exception handlers
    @app_.exception_handler(status.HTTP_404_NOT_FOUND)
    async def not_found_handler(request: Request, exc: HTTPException):
        warning_msg=f"The requested resource could not be found."
        suggestion_msg=f"Refer to the API documentation at {settings.API_V1_STR}/docs for available endpoints."
        return JSONResponse(
            f"{warning_msg} {suggestion_msg}",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app_.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handles all uncaught exceptions."""
        # Log the exception details
        logger.error(f"Unhandled exception: {exc}")

        # Return a generic error response to the client
        code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(f"An unexpected error occurred: {exc}.", status_code=code)
    
    # Include routers in the app
    app_.include_router(api_router)

    # Add middlewares
    add_middlewares(app_)
    
def init_app():
    # Get the number of applications from the environment variable
    app = create_app()

    # Setup the application
    configure_app(app)

    return app


# Initialize the application
app = init_app()