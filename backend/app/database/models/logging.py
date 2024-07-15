from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

from .base import Base

class RequestLog(Base):
    __tablename__ = 'request_logs'
    relo_id = Column(UUID, primary_key=True, index=True, unique=True, nullable=False, default=uuid4)
    relo_client_host = Column(String)
    relo_client_port = Column(Integer)
    relo_user_id = Column(UUID, ForeignKey('users.user_id'))
    relo_headers = Column(JSONB)
    relo_body = Column(Text, nullable=True)
    relo_query_params = Column(JSONB)
    relo_url = Column(String, index=True)
    relo_method = Column(String, index=True)
    relo_path = Column(String, index=True)
    relo_timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    relo_user = relationship('User', back_populates='user_request_logs')

class TaskLog(Base):
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    task_name = Column(String, index=True)
    executed_at = Column(DateTime, default=datetime.now(timezone.utc))
    success = Column(Boolean)
    message = Column(String)