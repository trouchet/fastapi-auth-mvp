
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

    def __dict__(self):
        return {
            "times": self.times,
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "milliseconds": self.milliseconds
        }
        
    def to_dict(self):
        return self.__dict__()