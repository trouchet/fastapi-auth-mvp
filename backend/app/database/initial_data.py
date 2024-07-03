from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from backend.app.database.core import Database
from backend.app.database.models.users import User
from backend.app.utils.security import hash_string
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.data.auth import ROLES_METADATA
from backend.app.repositories.auth import (
    get_role_repository, get_permission_repository,
)
from backend.app.repositories.users import get_user_repo
from backend.app.repositories.auth import get_role_repository
from backend.app.utils.repositories import get_role_permissions

from .models.users import Role, Permission

# Create roles and permissions
def create_roles_and_permissions():
    with get_role_repository() as role_repository:
        for role_name, metadata in ROLES_METADATA.items():
            permissions=metadata['permissions']        
            
            try:
                role_repository.create_role(role_name, permissions)

            except (IntegrityError, UniqueViolation):
                # Handle potential duplicate role errors
                logger.warning(f"Duplicate entries found. Skipping role {role_name}...")
                
                # Rollback changes if an error occurs
                role_repository.session.rollback()

# Insert initial users
def insert_initial_users():    
    # Create the first admin user    
    with get_role_repository() as role_repository: 
        super_admin_role = role_repository.get_role_by_name("SuperAdmin")

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

    with get_user_repo() as user_repository:
        for user in initial_users:
            try:
                user_repository.create_user(user)

            except (IntegrityError, UniqueViolation):
                # Handle potential duplicate user errors
                logger.warning(f"Duplicate entries found. Skipping user {user}...")
                
                # Rollback changes if an error occurs
                user_repository.session.rollback()

    logger.info("Initial users inserted successfully!")

def insert_initial_data():
    # Insert initial roles, permissions and users
    create_roles_and_permissions()
    insert_initial_users()

    logger.info("Initial data inserted successfully!")
