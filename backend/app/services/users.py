from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from asyncpg.exceptions import UniqueViolationError

from typing import List, Dict, Annotated

from backend.app.services.auth import role_checker
from backend.app.dependencies.auth import CurrentUserDependency
from backend.app.database.models.users import User
from backend.app.repositories.users import UsersRepository
from backend.app.base.exceptions import (
    InexistentUserIDException,
    InactiveUserException,
    IncorrectCurrentPasswordException,
    LastAdminRemovalException,
    InvalidEmailException,
    InvalidUUIDException,
    InvalidPasswordException,
)
from backend.app.models.users import (
    User, UnhashedUpdateUser, CreateUser,
)
from backend.app.database.models.auth import Role
from backend.app.utils.security import (
    is_password_valid, 
    apply_password_validity_dict, 
    is_email_valid,
    is_valid_uuid,
)
from backend.app.repositories.users import UsersRepository
from backend.app.dependencies.users import UsersRepositoryDependency

from backend.app.repositories.auth import RoleRepository
from backend.app.base.exceptions import (
    DuplicateEntryException, InternalDatabaseError,
)

from backend.app.utils.security import hash_string
from .roles_bundler import (
    user_management_roles,
    user_viewer_roles,
    user_editor_roles,
)

router = APIRouter(prefix='/users', tags=["Users"])

def userbd_to_user(user: User):
    return {
        "user_id": user.user_id,
        "user_created_at": user.user_created_at,
        "user_updated_at": user.user_updated_at,
        "user_username": user.user_username,
        "user_email": user.user_email,
        "user_is_active": user.user_is_active,
    }
    
def rolebd_to_role(role: Role):
    return {
        "role_id": role.role_id,
        "role_name": role.role_name,
        "role_description": role.role_description,
    }

class UserService:
    def __init__(
        self, 
        user_repository: UsersRepository,
        role_repository: RoleRepository
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def read_all_users(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        users = await self.user_repository.get_users(limit=limit, offset=offset)

        users_obj=list(map(userbd_to_user, users))

        return users_obj


    async def read_user_by_id(self, user_id: str):
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        user = await self.user_repository.get_user_by_id(user_id)
        
        if not user:
            raise InexistentUserIDException(user_id)

        user_obj=userbd_to_user(user)
    
        return user_obj


    async def delete_user(self, user_id: str):
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        user=await self.user_repository.get_user_by_id(user_id)

        if not user:
            raise InexistentUserIDException(user_id)

        admin_users=self.user_repository.get_users_by_role("admin")
        last_admin=len(admin_users)==1
        last_admin_candidate = admin_users[0]
        this_last_admin=str(last_admin_candidate.user_id)==user_id
        
        forbidden_remove_last_admin=last_admin and this_last_admin

        if forbidden_remove_last_admin:
            raise LastAdminRemovalException()

        self.user_repository.delete_user_by_id(user_id)
        
        message_dict={"message": f"User {user_id} deleted successfully"}
        serialized_msg=jsonable_encoder(message_dict)
        
        return JSONResponse(content=serialized_msg)


    async  def update_user(self, user_id: str, update_user_info: UnhashedUpdateUser) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        if not update_user_info:
            raise InexistentUserIDException(user_id)
        
        update_user_info.to_update_user()

        admin_users=await self.user_repository.get_users_by_role("admin")
        last_admin=len(admin_users)==1
        last_admin_candidate = admin_users[0]
        this_last_admin=last_admin_candidate.user_id==user_id

        forbidden_remove_last_admin=last_admin and this_last_admin

        if forbidden_remove_last_admin:
            raise LastAdminRemovalException()

        updated_user=await self.user_repository.update_user(update_user_info)
        serialized_updt_user=jsonable_encoder(dict(updated_user))
        
        return JSONResponse(content=serialized_updt_user)


    async def create_user(self, user: CreateUser) -> Dict:
        new_user = User(
            user_username=user.user_username,
            user_hashed_password=hash_string(user.user_password),
            user_email=user.user_email,
        )
        
        user = await self.user_repository.create_user(new_user)
        
        return userbd_to_user(user)


    async def signup(self, new_user_info: CreateUser) -> Dict:
        new_user = User(
            user_username=new_user_info.user_username,
            user_hashed_password=hash_string(new_user_info.user_password),
            user_email=new_user_info.user_email,
        )

        try:
            user = await self.user_repository.create_user(new_user)
        except UniqueViolationError:
            raise DuplicateEntryException('User', new_user_info.user_username)
        except Exception as e:
            raise InternalDatabaseError()
        
        return userbd_to_user(user)


    async def update_user(self, user_id: str, user: UnhashedUpdateUser) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)

        user = await self.user_repository.update_user(user_id, user)

        if user:
            raise InexistentUserIDException(user_id)
        else:
            return userbd_to_user(user)


    async def update_username(self, user_id: str, new_username: str) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        user = await self.user_repository.update_user_username(user_id, new_username)

        if user:
            return userbd_to_user(user)
        else:
            raise InexistentUserIDException(user_id)


    async def update_email(self, user_id: str, new_email: str) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        if not is_email_valid(new_email):
            raise InvalidEmailException(new_email)
        
        user = await self.user_repository.update_user_email(user_id, new_email)

        if user:
            return userbd_to_user(user)
        else:
            raise InexistentUserIDException(user_id)


    async def update_password(self, user_id: str, old_password: str, new_password: str) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        if not is_password_valid(new_password):
            invalidation_dict=apply_password_validity_dict(new_password)
            raise InvalidPasswordException(invalidation_dict)

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise InexistentUserIDException(user_id)

        if not user.user_is_active:
            raise InactiveUserException(user.user_username)

        is_authentic = await self.user_repository.is_user_credentials_authentic(
            user.user_username, old_password
        )

        if(is_authentic):
            user = await self.user_repository.update_user_password(user_id, new_password)
        else:
            raise IncorrectCurrentPasswordException()

        return userbd_to_user(user)

    async def get_user_roles_by_id(self, user_id: str) -> List[str]:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        roles=await self.user_repository.get_user_roles_by_id(user_id)
        
        if not roles:
            raise InexistentUserIDException(user_id) 
        else:
            return list(map(rolebd_to_role, roles))

    async def activate_user(self, user_id: str) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)

        user = await self.user_repository.update_user_active_status(user_id, True)

        if user:
            return userbd_to_user(user)
        else:
            raise InexistentUserIDException(user_id)


    async def deactivate_user(self, user_id: str) -> Dict:
        if not is_valid_uuid(user_id): 
            raise InvalidUUIDException(user_id)
        
        user = await self.user_repository.update_user_active_status(user_id, False)

        if user:
            return userbd_to_user(user)
        else:
            raise InexistentUserIDException(user_id)


    async def get_users_by_role(
        self, role: str, limit: int = 10, offset: int = 0
    ) -> List[Dict]:
        users = await self.user_repository.get_users_by_role(role)

        return list(map(userbd_to_user, users))
    

def get_users_service(user_repo: UsersRepositoryDependency) -> UserService:
    return UserService(user_repo)


UsersServiceDependency=Annotated[UserService, Depends(get_users_service)]
