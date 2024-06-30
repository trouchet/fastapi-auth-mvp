from backend.app.scheduler.request_logging import scheduler

schedulers=[scheduler]

async def start_schedulers():
    for scheduler in schedulers:
        await scheduler.start()