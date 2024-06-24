# Description: Constants for the application.
from datetime import timedelta

# Constants for the application.
POSSIBLE_ROLES_SET = {"admin", "user"}

# Token expiration times
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 20
DEFAULT_REFRESH_TOKEN_EXPIRE_MINUTES = 120

DEFAULT_ACCESS_TIMEOUT_MINUTES = timedelta(minutes=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)
DEFAULT_REFRESH_TIMEOUT_MINUTES = timedelta(
    minutes=DEFAULT_REFRESH_TOKEN_EXPIRE_MINUTES
)
