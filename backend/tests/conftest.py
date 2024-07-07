import pytest
from passlib.context import CryptContext
from typing import Set, Tuple
from unittest.mock import patch
from os import getcwd
from time import mktime
from uuid import uuid4
from contextlib import contextmanager

from backend.app.utils.security import hash_string
from backend.app.database.core import Database
from backend.app.database.models.users import User, Role
from backend.app.repositories.users import UsersRepository
from backend.app.repositories.auth import (
    RoleRepository, PermissionRepository
)
from backend.app.core.config import settings
from backend.app.database.initial_data import insert_initial_data

@pytest.fixture
def test_database():
    # Connect to your database
    database = Database(settings.test_database_uri)
    database.init()
    insert_initial_data()

    yield database
    database.engine.dispose()  # Teardown logic to close all connections

@pytest.fixture
def test_session(test_database):
    session = test_database.session_maker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user_repository(test_session):
    try:
        yield UsersRepository(session=test_session)
    finally:
        test_session.close()
    

@pytest.fixture
def test_role_repository(test_session):
    try:
        yield RoleRepository(session=test_session)
    finally:
        test_session.close()


@pytest.fixture
def test_permission_repository(test_session):
    try:
        yield PermissionRepository(session=test_session)
    finally:
        test_session.close()
    

@pytest.fixture
def test_user_password():
    return "User_password_shh123!"


@pytest.fixture
def test_admin_password():
    return "Admin_password_shh123!"


@pytest.fixture
def super_admin_role(test_role_repository):
    super_admin_role = test_role_repository.get_role_by_name("SuperAdmin")
    
    return super_admin_role


@pytest.fixture
def admin_role(test_role_repository):
    admin_role = test_role_repository.get_role_by_name("Admin")
    
    return admin_role


@pytest.fixture
def viewer_role(test_role_repository):
    viewer_role = test_role_repository.get_role_by_name("Viewer")
    
    return viewer_role


@pytest.fixture
def test_user_repository(test_session):
    try:
        yield UsersRepository(session=test_session)
    finally:
        test_session.close()

@pytest.fixture
def test_user(test_user_repository, super_admin_role, test_user_password):
    # Generate and insert test data
    user = User(
        user_id=uuid4(),
        user_username="test_user",
        user_email="test_@example.com",
        user_roles=[super_admin_role],
        user_hashed_password=hash_string(test_user_password),
        user_is_active=True,
    )

    test_user_repository.create_user(user)
    yield user  # Provide test data to the test
    test_user_repository.delete_user_by_username(user.user_username)


@pytest.fixture
def test_inactive_user(test_user_repository, viewer_role, test_user_password):
    # Generate and insert test data
    inactive_user = User(
        user_id=uuid4(),
        user_username="inactive_",
        user_email="inactive@example.com",
        user_roles=[viewer_role],
        user_hashed_password=hash_string(test_user_password),
        user_is_active=False,
    )

    test_user_repository.create_user(inactive_user)
    yield inactive_user
    test_user_repository.delete_user_by_username(inactive_user.user_username)


@pytest.fixture
def test_admin(test_session, admin_role, test_admin_password):
    # Generate and insert test data
    admin = User(
        user_id=uuid4(),
        user_username="admin_",
        user_email="admin_@example.com",
        user_roles=[admin_role],
        user_hashed_password=hash_string(test_admin_password),
        user_is_active=True,
    )
    test_session.add(admin)
    test_session.commit()
    yield admin
    test_session.delete(admin)
    test_session.commit()


@pytest.fixture
def logs_foldername():
    return "log_tmp"


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

    with patch("backend.app.utils.logging.time", side_effect=time) as mock_time, \
        patch("backend.app.utils.logging.localtime", side_effect=localtime), \
        patch("backend.app.utils.logging.gmtime", side_effect=gmtime):
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
