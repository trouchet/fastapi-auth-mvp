from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
from redis import asyncio as aioredis
from typing import Union

from backend.app.utils.request import get_route_and_token
from backend.app.base.exceptions import (
    MissingTokenException, TooManyRequestsException,
)
from backend.app.repositories.logging import get_log_repository
from backend.app.repositories.users import get_user_repository
from backend.app.base.config import settings
from backend.app.base.logging import logger

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
    return await aioredis.Redis.from_url(settings.redis_url)


async def init_rate_limiter():
    redis = await init_redis_pool()
    await FastAPILimiter.init(redis)
    
    logger.info("Rate limiter initialized!")


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

            try:
                current_user = await self.identifier_callable(token)
                user_identifier = current_user.user_username

                with get_user_repository() as user_repo:
                    user_rate_limit = await user_repo.get_user_rate_limit_policy(
                        user_identifier
                    )

                # Get the most permissive rate policy
                limiter_policy=RateLimiterPolicy(**user_rate_limit)
                limiter = get_rate_limiter(user_identifier, limiter_policy)

                if not await limiter.check(request, route):
                    with get_log_repository() as log_repo:
                        log_repo.create_rate_limit_log(current_user.user_id, route)

                    raise TooManyRequestsException()
            except Exception as e:
                logger.error(f"Error processing rate limit for user {user_identifier}: {e}")
                raise

        response = await call_next(request)
        return response
