from fastapi import Request, FastAPI
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from backend.app.utils.request import get_token, get_route
from backend.app.base.exceptions import MissingTokenException
from backend.app.repositories.logging import get_log_repository
from backend.app.services.auth import get_current_user
from backend.app.base.config import settings


def should_log_request(request: Request, response: Response):
    # Log only POST, PUT, DELETE requests or error responses
    log_verbs = ['GET', 'POST', 'PUT', 'DELETE']
    is_log_verb = request.method in log_verbs
    is_error_response = response.status_code >= 200
    must_log_route = settings.route_is_logged(request.url.path)

    return must_log_route and (is_log_verb or is_error_response)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        async with get_log_repository() as log_repository:

            # Process the request
            response = await call_next(request)

            if should_log_request(request, response):
                route, token = get_route_and_token(request)

                if settings.route_requires_authentication(route):
                    current_user = await get_current_user(token)
                    user_id = current_user.user_id
                else:
                    user_id = await ip_identifier(request)

                await log_repository.create_request_log(user_id, request)

            return response

