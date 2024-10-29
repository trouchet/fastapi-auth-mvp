from typing import Union
from fastapi_limiter.depends import RateLimiter

from backend.app.models.throttling import RateLimiterPolicy

def get_minute_rate_limiter(times: int):
    return RateLimiterPolicy(
        times=times, hours=0, minutes=1, seconds=0, milliseconds=0
    )

def get_rate_limiter(
    user_identifier: Union[str, None], 
    policy: RateLimiterPolicy = RateLimiterPolicy()
):
    return RateLimiter(
        identifier=user_identifier,
        times=policy.times, 
        hours=policy.hours,
        minutes=policy.minutes,
        seconds=policy.seconds,
        milliseconds=policy.milliseconds
    )
