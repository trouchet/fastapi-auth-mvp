from fnmatch import fnmatch
from fastapi import Request

from backend.app.core.config import settings

def get_route_and_token(request: Request):
    route = request.scope['path']
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return route, token


def route_requires_authentication(route: str) -> bool:
        prefix = settings.API_V1_STR
        
        allowed_patterns = [
            f"{prefix}/openapi.json",
            f"{prefix}/docs",
            f"{prefix}/redoc",
            f"{prefix}/favicon.ico",
            f"{prefix}/health",
            f"{prefix}/health/*",
            f"{prefix}/public/*", 
            f"{prefix}/token", 
            f"{prefix}/refresh",
        ]
        has_match = lambda pattern: fnmatch(route, pattern)
        non_token_route_list = list(map(has_match, allowed_patterns))

        return not any(non_token_route_list)
