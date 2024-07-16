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
            detail="You don't have enough permissions to a access this resource",
        )


class InexistentUsernameException(HTTPException):
    def __init__(self, username):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
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


class MissingTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ExpiredTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token has expired. Please log in again to obtain a new token.",
        )


class MissingRequiredClaimException(HTTPException):
    def __init__(
        self,
        claim: str,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token is missing required claim: {claim}",
        )

class MalformedTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token is malformed. Please log in again to obtain a new token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TooManyRequestsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )


class LastAdminRemovalException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't remove the last admin",
        )


class InvalidPasswordException(HTTPException):
    def __init__(self, invalidation_dict):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=invalidation_dict,
        )


class InvalidEmailException(HTTPException):
    def __init__(self, email):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} is invalid",
        )


class InvalidUUIDException(HTTPException):
    def __init__(self, uuid):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"String {uuid} is an invalid UUID",
        )


class InvalidRouteException(HTTPException):
    def __init__(self, route):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Route {route} is invalid",
        )
        
        
class DuplicateEntryException(HTTPException):
    def __init__(self, classifier, entry):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{classifier} {entry} already exists",
        )


class InternalDatabaseError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error",
        )