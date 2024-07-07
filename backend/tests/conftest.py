import pytest
from typing import Tuple, Dict, List
from unittest.mock import patch
from time import mktime
from uuid import uuid4

from backend.app.utils.security import hash_string
from backend.app.database.core import Database
from backend.app.database.models.users import User, Role
from backend.app.repositories.users import UsersRepository
from backend.app.repositories.auth import RoleRepository, PermissionRepository
from backend.app.database.initial_data import insert_initial_data
from backend.app.core.config import settings


@pytest.fixture
async def manage_database_connection():
    uri = settings.test_database_uri

    # Connect to your database
    database = Database(uri)

    try:
        await database.init()
        await insert_initial_data()

        yield database

    finally:
        await database.engine.dispose()

@pytest.fixture
async def test_session(manage_database_connection):
    """
    Provides an asynchronous database session.
    """
    session = manage_database_connection.session_maker()
    try:
        yield session
    finally:
        await session.aclose()


@pytest.fixture
async def test_user_repository(test_session):
    """
    Provides an asynchronous user repository.
    """
    try:
        yield UsersRepository(session=test_session)
    finally:
        await test_session.aclose()


@pytest.fixture
async def test_role_repository(test_session):
    try:
        yield RoleRepository(session=test_session)
    finally:
        await test_session.aclose()


@pytest.fixture
async def test_permission_repository(test_session):
    try:
        return PermissionRepository(session=test_session)
    finally:
        await test_session.aclose()


@pytest.fixture
def test_admin_data():
    return {
        "username": "admin_",
        "password": "Admin_password_shh123!",
        "email": "admin_@example.com"
    }


@pytest.fixture
def test_viewer_data():
    return {
        "username": "test_user",
        "password": "User_password_shh123!",
        "email": "test_@example.com"
    }
    
    
@pytest.fixture
def test_inactive_user_data():
    return {
        "username": "inactive_user",
        "password": "inactive@example.com",
        "email": "inactive@example.com",
        "is_active": False
    }


@pytest.fixture
async def super_admin_role(test_role_repository):
    super_admin_role = await test_role_repository.get_role_by_name("SuperAdmin")
    return super_admin_role


@pytest.fixture
async def admin_role(test_role_repository):
    admin_role = await test_role_repository.get_role_by_name("Admin")
    return admin_role


@pytest.fixture
async def viewer_role(test_role_repository):
    viewer_role = await test_role_repository.get_role_by_name("Viewer")
    return viewer_role


def user_factory(user_data: Dict, roles: List[Role]):
    return User(
        user_id=uuid4(),
        user_username=user_data['username'],
        user_email=user_data['email'],
        user_roles=roles,
        user_hashed_password=hash_string(user_data['password']),
        user_is_active=user_data.get("is_active", True),
    )


@pytest.fixture
async def test_super_admin(
    test_user_repository, super_admin_role, test_super_admin_data
):
    # Generate and insert test data
    super_admin_username = settings.FIRST_SUPER_ADMIN_USERNAME
    super_admin_user = await test_user_repository.get_user_by_username(super_admin_username)
    
    yield super_admin_user


@pytest.fixture
async def test_admin(test_user_repository, admin_role, test_admin_data):
    # Generate and insert test data
    admin_user = user_factory(test_admin_data, [admin_role])
    
    await test_user_repository.delete_user_by_username(admin_user.user_username)
    await test_user_repository.delete_user_by_email(admin_user.user_email)
    
    await test_user_repository.create_user(admin_user)
    yield admin_user
    await test_user_repository.delete_user_by_username(admin_user.user_username)


@pytest.fixture
async def test_viewer(test_user_repository, viewer_role, test_viewer_data):
    # Generate and insert test data
    viewer_user = user_factory(test_viewer_data, [viewer_role])

    await test_user_repository.delete_user_by_username(viewer_user.user_username)
    await test_user_repository.delete_user_by_email(viewer_user.user_email)

    await test_user_repository.create_user(viewer_user)
    yield viewer_user
    await test_user_repository.delete_user_by_username(viewer_user.user_username)


@pytest.fixture
async def test_inactive_user(test_user_repository, viewer_role, test_inactive_user_data):
    # Generate and insert test data
    inactive_user = user_factory(test_inactive_user_data, [viewer_role])

    await test_user_repository.delete_user_by_username(inactive_user.user_username)
    await test_user_repository.delete_user_by_email(inactive_user.user_email)
    
    await test_user_repository.create_user(inactive_user)
    yield inactive_user
    await test_user_repository.delete_user_by_username(inactive_user.user_username)


@pytest.fixture
def logs_foldername():
    return "log_tmp"


"""
def user_dict(
    username, password, email, roles: Set[str] = {"Admin"}, is_active: bool = True
):
    return {
        "username": username,
        "hashed_password": hash_string(password),
        "email": email,
        "roles": roles,
        "is_active": is_active,
    }
"""    

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
