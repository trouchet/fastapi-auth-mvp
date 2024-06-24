from fastapi import HTTPException, status

class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class CSRFProtectException(HTTPException):
    def __init__(self, error: str):
        super().__init__(
            status_code=status.HTTP_403_UNAUTHORIZED,
            detail="CSRF token is invalid",
        )

class InactiveUserException(HTTPException):
    def __init__(self, username):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {username} is inactive ",
        )

class PrivilegesException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="You don't have enough permissions",
        )

class InexistentUsernameException(HTTPException):
    def __init__(self, username):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username {username} does not exist",
        )

class ExistentUsernameException(HTTPException):
    def __init__(self, username):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username {username} already exists",
        )

class ExistentEmailException(HTTPException):
    def __init__(self, email):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} already exists",
        )

class InexistentUserIDException(HTTPException):
    def __init__(self, user_id):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User ID {user_id} does not exist",
        )

class IncorrectPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )


class IncorrectCurrentPasswordException(IncorrectPasswordException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current password is incorrect",
        )

class ExpiredTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token has expired.",
        )


class ExpiredRefreshTokenException(ExpiredTokenException):
    def __init__(self):
        detail=super().detail+" Please log in again to obtain a new token."
        
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class LastAdminRemovalException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't remove the last admin",
        )