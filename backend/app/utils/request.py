from fastapi import Request


def get_route_and_token(request: Request):
    route = request.scope['path']
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return route, token
