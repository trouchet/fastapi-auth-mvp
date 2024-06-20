from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, UUID, JSON
)

from datetime import datetime

from backend.app.database.base import Base

class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, index=True)
    user_inserted_at = Column(DateTime, default=None)
    user_updated_at = Column(DateTime, default=None, onupdate=datetime.now)
    user_username = Column(String, unique=True, index=True)
    user_email = Column(String, unique=True, index=True)
    user_hashed_password = Column(String)
    user_role = Column(JSON, default=["user"])
    user_is_active = Column(Boolean, default=True)
    user_access_token = Column(String, nullable=True)
    user_refresh_token = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return f"<User {self.username}>"

    def __eq__(self, other):
        return self.username == other.username
