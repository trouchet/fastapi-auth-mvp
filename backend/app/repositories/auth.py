from typing import List
from uuid import uuid4
from contextlib import contextmanager

from backend.app.database.models.users import Role
from backend.app.database.models.users import Permission
from backend.app.database.instance import get_session

class RoleRepository:
    def __init__(self, session):
        self.session = session

    def create_role(self, role_name: str, permission_names: List[str]) -> Role:
        """
        Creates a new role and persists it to the database.
    
        Args:
            role_name (str): The name of the role to create.
    
        Returns:
            Role: The newly created role object.
        """
        new_role = Role(role_id=uuid4(), role_name=role_name)
        
        for perm_name in permission_names:
            permission = self.session.query(Permission).filter_by(perm_name=perm_name).first()
            if not permission:
                permission = Permission(perm_id=uuid4(), perm_name=perm_name)
                new_role.role_permissions.append(permission)

        self.session.add(new_role)
        self.session.commit()
        self.session.expunge(new_role)
        
        return new_role

    def get_role_by_name(self, role_name: str) -> Role:
        """
        Retrieves a role object by its name.
    
        Args:
            role_name (str): The name of the role to retrieve.
    
        Returns:
            Role: The retrieved role object or None if not found.
        """
        return self.session.query(Role).filter_by(role_name=role_name).first()

    def get_permissions_by_role(self, role: Role) -> List[Permission]:
        """
        Retrieves all permissions associated with a role.
    
        Args:
            role (Role): The role object to retrieve permissions for.
    
        Returns:
            List[Permission]: A list of all permission objects associated with the role.
        """
        return role.role_permissions

    def get_all_roles(self) -> List[Role]:
        """
        Retrieves all roles from the database.
    
        Returns:
            List[Role]: A list of all role objects.
        """
        return self.session.query(Role).all()
    
    def update_role(self, role: Role) -> None:
        """
        Updates an existing role in the database.
    
        Args:
            role (Role): The role object with updated attributes.
        """
        self.session.commit()
    
    def delete_role(self, role: Role) -> None:
        """
        Deletes a role from the database.
    
        Args:
            role (Role): The role object to delete.
        """
        self.session.delete(role)
        self.session.commit()

class PermissionRepository:
    def __init__(self, session):
        self.session = session

    def create_permission(self, permission_name: str) -> Permission:
        """
        Creates a new permission and persists it to the database.
    
        Args:
            permission_name (str): The name of the permission to create.
    
        Returns:
            Permission: The newly created permission object.
        """
        new_permission = Permission(perm_name=permission_name)
        self.session.add(new_permission)
        self.session.commit()

        return new_permission

    def get_permission_by_name(self, permission_name: str) -> Permission:
        """
        Retrieves a permission object by its name.
    
        Args:
            permission_name (str): The name of the permission to retrieve.
    
        Returns:
            Permission: The retrieved permission object or None if not found.
        """
        return self.session.query(Permission).filter_by(perm_name=permission_name).first()

    def get_all_permissions(self) -> List[Permission]:
        """
        Retrieves all permissions from the database.
    
        Returns:
            List[Permission]: A list of all permission objects.
        """
        return self.session.query(Permission).all()
    
    def update_permission(self, permission: Permission) -> None:
        """
        Updates an existing permission in the database.
    
        Args:
            permission (Permission): The permission object with updated attributes.
        """
        self.session.commit()
    
    def delete_permission(self, permission: Permission) -> None:
        """
        Deletes a permission from the database.
    
        Args:
            permission (Permission): The permission object to delete.
        """
        self.session.delete(permission)
        self.session.commit()

@contextmanager
def get_permission_repository():
    with get_session() as session:
        yield PermissionRepository(session)

@contextmanager
def get_role_repository():
    with get_session() as session:
        yield RoleRepository(session)
