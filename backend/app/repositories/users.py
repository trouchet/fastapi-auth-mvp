from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from backend.app.database.models.users import UserDB

# Secutiry artifacts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersRepository:
    def __init__(self, session):
        self.session = session

    def get_user(self, username: str) -> UserDB:
        query=self.session.query(UserDB)
        
        return query.filter(UserDB.username == username).first()

    def get_user_by_email(self, email: str) -> UserDB:
        query=self.session.query(UserDB)
        
        return query.filter(UserDB.email == email).first()

    def create_user(self, user: UserDB):
        self.session.add(user)
        self.session.commit()

    def update_user(self, user: UserDB):
        """
        Updates user information of user on database

        Args:
            user (UserDB): user under subject
        """
        self.session.commit()

    def delete_user(self, user: UserDB):
        self.session.delete(user)
        self.session.commit()

    def get_all_users(self):
        query=self.session.query(UserDB)
        
        return query.all() 
    
    def get_user_by_id(self, user_id: int) -> UserDB:
        query=self.session.query(UserDB)
        
        return query.filter(UserDB.id == user_id).first()
    
    def get_users_by_role(self, role: str):
        query=self.session.query(UserDB)
        
        return query.filter(UserDB.role == role).all()
    
    def is_user_active_by_id(self, user_id: int) -> bool:
        query=self.session.query(UserDB)
        
        user=query.filter(UserDB.id == user_id).first()
        
        return user.is_active
    
    def are_credentials_authentic(
        self, username: str, plain_password: str
    ) -> UserDB:
        user=self.get_user(username)
        hashed_password=user.hashed_password
        
        user_not_found=not user
        is_password_wrong=not pwd_context.verify(plain_password, hashed_password)
        
        invalid_authentication=user_not_found or is_password_wrong
        
        return not invalid_authentication
