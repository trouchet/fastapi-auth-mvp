import pytest

from uuid import uuid4

from backend.app.utils.security import hash_string
from backend.app.database.models.users import User


def test_user_strings():
    new_user = User(
        user_username='test_user',
        user_hashed_password=hash_string('Secret_password_123'),
        user_email='test@example.com',
    )
    assert new_user.__repr__() == "User(test_user)"
    assert new_user.__str__() == "User(test_user)"

def test_user_equality():
    new_user = User(
        user_username='test_user',
        user_hashed_password=hash_string('Secret_password_123'),
        user_email='test@example.com',
    )
    
    assert new_user.__repr__() == "User(test_user)"