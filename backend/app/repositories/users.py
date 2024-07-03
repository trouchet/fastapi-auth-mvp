from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Tuple
from typing import List
from datetime import datetime

from backend.app.utils.security import hash_string, is_hash_from_string
from backend.app.models.users import UpdateUser
from backend.app.database.models.users import User
from backend.app.database.instance import get_session

# Secutiry artifacts
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TokenDependency = Annotated[str, Depends(oauth2_scheme)]


class UsersRepository:
    def __init__(self, session):
        self.session = session

    def get_user(self, username: str) -> User:
        query = self.session.query(User)

        return query.filter(User.user_username == username).first()

    def get_user_by_id(self, user_id: str) -> User:
        query = self.session.query(User)

        return query.filter(User.user_id == user_id).first()

    def get_user_by_email(self, email: str) -> User:
        query = self.session.query(User)

        return query.filter(User.user_email == email).first()

    def get_user_by_username(self, username: str) -> User:
        query=self.session.query(User)
        return query.filter(User.user_username == username).first()

    def create_user(self, user: User):

        self.session.add(user)
        self.session.commit()

    def update_user(self, user_id: str, update_user: UpdateUser):
        query=self.session.query(User)
        
        user_to_update=query.filter(User.user_id == user_id).first()
        
        if not user_to_update:
            return None
        
        # Iterate over the fields in the Pydantic model and update the SQLAlchemy model
        update_data = update_user.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_to_update, key, value)

        self.session.commit()
        self.session.refresh()
        
        return user_to_update  

    def delete_user_by_id(self, user_id: str):
        query = self.session.query(User)

        query.filter(User.user_id == user_id).delete()
        self.session.commit()

    def delete_user_by_username(self, username: str):
        query = self.session.query(User)

        query.filter(User.user_username == username).delete()
        self.session.commit()

    def update_user_active_status(self, user_id: str, new_status: bool):
        query=self.session.query(UserDB)
        
        user=query.filter(User.user_id == user_id).first()
        
        if user:
            user.user_is_active=new_status
        
            self.session.commit()

            return user

    def get_users(self, limit: int = 10, offset: int = 0):
        query = self.session.query(User)

        return query.limit(limit).offset(offset).all()

    def get_all_roles(self):
        query = self.session.query(User)

        return query.with_entities(User.roles).distinct().all()

    def get_user_roles(self, user_id: str):
        query=self.session.query(User)

        user=query.filter(User.user_id == user_id).first()
        
        if user:
            return user.user_roles
            

    def get_users_by_role(self, role: str):
        query = self.session.query(User)
        has_role = User.user_roles.contains([role])

        return query.filter(has_role).all()

    def update_user_email(self, user_id: str, email: str):
        query = self.session.query(User)

        user = query.filter(UserDB.user_id == user_id).first()
        
        if user:
            user.user_email = email
            self.session.commit()

            return user

    def update_user_password(self, user_id: str, password: str):
        query = self.session.query(User)

        user = query.filter(UserDB.user_id == user_id).first()
        
        if user:
            user.user_hashed_password = hash_string(password)
            self.session.commit()

            return user

    def update_user_username(self, user_id: str, username: str):
        query=self.session.query(User)
        
        user=query.filter(UserDB.user_id == user_id).first()
        
        if user:
            user.user_username=username
            self.session.commit()

            return user
        

    def update_user_roles(self, user_id: str, roles: list):
        query = self.session.query(User)

        user = query.filter(UserDB.user_id == user_id).first()
        
        if user:
            user.user_roles = roles
            self.session.commit()

            return user


    def is_user_active_by_id(self, user_id: str) -> bool:
        query=self.session.query(User)
        
        user=query.filter(User.user_id == user_id).first()
        
        return user.user_is_active
    
    def is_user_active_by_username(self, user_name: str) -> bool:
        query=self.session.query(User)
        
        user=query.filter(User.user_username == user_name).first()
        
        return user.user_is_active
    
    def is_user_credentials_authentic(
        self, username: str, plain_password: str
    ) -> User:
        user = self.get_user(username)
        hashed_password = user.user_hashed_password

        user_not_found = not user
        is_password_wrong = not is_hash_from_string(plain_password, hashed_password)

        invalid_authentication = user_not_found or is_password_wrong

        return not invalid_authentication

    def has_user_roles(self, username: str, roles: List[str]) -> bool:
        user=self.get_user(username)
        
        return set(roles).isdisjoint(set(user.user_roles)) is False
    
    def refresh_token_exists(self, token: str) -> Tuple[bool | None, User | None]:
        query = self.session.query(User)

        user = query.filter(User.user_refresh_token == token).first()

        return user is not None, user

    def update_user_last_login(self, username: str):
        user = self.get_user_by_username(username)

        user.user_last_login_at = datetime.now()
        self.session.commit()

        return user

    def update_user_access_token(self, username: str, access_token: str):
        user = self.get_user_by_username(username)
        user.user_access_token = access_token
        self.session.commit()

        return user

    def update_user_refresh_token(self, username: str, refresh_token: str):
        user = self.get_user_by_username(username)
        user.user_refresh_token = refresh_token
        self.session.commit()

        return user


def get_user_repo():
    session = get_session()
    return UsersRepository(session)
