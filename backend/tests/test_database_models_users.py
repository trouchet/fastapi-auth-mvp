

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

def test_user_repr():
    new_user = User(
        user_username='test_user',
        user_hashed_password=hash_string('Secret_password_123'),
        user_email='test@example.com',
    )
    
    assert new_user.__repr__() == "User(test_user)"

def test_user_equality():
    new_user_1 = User(
        user_username='test_user_1',
        user_hashed_password=hash_string('Secret_password_123_1'),
        user_email='test_1@example.com',
    )
    new_user_2 = User(
        user_username='test_user_2',
        user_hashed_password=hash_string('Secret_password_123_2'),
        user_email='test_2@example.com',
    )
    new_user_3 = User(
        user_username='test_user_3',
        user_hashed_password=hash_string('Secret_password_123_2'),
        user_email='test_1@example.com',
    )
    new_user_4 = User(
        user_username='test_user_2',
        user_hashed_password=hash_string('Secret_password_123_2'),
        user_email='test_4@example.com',
    )
    assert new_user_1 != new_user_2
    assert new_user_1 == new_user_3
    assert new_user_2 == new_user_4 