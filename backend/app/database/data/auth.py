
from backend.app.utils.throttling import (
    get_minute_rate_limiter
)
from typing import List

# Rate limiter policies
sloppy_rate=get_minute_rate_limiter(50)
loose_rate=get_minute_rate_limiter(40)
regular_rate=get_minute_rate_limiter(25)
strict_rate=get_minute_rate_limiter(10)

# Roles for business profiles 
PROFILES_METADATA = {
    "system_admin": {
        "roles": ["SuperAdmin", "Admin"]
    },
    "c_level": {
        "roles": ["Admin", "Moderator", "Editor", "Viewer"]
    },
    "recruiter": {
        "roles": ["Moderator", "Editor"]
    },
}

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

def get_combined_permissions(profile: str) -> List[str]:
    profile_data = PROFILES_METADATA.get(profile, {})
    roles = profile_data.get("roles", [])
    combined_permissions = set()
    
    for role in roles:
        role_data = ROLES_METADATA.get(role, {})
        role_permissions = role_data.get("permissions", [])
        combined_permissions.update(role_permissions)
    
    return list(combined_permissions)
