from backend.app.models.throttling import RateLimiterPolicy

def get_minute_rate_limiter(times: int):
    return RateLimiterPolicy(
        times=times, hours=0, minutes=1, seconds=0, milliseconds=0
    )