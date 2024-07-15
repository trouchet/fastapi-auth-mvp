import pytest
from fastapi.testclient import TestClient
from typing import Tuple, Dict, List, Generator
from unittest.mock import patch
from time import mktime
from uuid import uuid4
from asyncio import new_event_loop, AbstractEventLoop, get_event_loop_policy
from contextlib import contextmanager
from asyncpg.exceptions import PostgresConnectionError
from collections.abc import AsyncIterator, Iterator

from backend.app.database.models.base import Base
from backend.app.utils.throttling import get_minute_rate_limiter
from backend.app.utils.security import hash_string
from backend.app.database.core import Database
from backend.app.database.models.users import User
from backend.app.database.models.auth import Role 
from backend.app.repositories.users import UsersRepository
from backend.app.repositories.auth import RoleRepository, PermissionRepository
from backend.app.data.auth import ROLES_METADATA
from backend.app.database.initial_data import insert_initial_data
from backend.app.base.config import settings
from backend.app.main import app


@pytest.fixture(scope="session")
def event_loop(request: pytest.FixtureRequest) -> Iterator[AbstractEventLoop]:
    event_loop_policy = get_event_loop_policy()
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

def test_client():
    return TestClient(app)

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
async def test_super_admin_data():
    return {
        "username": "super_admin_",
        "password": "Super_Admin_password_shh123!",
        "email": "super_admin_@example.com"
    }
    

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
        "username": "test_viewer",
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
def test_dummy_data():
    return {
        "username": "dummy_user",
        "email": "dummy@example.com",
        "password": "dummy_password",
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
async def new_role(test_role_repository):
    permission_names = ["access_public_content"]
    rate_limit = get_minute_rate_limiter(1)
    rate_limit_dict=rate_limit.to_dict()
    
    role_name="Banned"

    existing_role = await test_role_repository.get_role_by_name(role_name)
    if(not existing_role):
        existing_role = await test_role_repository.create_role(role_name, rate_limit_dict, permission_names)

    yield existing_role
    await test_role_repository.delete_role(existing_role)


@pytest.fixture
async def viewer_role(test_role_repository):
    viewer_role = await test_role_repository.get_role_by_name("Viewer")
    return viewer_role


def user_factory(user_data: Dict, roles: List[Role]):
    return User(
        user_id=str(uuid4()),
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
async def dummy_user(test_user_repository, test_dummy_data, admin_role):
    dummy_user=user_factory(test_dummy_data, [admin_role])
    await test_user_repository.delete_user_by_username(dummy_user.user_username)
    await test_user_repository.delete_user_by_email(dummy_user.user_email)
    
    await test_user_repository.create_user(dummy_user)
    yield dummy_user
    await test_user_repository.delete_user_by_username(dummy_user.user_username)


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
async def test_users(
    test_super_admin, test_admin, test_viewer, test_inactive_user
):
    return [
        test_super_admin, test_admin, test_viewer, test_inactive_user
    ]
    


@pytest.fixture
def logs_foldername():
    return "log_tmp"


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

    with patch("backend.app.utils.logging.strftime", side_effect=strftime) as mock_strftime:
        yield mock_strftime
