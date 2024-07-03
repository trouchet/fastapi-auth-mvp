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


POSTGRES_DSN_SCHEME = "postgresql+asyncpg"

DEFAULT_POSTGRES_PASSWORD = "postgres"
DEFAULT_SECRET_KEY="secret_key_123"
DEFAULT_FIRST_SUPER_ADMIN_USERNAME="super_admin"
DEFAULT_FIRST_SUPER_ADMIN_PASSWORD="super_admin"
DEFAULT_FIRST_SUPER_ADMIN_EMAIL="super_admin@example.com"

# Token expiration times
DEFAULT_ACCESS_TIMEOUT_MINUTES = timedelta(minutes=30)
DEFAULT_REFRESH_TIMEOUT_MINUTES = timedelta(minutes=60)

# Project settings
with open("pyproject.toml", "r") as f:
    config = toml.load(f)


def string_has_token(string: str, token: str):
    # Regular expression to match 'docker' case-insensitively
    pattern = rf"(?i){token}"  # 'i' flag for case-insensitive matching

    # Check if the pattern matches anywhere in the string
    match = re.search(pattern, string)

    return match is not None


def validate_environment(environment):
    valid_environments = [
        "testing", "docker-dev", "docker-staging", "docker-prod",
    ]

    if environment not in valid_environments:
        raise ValueError(
            f"Invalid environment: {environment}. "
            f"Valid environments are: {valid_environments}"
        )
    else:
        return environment


def is_sandbox(environment: str):
    return string_has_token(environment, 'dev') or \
            string_has_token(environment, 'testing')


def is_docker(environment):
    return string_has_token(environment, 'docker')


def parse_cors(v: Any) -> Union[List[str], str]:
    maybe_list=not v.startswith("[") and not v.endswith("]")
    is_not_list=isinstance(v, str) and maybe_list
    if is_not_list:
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    
    raise ValueError(v)


# Settings class
class Settings(BaseSettings):
    """App settings."""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    VERSION: str = config["tool"]["poetry"]["version"]
    PROJECT_NAME: str = config["tool"]["poetry"]["name"]
    DESCRIPTION: str = config["tool"]["poetry"]["description"]
    API_V1_STR: str = "/api"
    ENVIRONMENT: Annotated[str, BeforeValidator(validate_environment)]

    APP_HOST: str = 'localhost'
    APP_PORT: int = 8000

    COOKIE_SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_ALGORITHM: str = 'HS256'
    
    FIRST_SUPER_ADMIN_USERNAME: str = DEFAULT_FIRST_SUPER_ADMIN_USERNAME
    FIRST_SUPER_ADMIN_PASSWORD: str = DEFAULT_FIRST_SUPER_ADMIN_PASSWORD
    FIRST_SUPER_ADMIN_EMAIL: str = DEFAULT_FIRST_SUPER_ADMIN_EMAIL

    DOMAIN: str = f"{APP_HOST}:{APP_PORT}"

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
        protocol = "http" if is_sandbox(self.ENVIRONMENT) else "https"
        return f"{protocol}://{self.DOMAIN}"

    @classmethod
    def get_redis_host(cls):
        return 'auth-redis' if is_docker(cls().ENVIRONMENT) else 'localhost'

    @classmethod
    def get_postgres_host(cls):
        return 'auth-db' if is_docker(cls().ENVIRONMENT) else 'localhost'

    # Database settings
    POSTGRES_DSN_SCHEME: str = POSTGRES_DSN_SCHEME
    
    @property
    def POSTGRES_HOST(self):
        return self.get_postgres_host()
    
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DBNAME: str = "auth_db"

    POSTGRES_HOST_TEST: str = 'localhost'
    POSTGRES_PORT_TEST: int = 5433
    POSTGRES_USER_TEST: str = 'postgres'
    POSTGRES_PASSWORD_TEST: str = 'postgres'
    POSTGRES_DBNAME_TEST: str = "auth_db"

    @property
    def REDIS_HOST(self):
        return self.get_redis_host()
    
    REDIS_PORT: int = 6379
    REDID_DB: int = 0

    @computed_field
    @property
    def database_uri(self) -> str:
        scheme=f"{POSTGRES_DSN_SCHEME}"
        credentials=f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
        url=f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DBNAME}"

        return f"{scheme}://{credentials}@{url}"
            
    @computed_field
    @property
    def redis_url(self) -> str:
        url = f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDID_DB}"
        return f"redis://{url}"
        
    @computed_field
    @property
    def test_database_uri(self) -> str:
        scheme=f"{POSTGRES_DSN_SCHEME}"
        credentials=f"{self.POSTGRES_USER_TEST}:{self.POSTGRES_PASSWORD_TEST}"
        url=f"{self.POSTGRES_HOST_TEST}:{self.POSTGRES_PORT_TEST}/{self.POSTGRES_DBNAME_TEST}"

        return f"{scheme}://{credentials}@{url}"

    def _warn_default_value(self, var_name: str, default_value: Any):
        environment = self.ENVIRONMENT
        message = (
            f'The value of {var_name} is "{default_value}", '
            "for security, please change it, at least for deployments."
        )

        if is_sandbox(environment):
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
