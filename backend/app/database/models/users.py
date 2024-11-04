from datetime import datetime, timezone
from typing import Any, List
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship

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
    user_created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    user_updated_at = Column(
        DateTime(timezone=True), default=None, onupdate=datetime.now(timezone.utc)
    )
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

    def has_roles(self, roles_names: List[str]) -> bool:
        """
        Checks if the user has any of the roles specified in roles_names.
        
        Args:
            roles_names (List[str]): List of role names to check against the user's roles.
        
        Returns:
            bool: True if the user has any of the roles in roles_names, False otherwise.
        """
        user_roles_names = {role.role_name for role in self.user_roles}
        return not set(roles_names).isdisjoint(user_roles_names)
    
    def has_permissions(self, permissions_names: List[str]) -> bool:
        """
        Checks if the user has any of the specified permissions.
        
        Args:
            permissions_names (List[str]): List of permission names to check against the user's permissions.
        
        Returns:
            bool: True if the user has any of the permissions in permissions_names, False otherwise.
        """
        user_permissions = {
             permission.permission_name 
             for role in self.user_roles for permission in role.role_permissions
        }
        return not set(permissions_names).isdisjoint(user_permissions)