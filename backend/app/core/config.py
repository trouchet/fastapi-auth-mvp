from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    model_validator,
)

from typing import (
    Literal, Union, Annotated, Any, List,
)
from typing_extensions import Self
from datetime import timedelta

from warnings import warn
import toml

POSTGRES_DSN_SCHEME = "postgresql+psycopg2"

DEFAULT_POSTGRES_PASSWORD = "postgres"
DEFAULT_SECRET_KEY="secret_key_123"
DEFAULT_FIRST_ADMIN_USERNAME="admin"
DEFAULT_FIRST_ADMIN_PASSWORD="admin"
DEFAULT_FIRST_ADMIN_EMAIL="admin@example.com"

DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
DEFAULT_REFRESH_TOKEN_EXPIRE_MINUTES = 120

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


def warn_default_value(environment, var_name, default_value):
    message = (
        f'The value of {var_name} is "{default_value}", '
        "for security, please change it, at least for deployments."
    )
    if environment == "development":
        warn(message, stacklevel=1)
    else:
        raise ValueError(message)

# Settings class
class Settings(BaseSettings):
    """App settings."""

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True, 
        extra="ignore"
    )

    VERSION: str = config["tool"]["poetry"]["version"]
    PROJECT_NAME: str = config["tool"]["poetry"]["name"]
    DESCRIPTION: str = config["tool"]["poetry"]["description"]
    API_V1_STR: str = "/api"
    
    APP_PORT: int = 8000

    COOKIE_SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_ALGORITHM: str = 'HS256'
    
    FIRST_ADMIN_USERNAME: str = DEFAULT_FIRST_ADMIN_USERNAME
    FIRST_ADMIN_PASSWORD: str = DEFAULT_FIRST_ADMIN_PASSWORD
    FIRST_ADMIN_EMAIL: str = DEFAULT_FIRST_ADMIN_EMAIL

    ENVIRONMENT: str = "development"
    DOMAIN: str = f"localhost:{APP_PORT}"

    # 1 day
    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(minutes=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)
    REFRESH_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(minutes=DEFAULT_REFRESH_TOKEN_EXPIRE_MINUTES)

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
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DBNAME: str = "auth_db"

    def database_uri(self) -> str:
        return (
            f"{POSTGRES_DSN_SCHEME}://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DBNAME}"
        )

    def _check_default_value(
        self, 
        var_name: str, 
        value: Union[str, None],
        default_value: str
    ) -> None:
        if value == default_value:
            warn_default_value(self.ENVIRONMENT, var_name, value)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_value("JWT_SECRET_KEY", self.JWT_SECRET_KEY, DEFAULT_SECRET_KEY)
        self._check_default_value("COOKIE_SECRET_KEY", self.COOKIE_SECRET_KEY, DEFAULT_SECRET_KEY)
        self._check_default_value("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD, DEFAULT_POSTGRES_PASSWORD)
        self._check_default_value("FIRST_ADMIN_USERNAME", self.FIRST_ADMIN_USERNAME, DEFAULT_FIRST_ADMIN_USERNAME)
        self._check_default_value("FIRST_ADMIN_PASSWORD", self.FIRST_ADMIN_PASSWORD, DEFAULT_FIRST_ADMIN_PASSWORD)
        self._check_default_value("FIRST_ADMIN_EMAIL", self.FIRST_ADMIN_EMAIL, DEFAULT_FIRST_ADMIN_EMAIL)

        return self


settings = Settings()
