import pytest
from backend.app.models.users import Token, User
from backend.app.repositories.users import UsersRepository
from backend.app.services.auth import JWTService, get_jwt_service
from backend.app.base.auth import create_token
from backend.app.base.config import settings

@pytest.mark.asyncio
async def test_login_for_access_token(
    auth_client, test_super_admin_data, test_super_admin
):
    signup_data={
        "username": test_super_admin_data['username'], 
        "password": test_super_admin_data['password']
    }
    
    route=f"{settings.API_V1_STR}/auth/token"
    response = await auth_client.post(route, data=signup_data)

    assert response.status_code == 200
    token = Token(**response.json())
    assert token.access_token
    assert token.refresh_token

@pytest.mark.asyncio
async def test_refresh_access_token(
    auth_client, test_super_admin_data
):
    signup_data={
        "username": test_super_admin_data['username'], 
        "password": test_super_admin_data['password']
    }
    
    route=f"{settings.API_V1_STR}/auth/token"
    
    response = await auth_client.post(route, data=signup_data)
    
    token = Token(**response.json())
    auth_data={"refresh_token": token.refresh_token}
    
    route=f"{settings.API_V1_STR}/auth/refresh"
    
    response = await auth_client.post(route, json=auth_data)
    print(response.json())
    assert response.status_code == 200
    token = Token(**response.json())
    
    assert token.access_token
    assert token.refresh_token
