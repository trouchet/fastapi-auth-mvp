DEFAULT_RATE_LIMITS = {
    "times": 10,
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
        # Ensure all values are non-negative
        for name, value in {
                "times": times, 
                "hours": hours, 
                "minutes": minutes, 
                "seconds": seconds, 
                "milliseconds": milliseconds
            }.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}.")

        # Ensure at least one time unit is non-zero
        if hours == 0 and minutes == 0 and seconds == 0 and milliseconds == 0:
            raise ValueError("At least one time unit (hours, minutes, seconds, or milliseconds) must be non-zero.")

        self.times = times
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds


    @property
    def value(self):
        """Calculate the total interval in the specified unit (hours, minutes, or seconds)."""
        # Convert all components to seconds first
        total_seconds = (
            self.hours * 3600 +
            self.minutes * 60 +
            self.seconds +
            self.milliseconds / 1000
        )

        # Convert total seconds to the requested unit
        if self.unit == "hour":
            return total_seconds / 3600
        elif self.unit == "minute":
            return total_seconds / 60
        elif self.unit == "second":
            return total_seconds
        else:
            raise ValueError("Invalid unit. Choose from 'hours', 'minutes', or 'seconds'.")

    @property
    def unit(self):
        # Determine the primary unit based on non-zero major interval component
        if self.hours > 0:
            return "hour"
        elif self.minutes > 0:
            return "minute"
        elif self.seconds > 0 or self.milliseconds > 0:
            return "second"
        else:
            raise ValueError("No valid time unit provided. Available units are 'second', 'minute' and 'hour'") 

    def throughput(self) -> float: 
        interval = self.value
        
        if interval < 1:
            raise ValueError("Interval must be at least one second.")
        
        # Calculate throughput as actions per second
        return self.times / interval

    def to_slowapi_format(self) -> str:
        """Return a rate limit string compatible with slowapi."""
        throughput = self.throughput()

        return f"{int(throughput)}/{self.unit}"

    def __call__(self):
        return self.to_slowapi_format() 

    def __repr__(self) -> str:
        content=f'times={self.times}, interval={self.value} {self.unit}'
        return f"RateLimiterPolicy({content})"
    
    def to_dict(self):
        return {
            "times": self.times,
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "milliseconds": self.milliseconds,
        }