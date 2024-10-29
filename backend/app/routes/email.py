from fastapi import APIRouter, BackgroundTasks

from backend.app.services.email import (
    EmailSchema, 
    MessageSchema, 
    EmailService, 
)
from backend.app.dependencies.email import EmailServiceDependency
from backend.app.services.auth import role_checker
from .roles_bundler import user_management_roles

router=APIRouter(prefix='/email', tags=["E-mail"])

@router.post("/send")
@role_checker(user_management_roles)
async def send_in_background(
    background_tasks: BackgroundTasks, 
    email: EmailSchema,
    email_service: EmailServiceDependency
):
    try:
        email_service.send_message(email)
    except Exception as e:
        return {"message": f"Error: {str(e)}"}

    return {"message": "Email has been sent in the background"}


@router.post("/test-send")
@role_checker(user_management_roles)
async def send_in_background(
    background_tasks: BackgroundTasks, email: EmailSchema,
    email_service: EmailServiceDependency
):
    message = MessageSchema(
        subject="Test mail",
        recipients=[email.email],  # List of recipients, as many as you can pass 
        body=":)",
        subtype="plain"
    )

    email_service.send_message(message, background_tasks)

    return {"message": "Email has been sent in the background"}