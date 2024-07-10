from uuid import uuid4
from datetime import datetime

from backend.app.utils.throttling import (
    RateLimiterPolicy, get_minute_rate_limiter
)
from backend.app.database.models.users import User
from backend.app.database.models.auth import Role, Permission
from backend.app.core.config import settings
from backend.app.utils.security import hash_string

# Rate limiter policies
sloppy_rate=get_minute_rate_limiter(50)
loose_rate=get_minute_rate_limiter(40)
regular_rate=get_minute_rate_limiter(25)
strict_rate=get_minute_rate_limiter(10)

# System roles and associated permissions
ROLES_METADATA = {
    "SuperAdmin": {
        "permissions": [
            "manage_system", "manage_users", "manage_roles",
            "moderate_content", "create_content", "edit_content",
            "delete_content", "view_content", "submit_content", 
            "access_public_content"
        ],
        "rate_policy": sloppy_rate
    },
    "Admin": {
        "permissions": [
            "manage_users", "manage_roles",
            "create_content", "edit_content", "delete_content",
            "view_content", "submit_content", "access_public_content"
        ],
        "rate_policy": loose_rate
    },
    "Moderator": {
        "permissions": [
            "moderate_content", "view_content", "access_public_content"
        ],
        "rate_policy": regular_rate
    },
    "Editor": {
        "permissions": [
            "create_content", "edit_content", "delete_content",
            "view_content", "submit_content", "access_public_content"
        ],
        "rate_policy": regular_rate
    },
    "Viewer": {
        "permissions": [
            "view_content", "access_public_content"
        ],
        "rate_policy": strict_rate
    },
    "Contributor": {
        "permissions": [
            "submit_content", "view_content", "access_public_content"
        ],
        "rate_policy": strict_rate
    },
    "Guest": {
        "permissions": [
            "access_public_content"
        ],
        "rate_policy": strict_rate
    }
}

