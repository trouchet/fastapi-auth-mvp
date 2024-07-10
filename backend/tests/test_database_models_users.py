import pytest

from uuid import uuid4

from backend.app.utils.security import hash_string
from backend.app.data.auth import ROLES_METADATA
from backend.app.database.models.users import User
from backend.app.database.models.auth import Permission


def test_user_strings():
    new_user = User(
        user_username='test_user',
        user_hashed_password=hash_string('Secret_password_123'),
        user_email='test@example.com',
    )
    assert new_user.__repr__() == "User(test_user)"
    assert new_user.__str__() == "User(test_user)"

def test_user_repr():
    new_user = User(
        user_username='test_user',
        user_hashed_password=hash_string('Secret_password_123'),
        user_email='test@example.com',
    )
    
    assert new_user.__repr__() == "User(test_user)"


def test_user_has_roles(test_viewer):
    assert test_viewer.has_roles(('Viewer',)) == True
    assert test_viewer.has_roles(('Admin',)) == False
    assert test_viewer.has_roles(('Viewer', 'Admin')) == False


async def test_get_permissions(test_viewer, test_session):
    assert await test_viewer.get_permissions(test_session) == {"view_content", "access_public_content"}
