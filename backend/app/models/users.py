from pydantic import BaseModel

class BaseUser(BaseModel):
    user_username: str


class User(BaseUser):
    user_email: str
    user_password: str

class CreateUser(User):
    pass


class UpdateUser(CreateUser):
    pass


class Token(BaseModel):
    access_token: str
    refresh_token: str
