"""Factory for creating transcription providers."""

from loguru import logger

from src.config import settings
from src.enums import TranscriptionProvider
from src.exceptions import ConfigurationError

from .base import TranscriptionProvider as BaseProvider
from .gpu_whisper import GPUWhisperProvider
from .litellm import LiteLLMProvider
from .mlx_whisper import MLXWhisperProvider


def create_provider() -> BaseProvider:
    """Create transcription provider based on configuration."""
    provider_type = settings.transcription_provider.lower()
    logger.info(f"Creating transcription provider: {provider_type}")

    providers = {
        TranscriptionProvider.MLX: MLXWhisperProvider,
        TranscriptionProvider.GPU: GPUWhisperProvider,
        TranscriptionProvider.LITELLM: LiteLLMProvider,
    }

    provider_class = providers.get(provider_type)
    if not provider_class:
        raise ConfigurationError(
            f"Invalid transcription provider: {provider_type}. "
            f"Supported: {', '.join(providers.keys())}"
        )

    return provider_class()
