from fastapi import Request, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from backend.app.repositories.request import RequestLogRepository
from backend.app.database.instance import get_session

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        session=get_session()
        request_repo=RequestLogRepository(session)
        try:
            # Log request information
            await request_repo.create_log(request)

            # Process the request
            response = await call_next(request)
            return response
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
