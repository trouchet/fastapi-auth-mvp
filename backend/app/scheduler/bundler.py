from backend.app.scheduler import (
    request_logging_scheduler,
    testing_scheduler,
)
from backend.app.base.config import settings

# Define the schedulers to start
schedulers=[
    request_logging_scheduler,
]

if settings.ENVIRONMENT == 'testing':
    schedulers.append(testing_scheduler)

def start_schedulers():
    for scheduler in schedulers:
        scheduler.start()