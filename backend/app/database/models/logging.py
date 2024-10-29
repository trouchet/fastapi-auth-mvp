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
    lore_id = Column(UUID, primary_key=True, index=True, unique=True, nullable=False, default=uuid4)
    lore_client_host = Column(String)
    lore_client_port = Column(Integer)
    lore_user_id = Column(UUID, ForeignKey('users.user_id'))
    lore_headers = Column(JSONB)
    lore_body = Column(Text, nullable=True)
    lore_query_params = Column(JSONB)
    lore_url = Column(String, index=True)
    lore_method = Column(String, index=True)
    lore_path = Column(String, index=True)
    lore_timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    lore_user = relationship('User', back_populates='user_lore_logs')

class TaskLog(Base):
    __tablename__ = "task_logs"
    
    talo_id = Column(Integer, primary_key=True, index=True)
    talo_job_id = Column(String, index=True)
    talo_task_name = Column(String, index=True)
    talo_executed_at = Column(DateTime, default=datetime.now(timezone.utc))
    talo_success = Column(Boolean)
    talo_message = Column(String)