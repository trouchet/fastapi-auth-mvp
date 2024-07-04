from typing import List
from uuid import uuid4
from contextlib import asynccontextmanager

from backend.app.database.models.users import Role
from backend.app.database.models.users import Permission
from backend.app.database.instance import get_session
from sqlalchemy.future import select

class RoleRepository:
    def __init__(self, session):
        self.session = session

    async def create_role(self, role_name: str, permission_names: List[str]) -> Role:
        """
        Creates a new role and persists it to the database.

        Args:
            role_name (str): The name of the role to create.
            permission_names (List[str]): List of permission names associated with the role.

        Returns:
            Role: The newly created role object.
        """
        new_role = Role(role_id=str(uuid4()), role_name=role_name)
        
        try:
            for perm_name in permission_names:
                condition = Permission.perm_name == perm_name
                statement = select(Permission).filter(condition)

                permission = await self.session.execute(statement)
                existing_permission = permission.scalars().first()
                
                if not existing_permission:
                    new_permission = Permission(perm_id=str(uuid4()), perm_name=perm_name)
                    
                    self.session.add(new_permission)
                    await self.session.flush()
                    new_role.role_permissions.append(new_permission)
                else:
                    new_role.role_permissions.append(existing_permission)

            self.session.add(new_role)
            await self.session.commit()
            await self.session.refresh(new_role)

            return new_role
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_role_by_name(self, role_name: str) -> Role:
        """
        Retrieves a role object by its name.

        Args:
            role_name (str): The name of the role to retrieve.

        Returns:
            Role: The retrieved role object or None if not found.
        """
        statement = select(Role).where(Role.role_name == role_name)
        result = await self.session.execute(statement)
        role = result.scalars().first()
        return role

    async def get_permissions_by_role(self, role: Role) -> List[Permission]:
        """
        Retrieves all permissions associated with a role.
    
        Args:
            role (Role): The role object to retrieve permissions for.
    
        Returns:
            List[Permission]: A list of all permission objects associated with the role.
        """
        return role.role_permissions

    async def get_all_roles(self) -> List[Role]:
        """
        Retrieves all roles from the database.
    
        Returns:
            List[Role]: A list of all role objects.
        """
        return await self.session.query(Role).all()
    
    async def update_role(self, role: Role) -> None:
        """
        Updates an existing role in the database.
    
        Args:
            role (Role): The role object with updated attributes.
        """
        await self.session.commit()
    
    async def delete_role(self, role: Role) -> None:
        """
        Deletes a role from the database.
    
        Args:
            role (Role): The role object to delete.
        """
        await self.session.delete(role)
        await self.session.commit()

class PermissionRepository:
    def __init__(self, session):
        self.session = session

    async def create_permission(self, permission_name: str) -> Permission:
        """
        Creates a new permission and persists it to the database.
    
        Args:
            permission_name (str): The name of the permission to create.
    
        Returns:
            Permission: The newly created permission object.
        """
        new_permission = Permission(perm_name=permission_name)
        await self.session.add(new_permission)
        await self.session.commit()

        return new_permission

    async def get_permission_by_name(self, permission_name: str) -> Permission:
        """
        Retrieves a permission object by its name.
    
        Args:
            permission_name (str): The name of the permission to retrieve.
    
        Returns:
            Permission: The retrieved permission object or None if not found.
        """
        return await self.session.query(Permission).filter_by(perm_name=permission_name).first()

    async def get_all_permissions(self) -> List[Permission]:
        """
        Retrieves all permissions from the database.
    
        Returns:
            List[Permission]: A list of all permission objects.
        """
        return await self.session.query(Permission).all()
    
    async def update_permission(self, permission: Permission) -> None:
        """
        Updates an existing permission in the database.
    
        Args:
            permission (Permission): The permission object with updated attributes.
        """
        await self.session.commit()
    
    async def delete_permission(self, permission: Permission) -> None:
        """
        Deletes a permission from the database.
    
        Args:
            permission (Permission): The permission object to delete.
        """
        await self.session.delete(permission)
        await self.session.commit()

@asynccontextmanager
async def get_permission_repository():
    async with get_session() as session:
        yield PermissionRepository(session)

@asynccontextmanager
async def get_role_repository():
    async with get_session() as session:
        yield RoleRepository(session)
