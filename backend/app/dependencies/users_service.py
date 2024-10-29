from fastapi import Depends
from typing import Annotated

from backend.app.services.users import (
    get_users_service, UserService, 
)

UsersServiceDependency=Annotated[UserService, Depends(get_users_service)]

