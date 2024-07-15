import pytest
from backend.app.models.users import UnhashedUpdateUser
from backend.app.utils.throttling import get_minute_rate_limiter

@pytest.mark.asyncio
async def test_get_all_roles(test_role_repository, new_role):
    roles=await test_role_repository.get_all_roles()
    assert len(roles) > 0
    assert new_role.role_name in [ role.role_name for role in roles ]


@pytest.mark.asyncio
async def test_create_role(test_role_repository, test_permission_repository, super_admin_role):
    rate_limit_dict=get_minute_rate_limiter(99999).to_dict()
    new_role_name = 'Unlimited'
    
    sadmin_permissions=await test_role_repository.get_permissions_by_role(super_admin_role)
    
    existing_new_role=await test_role_repository.get_role_by_name(new_role_name)

    if existing_new_role:
        await test_role_repository.delete_role(existing_new_role)

    roles=await test_role_repository.get_all_roles()
    sadmin_permission_names=[
        perm.perm_name for perm in sadmin_permissions
    ]
    
    
    new_role=await test_role_repository.create_role(new_role_name, rate_limit_dict, sadmin_permission_names)
    new_roles=await test_role_repository.get_all_roles()

    assert len(roles) == len(new_roles)-1
    
    assert new_role is not None
    assert new_role.role_name == 'Unlimited'
    assert new_role.role_rate_limit == rate_limit_dict
    
    await test_role_repository.delete_role(new_role)

def test_check_at_least_one_not_null():
    with pytest.raises(ValueError) as excinfo:
        UnhashedUpdateUser()
        
    exc_msg='At least one of fields'
    assert exc_msg in str(excinfo.value)

@pytest.mark.asyncio
async def test_permission_creation(test_permission_repository):
    permission_name = 'dummy_permission'

    permission=await test_permission_repository.get_permission_by_name(permission_name)

    if permission:
        await test_permission_repository.delete_permission(permission)

    dummy_permission=await test_permission_repository.create_permission(permission_name)
    assert dummy_permission.perm_name == permission_name

    await test_permission_repository.delete_permission(dummy_permission)

@pytest.mark.asyncio
async def test_get_permission_by_name(test_permission_repository):
    permission_name = 'manage_system'
    retrieved_permission=await test_permission_repository.get_permission_by_name(permission_name)
    
    assert retrieved_permission.perm_name == permission_name

@pytest.mark.asyncio
async def test_get_all_permissions(test_permission_repository):
    all_permissions=await test_permission_repository.get_all_permissions()
    assert len(all_permissions) > 0

# 44-49, 114, 167, 176, 190-191
# 44-49, 114, 167, 176, 190-191
