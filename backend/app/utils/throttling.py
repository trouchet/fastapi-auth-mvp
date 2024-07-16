from backend.app.models.throttling import RateLimiterPolicy

def get_minute_rate_limiter(times: int):
    return RateLimiterPolicy(
        times=times, hours=0, minutes=1, seconds=0, milliseconds=0
    )

# Given rate limiter, find throughput
def get_throughput(rate_limiter: RateLimiterPolicy):
    times = rate_limiter.times
    interval_seconds = rate_limiter.hours * 3600 + \
        rate_limiter.minutes * 60 + \
        rate_limiter.seconds + \
        rate_limiter.milliseconds / 1000
    
    return times / interval_seconds

