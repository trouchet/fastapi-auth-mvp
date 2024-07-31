from fastapi import FastAPI, Request

from backend.app.utils.request import get_route_and_token, list_routes

def test_get_route_and_token(utils_client):
    # Create a mock request with headers
    response = utils_client.get("/test-route", headers={"Authorization": "Bearer test_token"})
    
    # Create a mock Request object
    request = Request(scope={
        'type': 'http',
        'method': 'GET',
        'path': '/test-route',
        'headers': [
            (b'authorization', b'Bearer test_token'),
        ]
    })
    
    route, token = get_route_and_token(request)
    
    assert route == '/test-route'
    assert token == 'test_token'

def test_list_routes(utils_app):
    print(utils_app)
    # Retrieve route information
    routes = list_routes(utils_app)
    
    # Expected route information
    expected_routes = [
        {"path": "/test-route", "name": "Test Route", "methods": {"GET"}},
        {"path": "/another-route", "name": "Another Route", "methods": {"POST"}},
    ]
    
    # Check if the returned routes match the expected routes
    assert routes == expected_routes