from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from backend.app.database.core import Database
from backend.app.database.models.users import User
from backend.app.utils.security import hash_string
from backend.app.core.config import settings
from backend.app.core.logging import logger

from .models.users import Role, Permission

# System roles and associated permissions
ROLES_PERMISSIONS = {
    "SuperAdmin": [
        "manage_system", "manage_users", "manage_roles",
        "moderate_content", "create_content", "edit_content",
        "delete_content", "view_content", "submit_content", 
        "access_public_content"
    ],
    "Admin": [
        "manage_users", "manage_roles",
        "create_content", "edit_content", "delete_content",
        "view_content", "submit_content", "access_public_content"
    ],
    "Moderator": [
        "moderate_content", "view_content", "access_public_content"
    ],
    "Editor": [
        "create_content", "edit_content", "delete_content",
        "view_content", "submit_content", "access_public_content"
    ],
    "Viewer": [
        "view_content", "access_public_content"
    ],
    "Contributor": [
        "submit_content", "view_content", "access_public_content"
    ],
    "Guest": [
        "access_public_content"
    ]
}

# Function to create a new role with associated permissions
def create_role_with_permissions(session, role_name, permission_names):
    role = Role(name=role_name)
    for perm_name in permission_names:
        permission = session.query(Permission).filter_by(name=perm_name).first()
        if not permission:
            permission = Permission(name=perm_name)
        role.permissions.append(permission)
    session.add(role)
    session.commit()

# Create roles and permissions
def create_roles_and_permissions(session):
    for role, permissions in ROLES_PERMISSIONS.items():
        create_role_with_permissions(session, role, permissions)

# Insert initial users
def insert_initial_users(session):
    # Create the first admin user
    first_super_admin_user = User(
        user_id=uuid4(),
        user_created_at=datetime.now(),
        user_username=settings.FIRST_ADMIN_USERNAME,
        user_hashed_password=hash_string(settings.FIRST_ADMIN_PASSWORD),
        user_email=settings.FIRST_ADMIN_EMAIL,
        user_roles=["SuperAdmin", "Admin"],
        user_is_active=True,
    )

    initial_users = [ first_super_admin_user ]

    try:
        for user in initial_users:
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
