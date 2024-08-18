from fastapi import Request

from backend.app.models.throttling import RateLimiterPolicy

def get_minute_rate_limiter(times: int):
    return RateLimiterPolicy(
        times=times, hours=0, minutes=1, seconds=0, milliseconds=0
    )

async def ip_identifier(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    
    return request.client.host + ":" + request.scope["path"]
