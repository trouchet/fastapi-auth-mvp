from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

class RequestLogDB(Base):
    __tablename__ = 'request_logs'

    relo_id = Column(UUID, primary_key=True, index=True)
    relo_method = Column(String, nullable=False, index=True)
    relo_url = Column(String, nullable=False)
    relo_headers = Column(JSONB, nullable=True)
    relo_query_params = Column(JSONB, nullable=True)
    relo_client_host = Column(String, nullable=True)
    relo_client_port = Column(Integer, nullable=True)
    relo_cookies = Column(JSONB, nullable=True)
    relo_body = Column(Text, nullable=True)
    relo_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
