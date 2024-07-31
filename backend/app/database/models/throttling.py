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
        
    # Given rate limiter, find throughput
    @property
    def throughput(self):
        times = self.times
        interval_seconds = self.hours * 3600 + \
            self.minutes * 60 + \
            self.seconds + \
            self.milliseconds / 1000
        
        return times / interval_seconds
    
    def get_throughput(self):
        return self.throughput