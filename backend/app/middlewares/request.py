from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


from backend.app.repositories.request import (
    RequestLogRepository,
)
from backend.app.database.instance import get_session

def should_log_request(request: Request, response: Response):
    # Log only POST, PUT, DELETE requests or error responses
    log_verbs = ['POST', 'PUT', 'DELETE']
    is_log_verb = request.method in log_verbs
    is_error_response = response.status_code >= 400

    return is_log_verb or is_error_response
        

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ):
        with get_session() as session:
            request_repo=RequestLogRepository(session)

            # Process the request
            response = await call_next(request)

            try:
                if should_log_request(request, response):
                    # Log request information
                    await request_repo.create_log(request)

                return response
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()




