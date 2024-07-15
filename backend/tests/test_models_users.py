from backend.app.models.users import UnhashedUpdateUser

def test_to_update_user():
    test_user=UnhashedUpdateUser(
        user_username='test_user',
        user_email='test@example.com',
        user_password='Test_123!'
    )
    
    hashed_test_user=test_user.to_update_user()
    
    assert test_user.user_password != hashed_test_user.user_hashed_password