from typing import List
from pydantic import BaseModel

class BaseUser(BaseModel):
    user_username: str | None = None
    user_roles: List[str] | None = None


class User(BaseUser):
    user_email: str | None = None
    user_is_active: bool| None = None


class CreateUser(User):
    user_hashed_password: str | None = None


class UpdateUser(CreateUser):
    pass


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None

