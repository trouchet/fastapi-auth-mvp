from fastapi import BackgroundTasks, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List

from backend.app.base.config import settings

class EmailSchema(BaseModel):
    emails: List[EmailStr]

class EmailService:
    def __init__(self):
        conf = ConnectionConfig(
            MAIL_USERNAME = settings.MAIL_USERNAME,
            MAIL_PASSWORD = settings.MAIL_PASSWORD,
            MAIL_FROM = settings.MAIL_FROM,
            MAIL_PORT = settings.MAIL_PORT,
            MAIL_SERVER = settings.MAIL_SERVER,
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS = False,
            USE_CREDENTIALS = True,
            VALIDATE_CERTS = True
        )
        
        self.mail = FastMail(conf)

    def send_message(
        self, message: MessageSchema, background_tasks: BackgroundTasks):
        background_tasks.add_task(self.mail.send_message, message)
        
def get_email_service_dependency():
    return EmailService()
        
EmailServiceDependency = Depends(get_email_service_dependency)