from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Table
from typing import Tuple
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, JSONB
from uuid import uuid4

from .users import Base, users_roles_association

roles_permissions_association = Table(
    'roles_x_permissions', Base.metadata,
    Column('role_id', UUID, ForeignKey('roles.role_id', ondelete='cascade')),
    Column('perm_id', UUID, ForeignKey('permissions.perm_id'))
)

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(UUID, primary_key=True, default=uuid4)
    role_name = Column(String, unique=True, nullable=False)
    role_rate_limit = Column(JSON, nullable=False)
    role_permissions = relationship(
        'Permission', secondary=roles_permissions_association, back_populates='perm_roles'
    )
    role_users = relationship(
        'User', secondary=users_roles_association,  back_populates='user_roles'
    )

    def __repr__(self):
        return f"Role({self.role_name})"

class Permission(Base):
    __tablename__ = 'permissions'
    perm_id = Column(UUID, primary_key=True, default=uuid4)
    perm_name = Column(String, unique=True, nullable=False)
    perm_roles = relationship(
        'Role', secondary=roles_permissions_association, back_populates='role_permissions'
    )

    def __repr__(self):
        return f"Permission({self.perm_name})"
