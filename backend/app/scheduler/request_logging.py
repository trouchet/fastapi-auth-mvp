from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.app.repositories.request import (
    RequestLog
)
from backend.app.database.instance import get_session

scheduler = AsyncIOScheduler()

async def delete_old_logs(retention_period_days=30):
    cutoff_date = datetime.now() - timedelta(days=retention_period_days)

    with get_session() as session:
        datetime_filter = RequestLog.relo_timestamp < cutoff_date
        session.query(RequestLog).filter(datetime_filter).delete()
        session.commit()
        session.close()


async def setup_log_cleanup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_old_logs, 'interval', days=1)
    
