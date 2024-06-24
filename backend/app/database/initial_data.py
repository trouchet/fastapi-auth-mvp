from datetime import datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from backend.app.database.models.users import UserDB
from backend.app.logging import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

admin_user = UserDB(
    user_id=uuid4(),
    user_created_at=datetime.now(),
    user_username="admin_user",
    user_email="admin@example.com",
    user_hashed_password=pwd_context.hash("AdminPassword123!"),
    user_roles=["admin", "user"],
    user_is_active=True,
)

user_user = UserDB(
    user_id=uuid4(),
    user_created_at=datetime.now(),
    user_username="user",
    user_email="user@example.com",
    user_hashed_password=pwd_context.hash("UserPassword123!"),
    user_roles=["user"],
    user_is_active=True,
)

initial_users = [admin_user, user_user]

def insert_initial_users(database_):
    session = database_.session_maker()
    try:
        for user in initial_users:
            session.add(user)
        session.commit()
        logger.info("Initial users inserted successfully!")
    except IntegrityError as e:
        # Handle potential duplicate user errors (e.g., username or email already exist)
        logger.error(f"Error inserting users: {e}")
        session.rollback()  # Rollback changes if an error occurs
