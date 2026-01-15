"""Application configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str

    # RabbitMQ
    # Cloud URL có độ ưu tiên cao nhất
    rabbitmq_url: str | None = None
    
    # Fallback về config thủ công nếu không có URL
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = Field(default=5672, ge=1, le=65535)
    rabbitmq_user: str = "admin"
    rabbitmq_password: str = "admin123"

    # Redis
    redis_host: str
    redis_port: int = Field(ge=1, le=65535)

    # Google Gemini (using existing LLM env vars for compatibility)
    google_api_key: str = Field(alias="llm_api_key")
    llm_model: str
    llm_base_url: str
    llm_max_tokens: int = Field(ge=1)
    llm_temperature: float = Field(ge=0.0, le=2.0)

    # Summarization
    summary_chunk_size: int = Field(ge=1000)
    max_retries: int = Field(ge=1, le=10)
    retry_delay: float = Field(ge=0.1)

    # Celery
    celery_autoscale: str
    celery_prefetch_multiplier: int = Field(ge=1)
    celery_max_tasks_per_child: int = Field(ge=1)

    # App
    debug: bool
    log_level: str = Field(pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    def get_rabbitmq_url(self) -> str:
        """RabbitMQ URL."""
        # Ưu tiên dùng RABBITMQ_URL nếu có (cho cloud)
        if self.rabbitmq_url:
            return self.rabbitmq_url
        # Fallback về config thủ công (cho local)
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}//"

    @property
    def redis_url(self) -> str:
        """Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/0"


settings = Settings()
