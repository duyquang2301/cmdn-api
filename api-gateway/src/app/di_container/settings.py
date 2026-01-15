"""Application settings management."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_ENV_FILE = _PROJECT_ROOT / ".env"


def _base_config(prefix: str = "") -> dict:
    """Create base settings config."""
    return {
        "env_file": str(_ENV_FILE),
        "env_file_encoding": "utf-8",
        "env_prefix": prefix,
        "extra": "ignore",
        "case_sensitive": False,
    }


class DatabaseSettings(BaseSettings):
    """PostgreSQL database settings (DATABASE_*)."""

    model_config = SettingsConfigDict(**_base_config("DATABASE_"))

    url: PostgresDsn
    pool_size: int = Field(default=5, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    echo: bool = False
    echo_pool: bool = False

    @field_validator("url", mode="before")
    @classmethod
    def _ensure_async_driver(cls, v: str | PostgresDsn) -> str:
        url_str = str(v)
        if url_str.startswith("postgresql://"):
            return url_str.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url_str


class RedisSettings(BaseSettings):
    """Redis cache settings (REDIS_*)."""

    model_config = SettingsConfigDict(**_base_config("REDIS_"))

    host: str
    port: int = Field(ge=1, le=65535)
    db: int = Field(default=0, ge=0)
    decode_responses: bool = True

    @computed_field
    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class RabbitMQSettings(BaseSettings):
    """RabbitMQ message broker settings (RABBITMQ_*)."""

    model_config = SettingsConfigDict(**_base_config("RABBITMQ_"))

    url: str | None = None

    host: str = "localhost"
    port: int = Field(default=5672, ge=1, le=65535)
    user: str = "admin"
    password: str = Field(default="admin123", validation_alias="RABBITMQ_PASS")

    @computed_field
    @property
    def broker_url(self) -> str:
        if self.url:
            return self.url
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}//"


class S3Settings(BaseSettings):
    """S3-compatible storage settings (S3_*)."""

    model_config = SettingsConfigDict(**_base_config("S3_"))

    bucket_name: str
    region: str
    access_key_id: str
    secret_access_key: str
    endpoint_url: str | None = None


class Auth0Settings(BaseSettings):
    """Auth0 authentication settings (AUTH0_*)."""

    model_config = SettingsConfigDict(**_base_config("AUTH0_"))

    audience: str
    issuer_base_url: str
    jwks_cache_ttl: int = Field(default=3600)


class ServerSettings(BaseSettings):
    """Uvicorn server settings (UVICORN_*)."""

    model_config = SettingsConfigDict(**_base_config("UVICORN_"))

    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)


class LoggingSettings(BaseSettings):
    """Logging settings (LOG_*)."""

    model_config = SettingsConfigDict(**_base_config("LOG_"))

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class FileStorageSettings(BaseSettings):
    """File storage settings."""

    allowed_extensions: list[str] = Field(
        default=[
            ".mp3",
            ".wav",
            ".m4a",
            ".flac",
            ".ogg",
            ".opus",
            ".aac",
            ".wma",
            ".aiff",
        ]
    )
    max_file_size_mb: int = Field(default=500, ge=1, le=5000)  # Max 500MB
    max_duration_hours: int = Field(default=10, ge=1, le=24)  # Max 10 hours


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(**_base_config())

    app_env: Literal["local", "development", "staging", "production"] = "local"
    debug: bool = False

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    s3: S3Settings = Field(default_factory=S3Settings)
    auth0: Auth0Settings = Field(default_factory=Auth0Settings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    file_storage: FileStorageSettings = Field(default_factory=FileStorageSettings)

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.app_env in ("local", "development")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings singleton."""
    return Settings()


settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
