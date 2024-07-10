from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr

class EmailSchema(BaseModel):
    email: EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME = "your_email@example.com",
    MAIL_PASSWORD = "your_password",
    MAIL_FROM = "your_email@example.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.example.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

class EmailService:
    def __init__(self):
        self.mail = FastMail(conf)

    async def send_message(self, email: EmailSchema, background_tasks: BackgroundTasks):
        message = MessageSchema(
            subject="FastAPI Mail Module",
            recipients=[email.email],
            body="This is a test email sent from FastAPI using the FastAPI Mail module."
        )

        background_tasks.add_task(self.mail.send_message, message)
        
def get_email_service_dependency():
    return EmailService()
        
EmailServiceDependency = Depends(get_email_service_dependency)