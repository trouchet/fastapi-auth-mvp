from fastapi import BackgroundTasks, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from backend.app.models.email import EmailSchema
from backend.app.base.config import settings

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

class EmailService:
    def __init__(self):
        self.mail = FastMail(conf)

    async def send_message(
        self, email: EmailSchema, message: MessageSchema,
        background_tasks: BackgroundTasks
    ):
        background_tasks.add_task(self.mail.send_message, message)
        
def get_email_service_dependency():
    return EmailService()

