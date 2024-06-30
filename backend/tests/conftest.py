import pytest
from passlib.context import CryptContext
from typing import Set, Tuple
from unittest.mock import patch
from os import getcwd
from time import mktime
from uuid import uuid4

from backend.app.utils.security import hash_string
from backend.app.database.core import Database
from backend.app.database.models.users import User
from backend.app.repositories.users import UsersRepository
from backend.app.core.config import settings


@pytest.fixture
def test_database():
    uri = settings.test_database_uri
    
    # Connect to your database
    database = Database(uri)
    yield database
    database.engine.dispose()  # Teardown logic to close all connections


@pytest.fixture
def test_user_repository(test_database):
    session = test_database.session_maker()

    yield UsersRepository(session)


@pytest.fixture
def session(test_database):
    session = test_database.session_maker()
    yield session
    session.close()  # Teardown logic to close session


@pytest.fixture
def test_user_password():
    return "User_password_shh123!"


@pytest.fixture
def test_admin_password():
    return "Admin_password_shh123!"


@pytest.fixture
def test_user(session, test_user_password):
    # Generate and insert test data
    user = User(
        user_id=uuid4(),
        user_username="test_",
        user_email="test_@example.com",
        user_roles=["SuperAdmin"],
        user_hashed_password=hash_string(test_user_password),
        user_is_active=True,
    )
    session.add(user)
    session.commit()
    yield user  # Provide test data to the test
    session.delete(user)
    session.commit()


@pytest.fixture
def test_inactive_user(session, test_user_password):
    # Generate and insert test data
    inactive_user = User(
        user_id=uuid4(),
        user_username="inactive_",
        user_email="inactive@example.com",
        user_roles=["user"],
        user_hashed_password=hash_string(test_user_password),
        user_is_active=False,
    )
    session.add(inactive_user)
    session.commit()
    yield inactive_user
    session.delete(inactive_user)
    session.commit()


@pytest.fixture
def test_admin(session, test_admin_password):
    # Generate and insert test data
    admin = User(
        user_id=uuid4(),
        user_username="admin_",
        user_email="admin_@example.com",
        user_roles=["SuperAdmin", "user"],
        user_hashed_password=hash_string(test_admin_password),
        user_is_active=True,
    )
    session.add(admin)
    session.commit()
    yield admin
    session.delete(admin)
    session.commit()


@pytest.fixture
def test_users_db():
    return []


@pytest.fixture
def test_refresh_tokens():
    return []


@pytest.fixture
def logs_foldername():
    return "logs"


def user_dict(
    username, password, email, roles: Set[str] = {"user"}, is_active: bool = True
):
    return {
        "username": username,
        "hashed_password": hash_string(password),
        "email": email,
        "roles": roles,
        "is_active": is_active,
    }


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

    with patch("backend.app.utils.logging.time", side_effect=time) as mock_time, patch(
        "backend.app.utils.logging.localtime", side_effect=localtime
    ), patch("backend.app.utils.logging.gmtime", side_effect=gmtime):
        yield mock_time


@pytest.fixture
def test_current_time(test_time_tuple):
    return mktime(test_time_tuple)


# Mock strftime function
@pytest.fixture
def mock_strftime():
    def strftime(suffix: str, time_tuple: Tuple[int]):
        from time import strftime

        return strftime("%Y-%m-%d", time_tuple)

    with patch(
        "backend.app.utils.logging.strftime", side_effect=strftime
    ) as mock_strftime:
        yield mock_strftime

@pytest.fixture
def tmp_path():
    return 'tmp/'
