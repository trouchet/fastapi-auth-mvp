from fastapi import Request

def get_token(request: Request) -> str:
    return request.headers.get('Authorization', '').replace('Bearer ', '')

def get_route(request: Request) -> str:
    return request.scope['path']