from sqlalchemy import (
    Column, String, Boolean, DateTime, UUID,
    ForeignKey, Table
)

from typing import Tuple
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4

from datetime import datetime, timezone
from typing import Any

from . import Base


# Association tables for many-to-many relationships
users_roles_association = Table(
    'users_x_roles', Base.metadata,
    Column('user_id', UUID, ForeignKey('users.user_id', ondelete='cascade')),
    Column('role_id', UUID, ForeignKey('roles.role_id'))
)


roles_permissions_association = Table(
    'roles_x_permissions', Base.metadata,
    Column('role_id', UUID, ForeignKey('roles.role_id', ondelete='cascade')),
    Column('perm_id', UUID, ForeignKey('permissions.perm_id'))
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, index=True, default=uuid4)
    user_created_at = Column(DateTime, default=datetime.now)
    user_updated_at = Column(DateTime, default=None, onupdate=datetime.now(timezone.utc))
    user_last_login = Column(DateTime, default=None, nullable=True)
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
        return not user_roles_set.isdisjoint(allowed_roles_set)

    def has_permissions(self, permission_names: Tuple[str]) -> bool:
        user_permissions = {
            permission.perm_name 
            for role in self.user_roles 
            for permission in role.role_permissions
        }
        required_permissions = set(permission_names)
        return required_permissions.issubset(user_permissions)

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

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(UUID, primary_key=True)
    role_name = Column(String, unique=True, nullable=False)
    role_permissions = relationship(
        'Permission', secondary=roles_permissions_association, back_populates='perm_roles'
    )
    role_users = relationship(
        'User', secondary=users_roles_association,  back_populates='user_roles'
    )

class Permission(Base):
    __tablename__ = 'permissions'
    perm_id = Column(UUID, primary_key=True)
    perm_name = Column(String, unique=True, nullable=False)
    perm_roles = relationship(
        'Role', secondary=roles_permissions_association, back_populates='role_permissions'
    )
