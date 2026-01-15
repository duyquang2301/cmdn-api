"""MLX Whisper transcription provider for Apple Silicon."""

from pathlib import Path

from loguru import logger

from src.config import settings
from src.exceptions import TranscriptionFailedError
from src.models import Segment

from .base import TranscriptionProvider

try:
    import mlx_whisper
except ImportError:
    mlx_whisper = None  # type: ignore[assignment]


class MLXWhisperProvider(TranscriptionProvider):
    """Transcription provider using MLX Whisper for Apple Silicon."""

    def __init__(self):
        if mlx_whisper is None:
            raise TranscriptionFailedError(
                "mlx-whisper not installed. Install with: pip install mlx-whisper"
            )

        self._mlx_whisper = mlx_whisper
        self.model_name = settings.whisper_model_size
        logger.info(f"Initialized MLX Whisper with model: {self.model_name}")

    def transcribe(self, audio_path: Path) -> list[Segment]:
        """Transcribe audio file using MLX Whisper."""
        try:
            logger.info(f"Transcribing: {audio_path}")
            result = self._mlx_whisper.transcribe(
                str(audio_path), path_or_hf_repo=self.model_name
            )

            segments = [
                Segment(
                    start=float(seg["start"]),
                    end=float(seg["end"]),
                    text=seg["text"].strip(),
                )
                for seg in result.get("segments", [])
            ]

            logger.info(f"Transcription complete: {len(segments)} segments")
            return segments
        except Exception as e:
            logger.error(f"MLX Whisper failed: {e}")
            raise TranscriptionFailedError(f"MLX Whisper failed: {e}") from e
