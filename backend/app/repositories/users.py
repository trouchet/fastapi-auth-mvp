from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Tuple
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager

from backend.app.utils.security import hash_string, is_hash_from_string
from backend.app.models.users import UpdateUser
from backend.app.database.models.users import User
from backend.app.database.instance import get_session

# Secutiry artifacts
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TokenDependency = Annotated[str, Depends(oauth2_scheme)]


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, username: str) -> User:
        async with self.session() as session:
            statement = select(User).where(User.user_username == username)
            result = await self.session.execute(statement)
            user = result.scalars().first()
            return user

    async def get_user_by_id(self, user_id: str) -> User:
        statement = select(User).where(User.user_id == user_id)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user

    async def get_user_by_email(self, email: str) -> User:
        statement = select(User).where(User.user_email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user

    async def get_user_by_username(self, username: str) -> User:
        statement = select(User).where(User.user_username == username)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return user

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.commit()

    async def update_user(self, user_id: str, update_user: UpdateUser):
        statement = select(User).where(User.user_id == user_id)
        result = await self.session.execute(statement)
        user_to_update = result.scalars().first()

        if not user_to_update:
            return None
        
        # Update the user object
        update_data = update_user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_to_update, key, value)

        await self.session.commit()
        await self.session.refresh(user_to_update)
        
        return user_to_update

    async def delete_user_by_id(self, user_id: str):
        statement = select(User).where(User.user_id == user_id)
        result = await self.session.execute(statement)
        user_to_delete = result.scalars().first()

        if user_to_delete:
            self.session.delete(user_to_delete)
            await self.session.commit()

    async def delete_user_by_username(self, username: str):
        statement = select(User).where(User.user_username == username)
        result = await self.session.execute(statement)
        user_to_delete = result.scalars().first()

        if user_to_delete:
            await self.session.delete(user_to_delete)
            await self.session.commit()
            
    async def delete_user_by_email(self, email: str):
        statement = select(User).where(User.user_email == email)
        result = await self.session.execute(statement)
        user_to_delete = result.scalars().first()

        if user_to_delete:
            await self.session.delete(user_to_delete)
            await self.session.commit()

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

    async def get_all_roles(self):
        query = select(User.roles).distinct()
        result = await self.session.execute(query)
        roles = [row[0] for row in result.unique().all()]
        return roles

    async def get_user_roles(self, user_id: str):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return user.user_roles

    async def get_users_by_role(self, role: str):
        query = select(User).filter(User.user_roles.contains([role]))
        result = await self.session.execute(query)
        users = result.scalars().all()
        return users

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
            return user

    async def update_user_username(self, user_id: str, username: str):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            user.user_username = username
            await self.session.commit()
            return user
        

    async def update_user_roles(self, user_id: str, roles: list):
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            user.user_roles = roles
            await self.session.commit()
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

    async def has_user_roles(self, username: str, roles: List[str]) -> bool:
        user = await self.get_user(username)
        return not set(roles).isdisjoint(set(user.user_roles))
    
    async def refresh_token_exists(self, token: str) -> Tuple[bool | None, User | None]:
        print(token)
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

        return user

    async def update_user_access_token(self, username: str, access_token: str):
        query = select(User).where(User.user_username == username)
        result = await self.session.execute(query)
        user = result.scalars().first()

        if user:
            user.user_access_token = access_token
            await self.session.commit()
            await self.session.refresh(user)

    async def update_user_refresh_token(self, username: str, refresh_token: str):
        user = await self.get_user_by_username(username)
        if user:
            user.user_refresh_token = refresh_token
            print(user.user_refresh_token)
            await self.session.commit()
            await self.session.refresh(user)

@asynccontextmanager
async def get_user_repository():
    async with get_session() as session:
        yield UsersRepository(session)
