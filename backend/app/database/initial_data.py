from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from psycopg2.errors import UniqueViolation

from backend.app.database.models.users import UserDB
from backend.app.config import settings
from backend.app.logging import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

first_admin_user = UserDB(
    user_id=uuid4(),
    user_created_at=datetime.now(),
    user_username=settings.FIRST_ADMIN_USERNAME,
    user_hashed_password=pwd_context.hash(settings.FIRST_ADMIN_PASSWORD),
    user_email=settings.FIRST_ADMIN_EMAIL,
    user_roles=["admin", "user"],
    user_is_active=True,
)

initial_users = [ first_admin_user ]

def insert_initial_users(database_):
    session = database_.session_maker()
    try:
        for user in initial_users:
            session.add(user)

        session.commit()
        logger.info("Initial users inserted successfully!")

    except (IntegrityError, UniqueViolation) as e:
        # Handle potential duplicate user errors (e.g., username or email already exist)
        logger.error(f"Duplicate entries found. Skipping...")
        session.rollback()  # Rollback changes if an error occurs

