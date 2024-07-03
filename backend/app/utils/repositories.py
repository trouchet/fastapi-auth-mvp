from backend.app.data.auth import ROLES_METADATA
from backend.app.repositories.auth import get_permission_repository

def get_role_permissions(role_name: str):   
    role_metadata = ROLES_METADATA.get(role_name, None)
    
    if role_metadata:
        with get_permission_repository() as permission_repository: 
            permissions_list_str = role_metadata["permissions"]
            permissions=[
                permission_repository.get_permission_by_name(permission_str)
                for permission_str in permissions_list_str
            ]
            
        return permissions