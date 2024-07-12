from fastapi import Request, FastAPI, HTTPException, status
from typing import Awaitable
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

class RouteValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.app = app
    
    async def dispatch(self, request: Request, call_next):
        actual_app = self.app.app if hasattr(self.app, 'app') else self.app
        normalize_map = lambda route_path: route_path.rstrip('/') 
        
        normalized_route_path = normalize_map(request.url.path)

        # Get all available routes
        available_routes = [route.path for route in actual_app.routes]

        available_routes=list(map(normalize_map, available_routes))

        # Check if the requested path is within available routes
        if normalized_route_path not in available_routes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        # Proceed to the next middleware or request handler
        response = await call_next(request)
        return response