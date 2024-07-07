from fastapi import Request
from contextlib import contextmanager

from backend.app.database.models.request import RequestLog
from backend.app.database.instance import get_session

class RequestLogRepository:
    def __init__(self, session):
        self.session = session

    async def create_log(self, user_id, request: Request):
        body = await request.body()
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

@contextmanager
def get_request_log_repository():
    with get_session() as session:
        yield RequestLogRepository(session)
