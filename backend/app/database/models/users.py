from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Table
from typing import Tuple
from sqlalchemy.sql import select
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from . import Base

# Association tables for many-to-many relationships
users_roles_association = Table(
    'users_x_roles', Base.metadata,
    Column('user_id', UUID, ForeignKey('users.user_id', ondelete='cascade')),
    Column('role_id', UUID, ForeignKey('roles.role_id'))
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, index=True, default=uuid4)
    user_created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    user_updated_at = Column(DateTime(timezone=True), default=None, onupdate=datetime.now(timezone.utc))
    user_last_login_at = Column(DateTime, default=None, nullable=True)
    user_username = Column(String, unique=True, index=True, nullable=False)
    user_email = Column(String, unique=True, index=True, nullable=False)
    user_hashed_password = Column(String, nullable=False)
    user_is_active = Column(Boolean, default=True)
    user_access_token = Column(String, nullable=True)
    user_refresh_token = Column(String, nullable=True)

    user_roles = relationship(
        'Role', secondary=users_roles_association, back_populates='role_users', cascade="all"
    )
    user_request_logs = relationship('RequestLog', back_populates='relo_user')

    def has_roles(self, allowed_roles: Tuple[str]):
        user_roles_set = {
            role.role_name for role in self.user_roles
        }
        
        allowed_roles_set = set(allowed_roles)
        intersection_roles = user_roles_set.intersection(allowed_roles_set)
        
        return len(intersection_roles) == len(allowed_roles_set)

    def __repr__(self):
        return f"User({self.user_username})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, User):
            equal_username=self.user_username == other.user_username
            equal_email=self.user_email == other.user_email
            
            return equal_username or equal_email
        else:
            return False

