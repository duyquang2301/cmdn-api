"""LiteLLM transcription provider for API-based transcription."""

from pathlib import Path

from loguru import logger

from src.config import settings
from src.exceptions import TranscriptionFailedError
from src.models import Segment

from .base import TranscriptionProvider

try:
    import litellm
except ImportError:
    litellm = None  # type: ignore[assignment]


class LiteLLMProvider(TranscriptionProvider):
    """Transcription provider using LiteLLM for API-based transcription."""

    def __init__(self):
        if litellm is None:
            raise TranscriptionFailedError(
                "litellm not installed. Install with: pip install litellm"
            )

        self._litellm = litellm
        self.model = settings.litellm_model
        self.api_key = settings.litellm_api_key
        self.api_base = settings.litellm_api_base

        if self.api_base:
            self._litellm.api_base = self.api_base

        logger.info(f"Initialized LiteLLM with model: {self.model}")

    def transcribe(self, audio_path: Path) -> list[Segment]:
        """Transcribe audio file using LiteLLM API."""
        try:
            logger.info(f"Transcribing via LiteLLM: {audio_path}")

            with open(audio_path, "rb") as audio_file:
                response = self._litellm.transcription(
                    model=self.model, file=audio_file, api_key=self.api_key
                )

            text = (
                response.text
                if hasattr(response, "text")
                else response.get("text", "")
                if isinstance(response, dict)
                else str(response)
            )

            segments = [Segment(start=0.0, end=0.0, text=text.strip())]
            logger.info(f"Transcription complete: {len(text)} characters")
            return segments
        except Exception as e:
            logger.error(f"LiteLLM failed: {e}")
            raise TranscriptionFailedError(f"LiteLLM failed: {e}") from e
