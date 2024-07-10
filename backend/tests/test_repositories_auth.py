import pytest

async def test_get_all_roles(test_role_repository, new_role):
    roles=await test_role_repository.get_all_roles()
    assert len(roles) > 0
    assert new_role.role_name in [ role.role_name for role in roles ]
