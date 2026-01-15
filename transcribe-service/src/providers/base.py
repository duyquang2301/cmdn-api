"""Base transcription provider interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.models import Segment


class TranscriptionProvider(ABC):
    """Base interface for transcription providers."""

    @abstractmethod
    def transcribe(self, audio_path: Path) -> list[Segment]:
        """Transcribe audio file to segments with timing information."""
        pass
