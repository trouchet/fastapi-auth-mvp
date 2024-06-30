from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class RequestLog(Base):
    __tablename__ = 'request_logs'
    relo_id = Column(Integer, primary_key=True, index=True)
    relo_user_id = Column(Integer, ForeignKey('users.id'))
    relo_method = Column(String, index=True)
    relo_path = Column(String, index=True)
    relo_status_code = Column(Integer)
    relo_timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    
    relo_user = relationship('User', back_populates='request_logs')
