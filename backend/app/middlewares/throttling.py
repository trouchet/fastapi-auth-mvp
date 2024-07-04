from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
from aioredis import create_redis_pool
from typing import Callable, Union
from fnmatch import fnmatch

from backend.app.utils.request import get_route_and_token
from backend.app.core.exceptions import MissingTokenException, TooManyRequestsException
from backend.app.core.config import settings, is_docker
from backend.app.data.auth import ROLES_METADATA

class RateLimiterPolicy:
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


async def init_rate_limiter():
    redis = await init_redis_pool()
    await FastAPILimiter.init(redis)


# Given rate limiter, find throughput
def get_throughput(rate_limiter: RateLimiterPolicy):
    times = rate_limiter.times
    interval_seconds = rate_limiter.hours * 3600 + \
        rate_limiter.minutes * 60 + \
        rate_limiter.seconds + \
        rate_limiter.milliseconds / 1000
    
    return times / interval_seconds


def get_rate_limiter(
    user_identifier: Union[str, None], 
    policy: RateLimiterPolicy = RateLimiterPolicy()
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
    def __init__(self, app: FastAPI, identifier_callable: Callable[[str], Awaitable]):
        super().__init__(app)
        self.identifier_callable = identifier_callable

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        route, token = get_route_and_token(request)

        # Check if the route requires authentication
        if settings.route_requires_authentication(route):
            if not token:
                raise MissingTokenException()

            current_user = await self.identifier_callable(token)
            user_identifier = current_user.user_username
            roles = current_user.user_roles
            rate_policies = [
                ROLES_METADATA[role]['rate_policy'] for role in roles
            ]

            # Get the most permissive rate policy
            rate_policy = max(rate_policies, key=get_throughput)
            limiter = get_rate_limiter(user_identifier, rate_policy)

            if not await limiter.check(request, route):
                raise TooManyRequestsException()

        response = await call_next(request)
        return response

    

