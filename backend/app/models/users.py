from pydantic import BaseModel, model_validator
from typing import Optional

from backend.app.utils.security import hash_string

class BaseUser(BaseModel):
    user_username: Optional[str] = None

class User(BaseUser):
    user_email: Optional[str] = None

class CreateUser(User):
    user_password: str

class UpdateUser(User):
    user_email: Optional[str] = None
    user_hashed_password: Optional[str] = None

class UnhashedUpdateUser(BaseUser):
    user_email: Optional[str] = None
    user_password: Optional[str] = None
    
    @model_validator(mode='before')
    def check_at_least_one_not_null(cls, values):
        field_names=['user_username', 'user_email', 'user_password']
        ', '.join(field_names)
        if not any(values.get(field_name) for field_name in field_names):
            raise ValueError('At least one of fields {field_names_str} must be provided')

        return values
    
    def to_update_user(self) -> UpdateUser:
        update_user_data = self.model_dump(exclude_unset=True)
        
        if 'user_password' in update_user_data:
            update_user_data['user_hashed_password'] = hash_string(update_user_data['user_password'])
            del update_user_data['user_password']

        return UpdateUser(**update_user_data)

class Token(BaseModel):
    access_token: str
    refresh_token: str