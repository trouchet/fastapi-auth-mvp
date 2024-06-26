from sqlalchemy import (
    Column, String, Boolean, DateTime, UUID, 
)
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4

from datetime import datetime
from typing import Any

from . import Base


class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, index=True, default=uuid4)
    user_created_at = Column(DateTime, default=datetime.now)
    user_updated_at = Column(DateTime, default=None, onupdate=datetime.now)
    user_last_login = Column(DateTime, default=None, nullable=True)
    user_username = Column(String, unique=True, index=True)
    user_email = Column(String, unique=True, index=True, nullable=False)
    user_hashed_password = Column(String, nullable=False)
    user_roles = Column(JSONB, default=["user"], nullable=False)
    user_is_active = Column(Boolean, default=True)
    user_access_token = Column(String, nullable=True)
    user_refresh_token = Column(String, nullable=True)

    def __repr__(self):
        return f"User({self.user_username})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, UserDB):
            equal_username=self.user_username == other.user_username
            equal_email=self.user_email == other.user_email
            
            return equal_username or equal_email
        else:
            return False
