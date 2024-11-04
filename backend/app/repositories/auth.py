from typing import List
from uuid import uuid4
from contextlib import asynccontextmanager

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from backend.app.database.models.auth import Role, Permission, roles_permissions_association
from backend.app.database.instance import get_session
from backend.app.base.logging import logger

class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_role(
        self, role_name: str, rate_limit: dict, permission_names: List[str]
    ) -> Role:
        """
        Creates a new role and assigns permissions to it.

        Args:
            role_name (str): The name of the role to create.
            rate_limit (dict): Rate limit information.
            permission_names (List[str]): List of permission names to assign to the role.

        Returns:
            Role: The newly created role object with assigned permissions.
        """
        role_id = str(uuid4())
        new_role = Role(role_id=role_id, role_name=role_name, role_rate_limit=rate_limit)
        
        try:
            permissions = []
            for perm_name in permission_names:
                permission = await self._get_or_create_permission(perm_name)
                permissions.append(permission)

            # Link permissions to the new role
            new_role.role_permissions.extend(permissions)
            self.session.add(new_role)
            await self.session.commit()
            await self.session.refresh(new_role)
            
            return new_role

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create role '{role_name}': {e}")
            raise e
    
    async def _get_or_create_permission(self, perm_name: str) -> Permission:
        """
        Retrieves an existing permission by name or creates a new one if it doesn't exist.
        
        Args:
            perm_name (str): The name of the permission.

        Returns:
            Permission: The existing or newly created Permission object.
        """
        statement = select(Permission).filter(Permission.perm_name == perm_name)
        result = await self.session.execute(statement)
        permission = result.scalars().first()

        if not permission:
            permission = Permission(
                perm_id=str(uuid4()),
                perm_name=perm_name
            )
            self.session.add(permission)
            await self.session.flush()
            logger.info(f"Permission '{perm_name}' created and added to database.")

        return permission

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
        # Query RolePermission to find all permissions linked to the role
        query = (
            select(Permission)
            .join(RolePermission, Permission.perm_id == RolePermission.rope_perm_id)
            .where(RolePermission.rope_role_id == role.role_id)
        )
        result = await self.session.execute(query)
        
        # Fetch all permissions
        permissions = result.scalars().all()
        return permissions

    async def get_all_roles(self) -> List[Role]:
        """
        Retrieves all roles from the database.
    
        Returns:
            List[Role]: A list of all role objects.
        """
        statement = await self.session.execute(select(Role))
        
        return statement.scalars().all()
    
    async def get_role_permissions(self, role: Role) -> List[Permission]:
        """
        Retrieves all permissions associated with a role.

        Args:
            role (Role): The role object to retrieve permissions for.

        Returns:
            List[Permission]: A list of all permission objects associated with the role.
        """
        # Query to get permissions through the RolePermission model
        query = (
            select(Permission)
            .join(RolePermission, RolePermission.perm_id == Permission.perm_id)
            .where(RolePermission.role_id == role.role_id)
        )
        result = await self.session.execute(query)
        
        # Fetch all permissions
        permissions = result.scalars().all()
        return permissions

    
    async def update_role_permissions(self, role: Role, new_permissions: List[Permission]):
        query = select(Role).where(Role.role_id == role.role_id)\
            .options(joinedload(Role.role_permissions))
        result = await self.session.execute(query)
        role = result.scalars().first()
        
        if role:
            role.role_permissions = new_permissions
            await self.session.commit()
            await self.session.refresh(role)
            return role
    
    async def update_role(self, role: Role):
        """
        Updates a role in the database.
        
        Args:
            role (Role): The role object to update.
        """
        await self.session.merge(role)
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
        
        self.session.add(new_permission)
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
        query = select(Permission).where(Permission.perm_name == permission_name)
        result = await self.session.execute(query)
        permission = result.scalars().first()
        return permission

    async def get_all_permissions(self) -> List[Permission]:
        """
        Retrieves all permissions from the database.
    
        Returns:
            List[Permission]: A list of all permission objects.
        """
        query = select(Permission)
        result = await self.session.execute(query)
        permissions = result.scalars().all()
        return permissions
    
    async def update_permission(self, permission: Permission) -> None:
        """
        Updates an existing permission in the database.
    
        Args:
            permission (Permission): The permission object with updated attributes.
        """
        await self.session.merge(permission)
        await self.session.commit()

    async def delete_permission(self, permission: Permission) -> None:
        """
        Deletes a permission from the database.
    
        Args:
            permission (Permission): The permission object to delete.
        """
        await self.session.delete(permission)
        await self.session.commit()
    
    async def get_role_rate_limit(self, role_name: str) -> dict:
        """
        Retrieves the rate limit configuration for a role.
    
        Args:
            role_name (str): The name of the role to retrieve the rate limit for.
    
        Returns:
            dict: The rate limit configuration for the role.
        """
        query = select(Role).where(Role.role_name == role_name)
        result = await self.session.execute(query)
        role = result.scalars().first()
        
        if role:
            return role.role_rate_limit
        return None

@asynccontextmanager
async def get_permission_async_context_manager():
    async with get_session() as session:
        yield PermissionRepository(session)

async def get_permission_repository():
    async with get_session() as session:
        yield PermissionRepository(session)

@asynccontextmanager
async def role_repository_async_context_manager():
    async with get_session() as session:
        yield RoleRepository(session)

async def get_role_repository():
    async with get_session() as session:
        yield RoleRepository(session)
