from fnmatch import fnmatch
from fastapi import Request

from backend.app.core.config import settings

def get_route_and_token(request: Request):
    route = request.scope['path']
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return route, token
