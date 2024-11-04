from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from backend.app.database.models.users import User
from backend.app.utils.security import hash_string
from backend.app.base.config import settings
from backend.app.base.logging import logger
from backend.app.database.data.auth import ROLES_METADATA
from backend.app.repositories.auth import role_repository_async_context_manager
from backend.app.repositories.users import user_repository_async_context_manager


# Create roles and permissions
async def create_roles_and_permissions():
    async with role_repository_async_context_manager() as role_repository:
        for role_name, metadata in ROLES_METADATA.items():
            permissions = metadata['permissions']
            rate_limit_dict = metadata['rate_policy']

            try:
                await role_repository.create_role(
                    role_name, rate_limit_dict, permissions
                )

            except (IntegrityError, UniqueViolationError) as e:
                logger.warning(f"Unique violation for role '{role_name}'. Skipping...")
                await role_repository.session.rollback()

            except Exception as e:
                logger.error(f"An error occurred while creating role '{role_name}': {e}")
                await role_repository.session.rollback()


# Insert initial users
async def insert_initial_users():
    # Create the first admin user    
    async with role_repository_async_context_manager() as role_repository: 
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

    async with user_repository_async_context_manager() as user_repository:
        for user in initial_users:
            try:
                await user_repository.create_user(user)

            except (IntegrityError, UniqueViolationError):
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
