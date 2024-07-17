from fastapi import Depends 
from typing import Annotated

from backend.app.services.email import (
    EmailService, get_email_service_dependency,
)

EmailServiceDependency = Annotated[
    EmailService, Depends(get_email_service_dependency)
]