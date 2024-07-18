

from backend.app.utils.security import hash_string
from backend.app.database.models.auth import Permission, Role, Profile
from backend.app.utils.throttling import get_minute_rate_limiter

def test_auth_reprs():
    new_permission = Permission(
        perm_name='test_permission'
    )
    
    new_role = Role(
        role_name='test_role', 
        role_rate_limit=get_minute_rate_limiter(10).to_dict()
    )
    new_profile = Profile(prof_name='test_profile')
    assert new_permission.__repr__() == "Permission(test_permission)"
    assert new_permission.__str__() == "Permission(test_permission)"
    assert new_role.__repr__() == "Role(test_role)"
    assert new_role.__str__() == "Role(test_role)"
    assert new_profile.__repr__() == "Profile(test_profile)"
    assert new_profile.__str__() == "Profile(test_profile)"


