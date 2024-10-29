
from backend.app.utils.throttling import (
    get_minute_rate_limiter
)

# Rate limiter policies
sloppy_rate=get_minute_rate_limiter(50).to_slowapi_format()
loose_rate=get_minute_rate_limiter(40).to_slowapi_format()
regular_rate=get_minute_rate_limiter(25).to_slowapi_format()
strict_rate=get_minute_rate_limiter(10).to_slowapi_format()

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