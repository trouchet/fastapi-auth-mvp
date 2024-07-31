from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
from redis import asyncio as aioredis
from typing import Union

from backend.app.base.exceptions import (
    MissingTokenException, TooManyRequestsException,
)
from backend.app.base.config import settings
from backend.app.base.logging import logger
from backend.app.utils.throttling import get_rate_limiter
from backend.app.utils.request import get_route_and_token
from backend.app.repositories.users import get_users_repository_cmanager
from backend.app.services.auth import get_current_user
from backend.app.models.throttling import RateLimiterPolicy

async def init_redis_pool():
    return await aioredis.Redis.from_url(settings.redis_url)


async def init_rate_limiter():
    redis = await init_redis_pool()
    await FastAPILimiter.init(redis)

    logger.info("Rate limiter initialized!")


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        route, token = get_route_and_token(request)
        
        # Check if the route requires authentication
        if settings.route_requires_authentication(route):
            if not token:
                raise MissingTokenException()

            current_user = await get_current_user(token)
            user_identifier = current_user.user_username

            async with get_users_repository_cmanager() as user_repository:
                rate_policy=await user_repository.get_user_loosest_rate_limit(
                        current_user.user_username
                )

            limiter = get_rate_limiter(user_identifier, rate_policy)

            if not await limiter.check(request, route):
                raise TooManyRequestsException()

        response = await call_next(request)
        
        return response
