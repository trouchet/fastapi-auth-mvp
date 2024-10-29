DEFAULT_RATE_LIMITS = {
    "times": 5,
    "hours": 0,
    "minutes": 1,
    "seconds": 0,
    "milliseconds": 0
}

class RateLimiterPolicy:
    def __init__(
            self, 
            times: int = DEFAULT_RATE_LIMITS["times"], 
            hours: int = DEFAULT_RATE_LIMITS["hours"], 
            minutes: int = DEFAULT_RATE_LIMITS["minutes"], 
            seconds: int = DEFAULT_RATE_LIMITS["seconds"], 
            milliseconds: int = DEFAULT_RATE_LIMITS["milliseconds"]
        ):
        self.times = times
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    def interval_seconds(self) -> float:
        """Calculate the total interval in seconds."""
        return (
            self.hours * 3600 +
            self.minutes * 60 +
            self.seconds +
            self.milliseconds / 1000
        )

    def throughput(self) -> float: 
        interval = self.interval_seconds()
        
        if interval < 1:
            raise ValueError("Interval must be at least one second.")
        
        # Calculate throughput as actions per second
        return self.times / interval
        

    def to_slowapi_format(self) -> str:
        """Return a rate limit string compatible with slowapi."""
        throughput = self.throughput()

        # Define time units and their thresholds
        units = [("hour", 3600), ("minute", 60), ("second", 1)]
        
        for unit, threshold in units:
            if throughput <= 1 / threshold:
                rate_string = f"{int(throughput / threshold)}/{unit}"
                break

        return rate_string

    def __repr__(self) -> str:
        return f"RateLimiterPolicy({self.to_slowapi_format()})"
