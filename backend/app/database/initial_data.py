from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from backend.app.database.models.users import User
from backend.app.utils.security import hash_string
from backend.app.base.config import settings
from backend.app.base.logging import logger
from backend.app.data.auth import ROLES_METADATA
from backend.app.repositories.auth import get_role_repository
from backend.app.repositories.users import get_users_repository


# Create roles and permissions
async def create_roles_and_permissions():
    async with get_role_repository() as role_repository:
        for role_name, metadata in ROLES_METADATA.items():
            permissions=metadata['permissions']
            rate_limit_dict=metadata['rate_policy'].to_dict()
            
            try:
                await role_repository.create_role(role_name, rate_limit_dict, permissions)

            except (IntegrityError, UniqueViolation):
                # Handle potential duplicate role errors
                logger.warning(f"Duplicate entries found. Skipping role {role_name}...")
                
                # Rollback changes if an error occurs
                await role_repository.session.rollback()

# Insert initial users
async def insert_initial_users():
    # Create the first admin user    
    async with get_role_repository() as role_repository: 
        super_admin_role = await role_repository.get_role_by_name("SuperAdmin")

    first_super_admin_user = User(
        user_id=uuid4(),
        user_created_at=datetime.now(),
        user_username=settings.FIRST_SUPER_ADMIN_USERNAME,
        user_hashed_password=hash_string(settings.FIRST_SUPER_ADMIN_PASSWORD),
        user_email=settings.FIRST_SUPER_ADMIN_EMAIL,
        user_roles=[super_admin_role],
        user_is_active=True,
    )

    initial_users = [ first_super_admin_user ]

    async with get_users_repository() as user_repository:
        for user in initial_users:
            try:
                await user_repository.create_user(user)

            except (IntegrityError, UniqueViolation):
                # Handle potential duplicate user errors
                if settings.ENVIRONMENT != 'testing':
                    logger.warning(f"Duplicate entries found. Skipping user {user}...")

                # Rollback changes if an error occurs
                await user_repository.session.rollback()

    logger.info("Initial users inserted successfully!")

async def insert_initial_data():
    # Insert initial roles, permissions and users
    await create_roles_and_permissions()
    await insert_initial_users()
