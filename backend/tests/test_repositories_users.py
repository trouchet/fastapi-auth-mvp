import pytest
from uuid import uuid4

from backend.app.base.config import settings
from backend.app.models.users import UpdateUser
from backend.app.services.auth import create_token

from .conftest import user_factory 


@pytest.mark.asyncio
async def test_get_user_by_username(test_user_repository):
    user_username = settings.FIRST_SUPER_ADMIN_USERNAME
    user_by_username = await test_user_repository.get_user_by_username(user_username)
    user_by_id = await test_user_repository.get_user_by_id(user_by_username.user_id)

    assert user_by_id == user_by_username
    
@pytest.mark.asyncio
async def test_get_user_id_by_username(test_user_repository):
    user_username = settings.FIRST_SUPER_ADMIN_USERNAME
    user_id_by_username = await test_user_repository.get_user_id_by_username(
        user_username
    )
    user_by_id = await test_user_repository.get_user_by_id(user_id_by_username)

    assert user_by_id.user_id == user_id_by_username

@pytest.mark.asyncio
async def test_get_user_by_email(test_user_repository):
    user_email = settings.FIRST_SUPER_ADMIN_EMAIL
    user_by_email = await test_user_repository.get_user_by_email(user_email)
    user_by_id = await test_user_repository.get_user_by_id(user_by_email.user_id)

    assert user_by_id == user_by_email

@pytest.mark.asyncio
async def test_get_user_id_by_email(test_user_repository):
    user_email = settings.FIRST_SUPER_ADMIN_EMAIL
    user_id_by_email = await test_user_repository.get_user_id_by_email(user_email)
    user_by_id = await test_user_repository.get_user_by_id(user_id_by_email)

    assert user_by_id.user_id == user_id_by_email
    
@pytest.mark.asyncio
async def test_update_user(test_user_repository, test_viewer):
    test_user_id = test_viewer.user_id
    update_user=UpdateUser(
        user_username=test_viewer.user_username,
        user_email="new_mail@example.com",
        user_hashed_password=test_viewer.user_hashed_password
    )

    updated_user = await test_user_repository.update_user(test_user_id, update_user)

    assert updated_user.user_email == update_user.user_email

@pytest.mark.asyncio
async def test_update_password(test_user_repository, test_viewer):
    new_password='New_password_123'
    user=await test_user_repository.update_user_password(
        test_viewer.user_id, new_password
    )
    
    assert await test_user_repository.is_user_credentials_authentic(
        user.user_username, new_password
    )

@pytest.mark.asyncio
async def test_update_user_with_none_user(test_user_repository, test_viewer):
    test_user_id = test_viewer.user_id
    update_user=None

    updated_user = await test_user_repository.update_user(test_user_id, update_user)

    assert updated_user is None

@pytest.mark.asyncio
@pytest.mark.parametrize("new_status", [False, True])
async def test_update_status_user(test_user_repository, test_viewer, new_status):
    test_user_id = test_viewer.user_id
    
    updated_user = await test_user_repository.update_user_active_status(test_user_id, new_status)
    assert updated_user.user_is_active == new_status

@pytest.mark.asyncio
async def test_update_user_email(test_user_repository, test_viewer):
    test_user_id = test_viewer.user_id
    old_email = test_viewer.user_email
    new_email = "new_email@example.com"
    
    updated_user = await test_user_repository.update_user_email(test_user_id, new_email)
    
    assert updated_user.user_email == new_email
    
    updated_user = await test_user_repository.update_user_email(test_user_id, old_email)
    
    assert updated_user.user_email == old_email
    
    
@pytest.mark.asyncio
async def test_update_user_username(test_user_repository, test_viewer):
    test_user_id = test_viewer.user_id
    old_username = test_viewer.user_username
    new_username = "new_username"
        
    updated_user = await test_user_repository.update_user_username(test_user_id, new_username)
    
    assert updated_user.user_username == new_username
    
    updated_user = await test_user_repository.update_user_username(test_user_id, old_username)
    
    assert updated_user.user_username == old_username


