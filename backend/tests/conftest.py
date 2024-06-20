import pytest
from passlib.context import CryptContext

from backend.app.auth import RoleChecker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture
def test_users_db():
    return []


@pytest.fixture
def test_refresh_tokens():
    return []


@pytest.fixture
def test_roles():
    return {
        "admin": 1,
        "user": 2
    }


@pytest.fixture
def test_allowed_roles(test_roles):
    return ["admin"]


@pytest.fixture
def test_user_checker(test_roles):
    return RoleChecker(['user'])


@pytest.fixture
def test_admin_checker(test_roles):
    return RoleChecker(['admin'])


def user_dict(
    username, 
    password, 
    email, 
    role: str = "user", 
    is_active: bool = True
):
    return {
        "username": username,
        "hashed_password": pwd_context.hash(password),
        "email": email,
        "role": role,
        "is_active": is_active
    }


@pytest.fixture
def user_password():
    return "secret_shh"


@pytest.fixture
def admin_password():
    return "another_secret_shh"


@pytest.fixture
def test_user(user_password):
    return user_dict(
        'user name', 
        user_password, 
        'user@mail.com', 
        'user'
    )


@pytest.fixture
def test_admin(user_admin_password):
    return user_dict(
        'admin name', 
        user_admin_password, 
        'admin@mail.com', 
        'admin'
    )

