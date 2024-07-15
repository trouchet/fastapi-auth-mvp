from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Tuple
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.future import select
from sqlalchemy import delete
from contextlib import asynccontextmanager
from sqlalchemy.orm import selectinload

from backend.app.utils.security import hash_string, is_hash_from_string
from backend.app.models.users import UpdateUser
from backend.app.database.models.users import User
from backend.app.database.models.auth import Role

from backend.app.database.instance import get_session
from backend.app.database.models.users import users_roles_association

# Security artifacts
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TokenDependency = Annotated[str, Depends(oauth2_scheme)]


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: str) -> User:
        statement = select(User).where(User.user_id == user_id)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user
    
    async def get_user_id_by_username(self, username: str) -> UUID:
        statement = select(User).where(User.user_username == username)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user.user_id

    async def get_user_by_email(self, email: str) -> User:
        statement = select(User).where(User.user_email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user
    
    async def get_user_id_by_email(self, email: str) -> UUID:
        statement = select(User).where(User.user_email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user.user_id

    async def get_user_by_username(self, username: str) -> User:
        statement = select(User).where(User.user_username == username)
        result = await self.session.execute(statement)
        user = result.scalars().first()

        if user:
            return user

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def create_users(self, users: List[User]):
        for user in users:
            self.session.add(user)
            
            await self.session.commit()

    async def update_user(self, user_id: str, update_user: UpdateUser):
        statement = select(User).where(User.user_id == user_id)
        result = await self.session.execute(statement)
        user_to_update = result.scalars().first()

        if not user_to_update or not update_user:
            return None
        
        # Update the user object
        update_data = update_user.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_to_update, key, value)

        await self.session.commit()
        await self.session.refresh(user_to_update)
        
        return user_to_update

    async def delete_user_by_id(self, user_id: str):
        query=delete(User).where(User.user_id == user_id)
        deleted_count = await self.session.execute(query)
        return deleted_count.rowcount

    async def delete_user_by_username(self, username: str):
        statement = delete(User).where(User.user_username == username)
        deleted_count = await self.session.execute(statement)
        return deleted_count.rowcount
            
    async def delete_user_by_email(self, email: str):
        statement = delete(User).where(User.user_email == email)
        deleted_count = await self.session.execute(statement)
        return deleted_count.rowcount

    async def update_user_active_status(self, user_id: str, new_status: bool):
        statement = select(User).where(User.user_id == user_id)
        result = await self.session.execute(statement)
        user = result.scalars().first()

        if user:
            user.user_is_active = new_status
            await self.session.commit()

            return user

    async def get_users(self, limit: int = 10, offset: int = 0):
        query = select(User).limit(limit).offset(offset)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return users

    async def get_user_roles(self, user_id: str):
        query = select(User).options(selectinload(User.user_roles))\
            .where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return [role for role in user.user_roles]
        return []

    async def get_users_by_role(self, role: Role):
        query = select(User).join(users_roles_association).join(Role)\
            .filter(Role.role_name == role.role_name)
        result = await self.session.execute(query)
        users_with_role = result.scalars().all()
        
        return users_with_role

    async def update_user_email(self, user_id: str, email: str):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            user.user_email = email
            await self.session.commit()
            return user

    async def update_user_password(self, user_id: str, password: str):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            user.user_hashed_password = hash_string(password)
            await self.session.commit()
            await self.session.refresh(user)
            return user

    async def update_user_username(self, user_id: str, username: str):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            user.user_username = username
            await self.session.commit()
            await self.session.refresh(user)
            return user

    async def update_user_roles(self, user_id: str, roles: List[Role]):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            user.user_roles = roles
            await self.session.commit()
            await self.session.refresh(user)
            return user

    async def is_user_active_by_id(self, user_id: str) -> bool:
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        return user.user_is_active if user else False
    
    async def is_user_active_by_username(self, user_name: str) -> bool:
        query = select(User).where(User.user_username == user_name)
        result = await self.session.execute(query)
        user = result.scalars().first()
        return user.user_is_active if user else False
    
    async def is_user_credentials_authentic(
        self, username: str, plain_password: str
    ) -> User:
        query = select(User).where(User.user_username == username)
        result = await self.session.execute(query)
        user = result.scalars().first()
        
        if not user:
            return False
        
        hashed_password = user.user_hashed_password
        return is_hash_from_string(plain_password, hashed_password)

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Retrieves all roles associated with a user.
        
        Args:
        """
        query = select(User).options(selectinload(User.user_roles))\
            .where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return [role for role in user.user_roles]
        return []

    async def has_user_roles(self, username: str, roles_names: List[str]) -> bool:
        user = await self.get_user_by_username(username)
        user_roles = await self.get_user_roles(user.user_id)
        
        user_roles_names = [
            user_role.role_name
            for user_role in user_roles
        ]

        return not set(roles_names).isdisjoint(set(user_roles_names))

    async def refresh_token_exists(self, token: str) -> Tuple[bool | None, User | None]:
        query = select(User).where(User.user_refresh_token == token)
        result = await self.session.execute(query)

        user = result.scalars().first()

        return user is not None, user

    async def update_user_last_login(self, username: str):
        query = select(User).where(User.user_username == username)
        result = await self.session.execute(query)
        user = result.scalars().first()

        if user:
            user.user_last_login_at = datetime.now()
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def update_user_access_token(self, username: str, access_token: str):
        query = select(User).where(User.user_username == username)
        result = await self.session.execute(query)
        user = result.scalars().first()

        if user:
            user.user_access_token = access_token
            await self.session.commit()
            await self.session.refresh(user)
            
        return user

    async def update_user_refresh_token(self, username: str, refresh_token: str):
        user = await self.get_user_by_username(username)
        if user:
            user.user_refresh_token = refresh_token
            await self.session.commit()
            await self.session.refresh(user)

@asynccontextmanager
async def get_user_repository():
    async with get_session() as session:
        yield UsersRepository(session)
