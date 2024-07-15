from fastapi import APIRouter, BackgroundTasks

from backend.app.services.email import (
    EmailSchema, 
    MessageSchema, 
    EmailService,
)
from backend.app.dependencies.email import EmailServiceDependency
from backend.app.core.auth import role_checker
from .roles_bundler import user_management_roles

router=APIRouter(prefix='/email', tags=["E-mail"])

@router.post("/send")
@role_checker(user_management_roles)
async def send_in_background(
    background_tasks: BackgroundTasks, 
    email: EmailSchema,
    email_service: EmailService = EmailServiceDependency
):
    message = MessageSchema(
        subject="FastAPI Mail Module",
        recipients=[email.email],  # List of recipients, as many as you can pass 
        body="This is a test email sent from FastAPI",
        subtype="plain"
    )

    background_tasks.add_task(email_service.send_message, message)

    return {"message": "Email has been sent in the background"}
