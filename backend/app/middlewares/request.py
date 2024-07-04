from fastapi import Request, FastAPI
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from backend.app.utils.request import get_route_and_token
from backend.app.repositories.request import RequestLogRepository
from backend.app.database.instance import get_session
from backend.app.core.config import settings


def should_log_request(request: Request, response: Response):
    # Log only POST, PUT, DELETE requests or error responses
    log_verbs = ['GET', 'POST', 'PUT', 'DELETE']
    is_log_verb = request.method in log_verbs
    is_error_response = response.status_code >= 200

    return is_log_verb or is_error_response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, identifier_callable: Callable = None):
        super().__init__(app)
        self.identifier_callable = identifier_callable

    async def dispatch(self, request: Request, call_next: Callable):
        async with get_session() as session:
            request_repo=RequestLogRepository(session)

            # Process the request
            response = await call_next(request)

            try:
                if should_log_request(request, response):
                    route, token = get_route_and_token(request)

                    if settings.route_requires_authentication(route):
                        current_user = await self.identifier_callable(token)
                        user_id = current_user.user_id
                    else:
                        user_id = None

                    await request_repo.create_log(user_id, request)

                return response
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

