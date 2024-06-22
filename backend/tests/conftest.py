import pytest
from passlib.context import CryptContext
from typing import Set
from os import getcwd 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture
def test_users_db():
    return []


@pytest.fixture
def test_refresh_tokens():
    return []


@pytest.fixture
def logs_foldername():
    return 'logs'


def user_dict(
    username, password, email, roles: Set[str] = {"user"}, is_active: bool = True
):
    return {
        "username": username,
        "hashed_password": pwd_context.hash(password),
        "email": email,
        "roles": roles,
        "is_active": is_active
    }


@pytest.fixture
def test_user_password():
    return "secret_shh"


@pytest.fixture
def test_admin_password():
    return "another_secret_shh"


@pytest.fixture
def test_user(test_user_password):
    return user_dict(
        'user name', test_user_password, 'user@mail.com', {'user'}
    )


@pytest.fixture
def test_admin(test_admin_password):
    return user_dict(
        'admin name', test_admin_password, 'admin@mail.com', {'admin'}
    )

@pytest.fixture
def tmp_path():
    return getcwd()
