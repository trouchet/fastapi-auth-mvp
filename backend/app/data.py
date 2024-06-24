from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = [
    {
        "username": "johndoe",
        "email": "john@emaik.com",
        "roles": ["user"],
        "hashed_password": pwd_context.hash("Secret_password_shh123!"),
        "is_active": True,
    },
    {
        "username": "alice",
        "email": "al8ce@emaik.com",
        "roles": ["admin", "user"],
        "hashed_password": pwd_context.hash("Another_password_shh123!"),
        "is_active": True,
    },
]

refresh_tokens = []
