from fastapi import Request, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware


from backend.app.base.exceptions import InvalidRouteException

class RouteValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.app = app
    
    async def dispatch(self, request: Request, call_next):
        actual_app = self.app.app if hasattr(self.app, 'app') else self.app
        def normalize_map(route_path):
            return route_path.rstrip('/') 
        
        normalized_route_path = normalize_map(request.url.path)

        # Let FastAPI handle path parameter validation
        try:
            response = await call_next(request)
            return response

        # Catch potential FastAPI validation errors
        except (RequestValidationError, HTTPException) as e:
            if isinstance(e, HTTPException) and e.status_code == status.HTTP_404_NOT_FOUND:
                # Handle specific cases like 404 Not Found (optional)
                raise InvalidRouteException(normalized_route_path)
            else:
                raise e  # Re-raise other exceptions
        except Exception as e:
            # Handle other exceptions
            raise InvalidRouteException(normalized_route_path)