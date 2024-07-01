from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    model_validator,
)

from typing import Union, Annotated, Any, List, Tuple
from typing_extensions import Self
from datetime import timedelta
import re
from warnings import warn
import toml


POSTGRES_DSN_SCHEME = "postgresql+psycopg2"

DEFAULT_POSTGRES_PASSWORD = "postgres"
DEFAULT_SECRET_KEY="secret_key_123"
DEFAULT_FIRST_SUPER_ADMIN_USERNAME="admin"
DEFAULT_FIRST_SUPER_ADMIN_PASSWORD="admin"
DEFAULT_FIRST_SUPER_ADMIN_EMAIL="admin@example.com"

# Token expiration times
DEFAULT_ACCESS_TIMEOUT_MINUTES = timedelta(minutes=30)
DEFAULT_REFRESH_TIMEOUT_MINUTES = timedelta(minutes=60)

# Project settings
with open("pyproject.toml", "r") as f:
    config = toml.load(f)

def parse_cors(v: Any) -> Union[List[str], str]:
    maybe_list=not v.startswith("[") and not v.endswith("]")
    is_not_list=isinstance(v, str) and maybe_list
    if is_not_list:
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    
    raise ValueError(v)

def string_has_token(string: str, token: str):
    # Regular expression to match 'docker' case-insensitively
    pattern = rf"(?i){token}"  # 'i' flag for case-insensitive matching

    # Check if the pattern matches anywhere in the string
    match = re.search(pattern, string)

    return match is not None

# Settings class
class Settings(BaseSettings):
    """App settings."""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    VERSION: str = config["tool"]["poetry"]["version"]
    PROJECT_NAME: str = config["tool"]["poetry"]["name"]
    DESCRIPTION: str = config["tool"]["poetry"]["description"]
    API_V1_STR: str = "/api"
    
    APP_PORT: int = 8000

    COOKIE_SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_ALGORITHM: str = 'HS256'
    
    FIRST_SUPER_ADMIN_USERNAME: str = DEFAULT_FIRST_SUPER_ADMIN_USERNAME
    FIRST_SUPER_ADMIN_PASSWORD: str = DEFAULT_FIRST_SUPER_ADMIN_PASSWORD
    FIRST_SUPER_ADMIN_EMAIL: str = DEFAULT_FIRST_SUPER_ADMIN_EMAIL

    ENVIRONMENT: str = "development"
    DOMAIN: str = f"localhost:{APP_PORT}"

    # 1 day
    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = DEFAULT_ACCESS_TIMEOUT_MINUTES
    REFRESH_TOKEN_EXPIRE_MINUTES: timedelta = DEFAULT_REFRESH_TIMEOUT_MINUTES

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        Union[List[AnyUrl], str], BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        protocol = "http" if self.ENVIRONMENT == "development" else "https"
        return f"{protocol}://{self.DOMAIN}"

    # Database settings
    POSTGRES_DSN_SCHEME: str = POSTGRES_DSN_SCHEME
    
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DBNAME: str = "auth_db"
    
    POSTGRES_HOST_TEST: str = 'localhost'
    POSTGRES_PORT_TEST: int = 5433
    POSTGRES_USER_TEST: str = 'postgres'
    POSTGRES_PASSWORD_TEST: str = 'postgres'
    POSTGRES_DBNAME_TEST: str = "auth_db"

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDID_DB: int = 0

    @computed_field
    @property
    def database_uri(self) -> str:
        return (
            f"{POSTGRES_DSN_SCHEME}://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DBNAME}"
        )
    
    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDID_DB}"
        
    @computed_field
    @property
    def test_database_uri(self) -> str:
        return (
            f"{POSTGRES_DSN_SCHEME}://"
            f"{self.POSTGRES_USER_TEST}:{self.POSTGRES_PASSWORD_TEST}@"
            f"{self.POSTGRES_HOST_TEST}:{self.POSTGRES_PORT_TEST}/{self.POSTGRES_DBNAME_TEST}"
        )

    def _warn_default_value(self, var_name: str, default_value: Any):
        environment = self.ENVIRONMENT
        message = (
            f'The value of {var_name} is "{default_value}", '
            "for security, please change it, at least for deployments."
        )
        
        is_default_safe=string_has_token(environment, 'dev') or \
            string_has_token(environment, 'testing')
        
        if is_default_safe:
            warn(message, stacklevel=1)
        else:
            raise ValueError(message)

    def _check_default_values(
        self, default_tuples: List[Tuple[str, Any, Any]] = None
    ) -> None:
        for var_name, value, default_value in default_tuples:
            if value == default_value:
                self._warn_default_value(var_name, value)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        default_tuples = [
            ("JWT_SECRET_KEY", self.JWT_SECRET_KEY, DEFAULT_SECRET_KEY),
            ("COOKIE_SECRET_KEY", self.COOKIE_SECRET_KEY, DEFAULT_SECRET_KEY),
            ("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD, DEFAULT_POSTGRES_PASSWORD),
            ("FIRST_SUPER_ADMIN_USERNAME", self.FIRST_SUPER_ADMIN_USERNAME, DEFAULT_FIRST_SUPER_ADMIN_USERNAME),
            ("FIRST_SUPER_ADMIN_PASSWORD", self.FIRST_SUPER_ADMIN_PASSWORD, DEFAULT_FIRST_SUPER_ADMIN_PASSWORD),
            ("FIRST_SUPER_ADMIN_EMAIL", self.FIRST_SUPER_ADMIN_EMAIL, DEFAULT_FIRST_SUPER_ADMIN_EMAIL),
        ]
        
        self._check_default_values(default_tuples)

        return self


# Instantiate settings
settings = Settings()

# Set postgres host as 'auth-db' if environment has '*docker*'
if string_has_token(settings.ENVIRONMENT, 'docker'):
    settings.POSTGRES_HOST = 'auth-db'
