from fastapi import Depends

from backend.app.services.email import get_email_service_dependency

EmailServiceDependency = Depends(get_email_service_dependency)