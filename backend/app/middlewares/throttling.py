from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
from aioredis import create_redis_pool
from typing import Callable
from enum import Enum
from fnmatch import fnmatch

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    MissingTokenException,
    TooManyRequestsException,
)
from backend.app.core.config import settings

class RateLimiterPolicy(Enum):
    def __init__(
            self, 
            times: int = 5, 
            hours: int = 0, 
            minutes: int = 1, 
            seconds: int = 0, 
            milliseconds: int = 0
        ):
        self.times = times
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds


async def init_redis_pool():
    return await create_redis_pool(settings.redis_url)

async def init_rate_limiter(app: FastAPI):
    redis = await init_redis_pool()
    await FastAPILimiter.init(redis)

def get_rate_limiter(
    user_identifier: str, policy: RateLimiterPolicy = RateLimiterPolicy()
):
    return RateLimiter(
        times=policy.times, 
        hours=policy.hours,
        minutes=policy.minutes,
        seconds=policy.seconds,
        milliseconds=policy.milliseconds,
        identifier=user_identifier
    )

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: FastAPI, identifier_callable: Callable[[str], Awaitable]
    ):
        super().__init__(app)
        self.identifier_callable = identifier_callable

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        route = request.scope['path']
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        # Check if the route requires authentication
        if self.route_requires_authentication(route):
            if not token:
                raise MissingTokenException()

            current_user = await self.identifier_callable(token)
            user_identifier = current_user.user_username
            limiter = get_rate_limiter(user_identifier)

            if not await limiter.check(request, route):
                raise TooManyRequestsException()

        response = await call_next(request)
        return response

    def route_requires_authentication(self, route: str) -> bool:
        prefix = settings.API_V1_STR
        allowed_patterns = [
            f"/{prefix}/public/*", 
            f"/{prefix}/token", 
            f"/{prefix}/refresh",
        ]

        for pattern in allowed_patterns:
            if fnmatch(route, pattern):
                return False

        return True  # Route requires authentication

