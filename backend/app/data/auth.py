from uuid import uuid4
from datetime import datetime

from backend.app.utils.throttling import (
    RateLimiterPolicy, get_minute_rate_limiter
)
from backend.app.database.models.users import User, Role
from backend.app.core.config import settings
from backend.app.utils.security import hash_string

# System roles and associated permissions
ROLES_METADATA = {
    "SuperAdmin": {
        "permissions": [
            "manage_system", "manage_users", "manage_roles",
            "moderate_content", "create_content", "edit_content",
            "delete_content", "view_content", "submit_content", 
            "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(50)
    },
    "Admin": {
        "permissions": [
            "manage_users", "manage_roles",
            "create_content", "edit_content", "delete_content",
            "view_content", "submit_content", "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(40)
    },
    "Moderator": {
        "permissions": [
            "moderate_content", "view_content", "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(25)
    },
    "Editor": {
        "permissions": [
            "create_content", "edit_content", "delete_content",
            "view_content", "submit_content", "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(10)
    },
    "Viewer": {
        "permissions": [
            "view_content", "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(5)
    },
    "Contributor": {
        "permissions": [
            "submit_content", "view_content", "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(5)
    },
    "Guest": {
        "permissions": [
            "access_public_content"
        ],
        "rate_policy": get_minute_rate_limiter(3)
    }
}

