from sqlalchemy import Column, String, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from uuid import uuid4

from .users import Base, users_roles_association

roles_permissions_association = Table(
    'roles_x_permissions', Base.metadata,
    Column('role_id', UUID, ForeignKey('roles.role_id', ondelete='cascade')),
    Column('perm_id', UUID, ForeignKey('permissions.perm_id'))
)

profiles_roles_association = Table(
    'profiles_x_roles', Base.metadata,
    Column('profile_id', UUID, ForeignKey('profiles.profile_id', ondelete='cascade')),
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
        return f"Profile({self.profile_name})"

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(UUID, primary_key=True, default=uuid4)
    role_name = Column(String, unique=True, nullable=False)
    role_rate_limit = Column(JSON, nullable=False)
    role_permissions = relationship(
        'Permission', secondary=roles_permissions_association, 
        back_populates='perm_roles'
    )
    role_users = relationship(
        'User', secondary=users_roles_association,  
        back_populates='user_roles'
    )
    role_profiles = relationship(
        'Profile', secondary=profiles_roles_association, back_populates='profile_roles'
    )

    def __repr__(self):
        return f"Role({self.role_name})"

class Permission(Base):
    __tablename__ = 'permissions'
    perm_id = Column(UUID, primary_key=True, default=uuid4)
    perm_name = Column(String, unique=True, nullable=False)
    perm_roles = relationship(
        'Role', secondary=roles_permissions_association, 
        back_populates='role_permissions'
    )

    def __repr__(self):
        return f"Permission({self.perm_name})"
