from backend.app.utils.models import userbd_to_user, rolebd_to_role

def test_userbd_to_user(mock_user):
    result = userbd_to_user(mock_user)
    expected = {
        "user_id": mock_user.user_id,
        "user_created_at": mock_user.user_created_at,
        "user_updated_at": mock_user.user_updated_at,
        "user_username": mock_user.user_username,
        "user_email": mock_user.user_email,
        "user_is_active": mock_user.user_is_active,
    }
    assert result == expected

def test_rolebd_to_role(mock_role):
    result = rolebd_to_role(mock_role)
    expected = {
        "role_id": mock_role.role_id,
        "role_name": mock_role.role_name
    }
    assert result == expected