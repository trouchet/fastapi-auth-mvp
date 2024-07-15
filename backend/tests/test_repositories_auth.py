import pytest
from backend.app.utils.throttling import get_minute_rate_limiter

@pytest.mark.asyncio
async def test_get_all_roles(test_role_repository, new_role):
    roles=await test_role_repository.get_all_roles()
    assert len(roles) > 0
    assert new_role.role_name in [ role.role_name for role in roles ]


@pytest.mark.asyncio
async def test_create_role(test_role_repository, test_permission_repository, super_admin_role):
    rate_limit_dict=get_minute_rate_limiter(99999).to_dict()

    sadmin_permissions=await test_role_repository.get_permissions_by_role(super_admin_role)

    roles=await test_role_repository.get_all_roles()
    sadmin_permission_names=[
        perm.perm_name for perm in sadmin_permissions
    ]
    
    new_role=await test_role_repository.create_role('Unlimited', rate_limit_dict, sadmin_permission_names)
    new_roles=await test_role_repository.get_all_roles()

    assert len(roles) == len(new_roles)-1
    
    assert new_role is not None
    assert new_role.role_name == 'Unlimited'
    assert new_role.role_rate_limit == rate_limit_dict
    
    test_role_repository.delete_role(new_role)
