from sqlalchemy import Column, String, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from uuid import uuid4

from .users import Base, users_roles_association


# Define the association table for roles and permissions
roles_permissions_association = Table(
    'roles_x_permissions',
    Base.metadata,
    Column('rope_id', UUID, primary_key=True, default=uuid4),
    Column('rope_role_id', UUID, ForeignKey('roles.role_id', ondelete='CASCADE')),
    Column('rope_perm_id', UUID, ForeignKey('permissions.perm_id', ondelete='CASCADE'))
)

class Permission(Base):
    __tablename__ = 'permissions'
    perm_id = Column(UUID, primary_key=True, default=uuid4)
    perm_name = Column(String, unique=True, nullable=False)

    # Relationship to roles via the association table
    perm_roles = relationship(
        'Role', secondary=roles_permissions_association, back_populates='role_permissions'
    )

    def __repr__(self):
        return f"Permission({self.perm_name})"

    def to_dict(self):
        return {
            "perm_id": str(self.perm_id),
            "perm_name": self.perm_name,
            "perm_roles": [role.role_name for role in self.perm_roles]  # Access role names directly
        }

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(UUID, primary_key=True, default=uuid4)
    role_name = Column(String, unique=True, nullable=False)
    role_rate_limit = Column(JSON, nullable=False)

    role_users = relationship(
        'User', secondary=users_roles_association, back_populates='user_roles'
    )

    # Relationship to permissions via the association table
    role_permissions = relationship(
        'Permission', secondary=roles_permissions_association, back_populates='perm_roles'
    )

    def __repr__(self):
        return f"Role({self.role_name})"
    
    def to_dict(self):
        return {
            "role_id": str(self.role_id),
            "role_name": self.role_name,
            "role_permissions": [
                perm.perm_name for perm in self.role_permissions
            ]  # Access permission names directly
        }