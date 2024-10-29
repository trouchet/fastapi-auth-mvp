from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from backend.app.listeners.logging import task_job_listener
from backend.app.repositories.logging import get_log_repository

scheduler = AsyncIOScheduler()

# Retention period in days
LOGS_POLICY=1

async def setup_log_cleanup():
    async with get_log_repository() as log_repo:
        event_at=EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        scheduler.add_listener(task_job_listener, event_at)
        
        async def delete_old_logs_wrapper():
            await log_repo.delete_old_logs()

        scheduler.add_job(delete_old_logs_wrapper, 'interval', days=1)
        scheduler.start()

