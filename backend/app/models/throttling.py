
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
