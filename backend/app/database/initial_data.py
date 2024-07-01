from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from backend.app.database.core import Database
from backend.app.database.models.users import User
from backend.app.utils.security import hash_string
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.data.auth import (
    ROLES_METADATA,
    INITIAL_USERS,
)

from .models.users import Role, Permission

# Function to create a new role with associated permissions
def create_role_with_permissions(session, role_name, permission_names):
    role = Role(name=role_name)
    for perm_name in permission_names:
        permission = session.query(Permission).filter_by(name=perm_name).first()
        if not permission:
            permission = Permission(name=perm_name)
        role.role_permissions.append(permission)
    session.add(role)
    session.commit()

# Create roles and permissions
def create_roles_and_permissions(session):
    for role, metadata in ROLES_METADATA.items():
        permissions=metadata['permissions']
        create_role_with_permissions(session, role, permissions)

# Insert initial users
def insert_initial_users(session):
    try:
        for user in INITIAL_USERS:
            session.add(user)

        session.commit()
        logger.info("Initial users inserted successfully!")

    except (IntegrityError, UniqueViolation):
        # Handle potential duplicate user errors (e.g., username or email already exist)
        logger.error("Duplicate entries found. Skipping...")
        session.rollback()  # Rollback changes if an error occurs

def insert_initial_data(database_: Database):
    session = database_.session_maker()

    # Insert initial roles, permissions and users
    create_roles_and_permissions(session)
    insert_initial_users(session)

    logger.info("Initial data inserted successfully!")
