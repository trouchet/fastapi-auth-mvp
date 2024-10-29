from backend.app.database.models.users import User
from backend.app.database.models.auth import Role

def userbd_to_user(user: User):
    return {
        "user_id": user.user_id,
        "user_created_at": user.user_created_at,
        "user_updated_at": user.user_updated_at,
        "user_username": user.user_username,
        "user_email": user.user_email,
        "user_is_active": user.user_is_active,
    }
    
def rolebd_to_role(role: Role):
    return {
        "role_id": role.role_id,
        "role_name": role.role_name
    }
