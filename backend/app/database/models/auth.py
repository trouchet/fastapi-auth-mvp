from sqlalchemy import Column, String, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from uuid import uuid4

from .users import Base, users_roles_association

class RolePermission(Base):
    __tablename__ = 'roles_x_permissions'
    rope_id = Column(UUID, primary_key=True, default=uuid4)
    rope_role_id = Column(UUID, ForeignKey('roles.role_id', ondelete='CASCADE'))
    rope_perm_id = Column(UUID, ForeignKey('permissions.perm_id', ondelete='CASCADE'))
    
    # Define relationships to Role and Permission for easier access
    role = relationship('Role', back_populates='role_permissions')
    permission = relationship('Permission', back_populates='perm_roles')

class Permission(Base):
    __tablename__ = 'permissions'
    perm_id = Column(UUID, primary_key=True, default=uuid4)
    perm_name = Column(String, unique=True, nullable=False)

    # Relationship to RolePermission association table
    perm_roles = relationship(
        'RolePermission', back_populates='permission', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Permission({self.perm_name})"

    def to_dict(self):
        return {
            "perm_id": str(self.perm_id),
            "perm_name": self.perm_name,
            "perm_roles": [rp.role.role_name for rp in self.perm_roles]  # Access role names through RolePermission
        }

profiles_roles_association = Table(
    'profiles_x_roles', Base.metadata,
    Column('profile_id', UUID, ForeignKey('profiles.prof_id', ondelete='cascade')),
    Column('role_id', UUID, ForeignKey('roles.role_id', ondelete='cascade'))
)

class Profile(Base):
    __tablename__ = 'profiles'
    prof_id = Column(UUID, primary_key=True, default=uuid4)
    prof_name = Column(String, unique=True, nullable=False)
    prof_roles = relationship(
        'Role', secondary=profiles_roles_association, back_populates='role_profiles'
    )
    prof_users = relationship('User', back_populates='user_profile')

    def __repr__(self):
        return f"Profile({self.prof_name})"

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(UUID, primary_key=True, default=uuid4)
    role_name = Column(String, unique=True, nullable=False)
    role_rate_limit = Column(JSON, nullable=False)

    role_users = relationship(
        'User', secondary=users_roles_association, back_populates='user_roles'
    )

    # Relationship to RolePermission association table
    role_permissions = relationship(
        'RolePermission', back_populates='role', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Role({self.role_name})"
    
    def to_dict(self):
        return {
            "role_id": str(self.role_id),
            "role_name": self.role_name,
            "role_permissions": [rp.permission.perm_name for rp in self.role_permissions]  # Access permission names through RolePermission
        }
