from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Awaitable
from redis import asyncio as aioredis
from typing import Union, Optional
import traceback

from backend.app.utils.throttling import ip_identifier
from backend.app.utils.request import get_token, get_route
from backend.app.base.auth import get_current_user
from backend.app.database.models.users import User
from backend.app.repositories.auth import role_repository_async_context_manager
from backend.app.repositories.users import user_repository_async_context_manager
from backend.app.base.exceptions import (
    MissingTokenException, TooManyRequestsException, RatePolicyException
)
from backend.app.base.config import settings
from backend.app.base.logging import logger
from backend.app.utils.throttling import RateLimiterPolicy


def get_user_rate_policy(user: User) -> Optional[RateLimiterPolicy]:
    """Determine the most permissive rate policy based on user roles.
    
    Args:
        user (User): The current user object.

    Returns:
        Optional[RateLimiterPolicy]: The most permissive rate limiter policy for the user, 
        or None if the user has no roles.
    """
    if not user or not user.user_roles:
        return None  # No roles or user found

    # Extract rate policies from user roles
    rate_policies = [
        RateLimiterPolicy(**role.role_rate_limit)
        for role in user.user_roles
    ]

    # Return the most permissive rate policy based on throughput
    return max(rate_policies, key=lambda p: p.throughput(), default=None)

async def fetch_current_user(request: Request) -> User:
    """Fetch the current user from the request token.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        User: The current user object.

    Raises:
        MissingTokenException: If the request token is missing.
        RatePolicyException: If there is an error retrieving the user.
    """
    token = get_token(request)
    if not token:
        raise MissingTokenException()

    try:
        return await get_current_user(token)
    except Exception as e:
        logger.error(f"Error retrieving current user: {e}\n{traceback.format_exc()}")
        raise RatePolicyException()

async def get_request_rate_policy(request: Request) -> Optional[RateLimiterPolicy]:
    """Retrieve the user's rate limiting policy based on their roles.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        Optional[RateLimiterPolicy]: The user's rate limiting policy or a default policy for non-authenticated users.
    """
    route = get_route(request)
    if settings.route_requires_authentication(route):
        current_user = await fetch_current_user(request)
        print(current_user)
        return get_user_rate_policy(current_user)

    # Default rate limit policy for unauthenticated users
    return RateLimiterPolicy()  # Define this separately if there are common default values

async def get_user_identifier(request: Request) -> Union[str, None]:
    """Retrieve the user identifier based on the request.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        Union[str, None]: A string identifier for the user or the remote IP address if unauthenticated.
    """
    route = get_route(request)

    if settings.route_requires_authentication(route):
        current_user = await fetch_current_user(request)
        return f"user:{current_user.user_id}"

    return get_remote_address(request)

# Rate limiter instance
limiter = Limiter(key_func=get_user_identifier, storage_uri=settings.redis_url)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rate_limit_policy = await get_request_rate_policy(request)
        without_rate_limit='0/second'
        has_rate_limit=rate_limit_policy and rate_limit_policy()!=without_rate_limit
        if has_rate_limit:
            
            @limiter.limit(rate_limit_policy)
            async def limited_call_next(request: Request):
                return await call_next(request)

            return await limited_call_next(request)

        logger.info("No rate limit applied, proceeding with request.")
        return await call_next(request)

async def init_rate_limiter(app_: FastAPI):
    """Initialize the SlowAPI rate limiter with Redis connection."""
    # Initialize the limiter
    app_.state.limiter = limiter
    app_.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiter initialized!")