@pytest.mark.asyncio
async def test_create_users(test_user_repository, test_dummy_data, admin_role):
    dummy_user=user_factory(test_dummy_data, [admin_role])
    await test_user_repository.delete_user_by_email(dummy_user.user_email)

    await test_user_repository.create_users([dummy_user])
    
    user=await test_user_repository.get_user_by_username(dummy_user.user_username)
    assert user
    await test_user_repository.delete_user_by_username(dummy_user.user_username)

@pytest.mark.asyncio
async def test_user_has_roles(test_user_repository, test_viewer, admin_role):
    roles=await test_user_repository.get_user_roles(test_viewer.user_id)
    role_names=[role.role_name for role in roles]
    
    assert await test_user_repository.has_user_roles(
        test_viewer.user_username, role_names
    )
    assert not await test_user_repository.has_user_roles(
        test_viewer.user_username, [admin_role.role_name]
    )
    
@pytest.mark.asyncio
async def test_get_user_roles(test_user_repository, test_viewer):
    viewer_roles=await test_user_repository.get_user_roles(test_viewer.user_id)
    assert len(viewer_roles) == 1

@pytest.mark.asyncio
async def test_delete_user_by_id(test_user_repository, test_viewer):
    test_user_id = test_viewer.user_id
    
    deleted_count = await test_user_repository.delete_user_by_id(test_user_id)
    
    assert deleted_count == 1
    
    user=await test_user_repository.get_user_by_id(test_user_id)
    
    assert user is None

@pytest.mark.asyncio
async def test_delete_user_by_email(test_user_repository, test_viewer):
    test_user_email = test_viewer.user_email
    
    deleted_count = await test_user_repository.delete_user_by_email(test_user_email)
    
    assert deleted_count == 1
    
    user=await test_user_repository.get_user_by_email(test_user_email)
    
    assert user is None


@pytest.mark.asyncio
async def test_get_all_users(test_user_repository, test_users):
    users=await test_user_repository.get_users()
    assert len(users) == len(test_users)+1


@pytest.mark.asyncio
async def test_get_users_by_role(test_user_repository, super_admin_role):
    users=await test_user_repository.get_users_by_role(super_admin_role)
    assert len(users) == 1


@pytest.mark.asyncio
async def test_get_user_roles(test_user_repository, test_admin):
    roles=await test_user_repository.get_user_roles(test_admin.user_id)
    assert len(roles) == 1
    
@pytest.mark.asyncio
async def test_get_user_roles_unknown_id(test_user_repository):
    roles = await test_user_repository.get_user_roles(uuid4())
    
    assert roles == []

@pytest.mark.asyncio
async def test_is_user_active_by_id(test_user_repository, test_viewer):
    is_active=await test_user_repository.is_user_active_by_id(test_viewer.user_id)
    assert is_active

@pytest.mark.asyncio
async def test_is_user_active_by_username(test_user_repository, test_viewer):
    is_active=await test_user_repository.is_user_active_by_username(
        test_viewer.user_username
    )
    
    assert is_active

@pytest.mark.asyncio
async def test_is_user_credentials_authentic(test_user_repository):
    is_authentic=await test_user_repository.is_user_credentials_authentic(
        'unknown_user', 'password_shh123'
    )
    
    assert not is_authentic

@pytest.mark.asyncio
async def test_user_access_token(test_user_repository, test_viewer):
    new_access_token=create_token({})
    updated_user=await test_user_repository.update_user_access_token(
        test_viewer.user_username, new_access_token
    )
    
    assert updated_user.user_access_token == new_access_token

@pytest.mark.asyncio
async def test_update_user_last_login(test_user_repository, dummy_user):
    last_login_at=dummy_user.user_last_login_at

    updated_user=await test_user_repository.update_user_last_login(
        dummy_user.user_username
    )

    assert last_login_at is not updated_user.user_last_login_at


