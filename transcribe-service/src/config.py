"""Application configuration using Pydantic Settings."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str
    database_pool_size: int = Field(default=5, ge=1, le=50)
    database_max_overflow: int = Field(default=10, ge=0, le=100)

    # Redis
    redis_url: str
    redis_decode_responses: bool = True

    # RabbitMQ
    # Cloud URL có độ ưu tiên cao nhất
    rabbitmq_url: str | None = None

    # Fallback về config thủ công nếu không có URL
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = Field(default=5672, ge=1, le=65535)
    rabbitmq_user: str = "admin"
    rabbitmq_password: str = "admin123"

    # Audio
    upload_dir: str = "./uploads"
    chunk_duration_minutes: int = Field(default=10, ge=1, le=60)

    # Transcription
    transcription_provider: str = Field(default="gpu", pattern="^(mlx|gpu|litellm)$")
    whisper_model_size: str = Field(
        default="medium", pattern="^(tiny|base|small|medium|large|large-v2|large-v3)$"
    )
    whisper_device: str = Field(default="cpu", pattern="^(cpu|cuda|mps)$")
    whisper_compute_type: str = Field(
        default="int8", pattern="^(int8|int16|float16|float32)$"
    )
    whisper_beam_size: int = Field(default=5, ge=1, le=10)
    whisper_vad_filter: bool = True
    litellm_api_key: str = ""
    litellm_model: str = "whisper-1"
    litellm_api_base: str | None = None

    # Celery
    celery_autoscale: str = "10,1"
    celery_prefetch_multiplier: int = Field(default=1, ge=1)
    celery_max_tasks_per_child: int = Field(default=100, ge=1)

    # App
    debug: bool = False
    log_level: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    @field_validator("upload_dir")
    @classmethod
    def validate_upload_dir(cls, v: str) -> str:
        """Ensure upload directory path is valid."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    def get_rabbitmq_url(self) -> str:
        """RabbitMQ connection URL."""
        # Ưu tiên dùng RABBITMQ_URL nếu có (cho cloud)
        if self.rabbitmq_url:
            return self.rabbitmq_url
        # Fallback về config thủ công (cho local)
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}//"

    @property
    def chunk_duration_ms(self) -> int:
        """Chunk duration in milliseconds."""
        return self.chunk_duration_minutes * 60 * 1000


settings = Settings()
