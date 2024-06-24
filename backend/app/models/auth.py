from pydantic import BaseModel
from backend.app.config import settings

# Set cookie_secure to True if using HTTPS
is_cookie_secure = (not settings.ENVIRONMENT == "development")

class CsrfSettings(BaseModel):
    secret_key: str = settings.COOKIE_SECRET_KEY
    cookie_name: str = "csrftoken"
    cookie_samesite: str = "lax"
    cookie_secure: bool = is_cookie_secure
