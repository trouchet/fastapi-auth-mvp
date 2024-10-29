from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
from redis import asyncio as aioredis
from typing import Union

from backend.app.utils.throttling import ip_identifier
from backend.app.utils.request import get_token, get_route
from backend.app.base.auth import get_current_user
from backend.app.database.models.users import User
from backend.app.base.exceptions import (
    MissingTokenException, TooManyRequestsException, RatePolicyException
)
from backend.app.base.config import settings
from backend.app.data.auth import ROLES_METADATA
from backend.app.base.logging import logger

# Define rate limiting policy
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
        self.interval_seconds = (
            hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        )

    def throughput(self) -> float:
        """Calculate the throughput based on policy."""
        return self.times / self.interval_seconds if self.interval_seconds > 0 else float("inf")

    def __repr__(self) -> str:
        return f"RateLimiterPolicy({self.interval_seconds})"

async def init_redis_pool():
    """Initialize Redis connection pool asynchronously."""
    return await aioredis.Redis.from_url(settings.redis_url)


async def init_rate_limiter():
    """Initialize FastAPI rate limiter with Redis connection."""
    redis = await init_redis_pool()
    await FastAPILimiter.init(redis)
    logger.info("Rate limiter initialized!")


def get_rate_limiter(
        policy: RateLimiterPolicy = RateLimiterPolicy()
    ) -> RateLimiter:
    """Get configured RateLimiter based on policy."""
    return RateLimiter(
        times=policy.times,
        milliseconds=int(policy.interval_seconds * 1000)
    )

def get_user_rate_policy(user: User) -> RateLimiterPolicy:
    """Determine the most permissive rate policy based on user roles."""
    rate_policies = [
        ROLES_METADATA[role.role_name]['rate_policy']
        for role in user.user_roles
        if role.role_name in ROLES_METADATA
    ]
    return max(rate_policies, key=lambda p: p.throughput(), default=RateLimiterPolicy())


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        route = get_route(request)

        if settings.route_requires_authentication(route):
            token = get_token(request)
            if not token:
                raise MissingTokenException()

            try:
                current_user = await get_current_user(token)
                rate_policy = get_user_rate_policy(current_user)
            except Exception as e:
                logger.error(f"Error retrieving current user: {e}")
                raise RatePolicyException("Unable to retrieve user rate policy")
        else:
            rate_policy = RateLimiterPolicy()

        limiter = get_rate_limiter(rate_policy)
        
        # Use RateLimiter dependency for rate limiting
        await limiter(request)

        return await call_next(request)
