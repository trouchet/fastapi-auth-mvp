from backend.app.scheduler.request_logging import scheduler as request_logging_scheduler

# Define the schedulers to start
schedulers=[
    request_logging_scheduler
]

def start_schedulers():
    for scheduler in schedulers:
        scheduler.start()