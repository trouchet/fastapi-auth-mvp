from fastapi import APIRouter, BackgroundTasks

from backend.app.services.email import (
    EmailSchema, 
    MessageSchema, 
    EmailServiceDependency,
    EmailService, 
)

router=APIRouter(prefix='/email', tags=["E-mail"])

@router.post("/send")
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
