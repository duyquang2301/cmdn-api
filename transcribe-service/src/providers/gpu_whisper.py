"""GPU Whisper transcription provider using faster-whisper with CUDA."""

from pathlib import Path

from loguru import logger

from src.config import settings
from src.exceptions import TranscriptionFailedError
from src.models import Segment

from .base import TranscriptionProvider

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None  # type: ignore[assignment, misc]


class GPUWhisperProvider(TranscriptionProvider):
    """Transcription provider using faster-whisper with CUDA acceleration."""

    def __init__(self):
        if WhisperModel is None:
            raise TranscriptionFailedError(
                "faster-whisper not installed. Install with: pip install faster-whisper"
            )

        try:
            self.model_name = settings.whisper_model_size
            self.device = settings.whisper_device
            self.compute_type = settings.whisper_compute_type
            self.beam_size = settings.whisper_beam_size
            self.vad_filter = settings.whisper_vad_filter

            logger.info(
                f"Loading faster-whisper: {self.model_name} "
                f"on {self.device} ({self.compute_type}), beam_size={self.beam_size}, vad_filter={self.vad_filter}"
            )

            self.model = WhisperModel(
                self.model_name, device=self.device, compute_type=self.compute_type
            )
            logger.info("GPU Whisper initialized")
        except Exception as e:
            raise TranscriptionFailedError(
                f"Failed to initialize GPU Whisper: {e}"
            ) from e

    def transcribe(self, audio_path: Path) -> list[Segment]:
        """Transcribe audio file using GPU Whisper."""
        try:
            logger.info(f"Transcribing: {audio_path}")
            segments_iter, info = self.model.transcribe(
                str(audio_path), beam_size=self.beam_size, vad_filter=self.vad_filter
            )

            logger.info(
                f"Detected: {info.language} (prob: {info.language_probability:.2f})"
            )

            segments = [
                Segment(
                    start=float(seg.start),
                    end=float(seg.end),
                    text=seg.text.strip(),
                )
                for seg in segments_iter
            ]

            logger.info(f"Transcription complete: {len(segments)} segments")
            return segments
        except Exception as e:
            logger.error(f"GPU Whisper failed: {e}")
            raise TranscriptionFailedError(f"GPU Whisper failed: {e}") from e
