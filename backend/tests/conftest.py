import pytest
from passlib.context import CryptContext
from typing import Set, Tuple
from unittest.mock import patch
from os import getcwd 
from time import mktime

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

@pytest.fixture
def test_time_tuple():
    return (2000, 1, 1, 0, 0, 0, 0, 0, 0)

# Mock time-related functions (replace with actual logic if needed)
@pytest.fixture
def mock_time_functions(test_time_tuple):
    def gmtime(timestamp):
        return test_time_tuple

    def localtime(timestamp):
        return test_time_tuple

    def time():
        return mktime(test_time_tuple)

    with \
        patch("backend.app.utils.logging.time", side_effect=time) as mock_time, \
        patch("backend.app.utils.logging.localtime", side_effect=localtime), \
        patch("backend.app.utils.logging.gmtime", side_effect=gmtime):
        yield mock_time

@pytest.fixture
def test_time_tuple():
    return (2000, 1, 1, 0, 0, 0, 0, 0, 0)


@pytest.fixture
def test_current_time(test_time_tuple):
    return mktime(test_time_tuple)


# Mock strftime function
@pytest.fixture
def mock_strftime():
    def strftime(suffix: str, time_tuple: Tuple[int]):
        from time import strftime
        return strftime("%Y-%m-%d", time_tuple)

    with patch(\
        "backend.app.utils.logging.strftime", \
        side_effect=strftime \
    ) as mock_strftime:
        yield mock_strftime

