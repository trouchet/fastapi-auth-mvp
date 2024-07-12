from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from backend.app.repositories.logging import RequestLog
from backend.app.database.instance import get_session
from backend.app.listeners.logging import job_listener
from backend.app.repositories.logging import get_log_repository
from backend.app.base.logging import logger

scheduler = AsyncIOScheduler()


async def setup_log_cleanup():
    async with get_log_repository() as log_repo:
        scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        async def delete_old_logs_wrapper():
            await log_repo.delete_old_logs()
        
        scheduler.add_job(delete_old_logs_wrapper, 'interval', days=1)
        scheduler.start()
    
