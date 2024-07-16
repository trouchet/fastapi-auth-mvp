from fastapi import Request
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from backend.app.database.models.logging import (
    RequestLog, TaskLog, RateLimitLog,
)
from backend.app.database.instance import get_session
from backend.app.base.config import settings


class LogRepository:
    def __init__(self, session):
        self.session = session

    async def create_request_log(self, user_id, request: Request):
        try:
            body = await request.body()
        except Exception:
            body = ''
        
        log = RequestLog(
            relo_user_id=user_id,
            relo_client_host=request.client.host,
            relo_client_port=request.client.port,
            relo_headers=dict(request.headers),
            relo_body=body.decode("utf-8") if body else None,
            relo_method=request.method,
            relo_url=str(request.url),
            relo_path=request.url.path,
            relo_query_params=dict(request.query_params),
        )
        
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        
        return log
    
    async def delete_old_logs(self, retention_period_days: int = settings.RETENTION_PERIOD_DAYS):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_period_days)
        
        datetime_filter = RequestLog.relo_timestamp < cutoff_date
        self.session.query(RequestLog).filter(datetime_filter).delete()
        await self.session.commit()
        
        datetime_filter = TaskLog.relo_timestamp < cutoff_date
        self.session.query(TaskLog).filter(datetime_filter).delete()
        await self.session.commit()

    def create_task_log(self, job_id, task_name, success, message):
        log = TaskLog(
            talo_job_id=job_id,
            talo_task_name=task_name,
            talo_executed_at=datetime.now(timezone.utc),
            talo_success=success
        )
        
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)

        return log
    
    def create_rate_limit_log(self, user_id, route):
        log = RateLimitLog(rali_user_id=user_id, rali_route=route)
        
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)

        return log


@asynccontextmanager
async def get_log_repository():
    async with get_session() as session:
        yield LogRepository(session)