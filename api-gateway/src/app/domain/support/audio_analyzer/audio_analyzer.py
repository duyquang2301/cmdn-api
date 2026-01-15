"""Audio analyzer."""

import io
from pathlib import Path
from typing import BinaryIO

from mutagen import (
    File as MutagenFile,
    MutagenError,
)

from app.domain.support.logger.logger import Logger


class AudioAnalyzer:
    """Audio duration detection with format validation."""

    def __init__(self, logger: Logger) -> None:
        from app.di_container.settings import settings

        self._logger = logger
        self._allowed_extensions = set(settings.file_storage.allowed_extensions)
        self._max_file_size_bytes = settings.file_storage.max_file_size_mb * 1024 * 1024
        self._max_duration_seconds = settings.file_storage.max_duration_hours * 3600

    async def detect_duration(self, file: BinaryIO, filename: str) -> float:
        """Detect audio duration in seconds."""
        self._validate_format(filename)
        self._validate_file_size(file, filename)

        try:
            # Read file content into memory
            file.seek(0)
            file_content = file.read()
            file.seek(0)  # Reset for later use

            # Use mutagen to read audio metadata
            audio = MutagenFile(io.BytesIO(file_content), easy=True)

            if audio is None or audio.info is None:
                raise ValueError("Unable to read audio metadata")

            duration = float(audio.info.length)
            self._validate_duration(duration, filename)

            self._logger.info(
                f"Audio duration detected: {duration:.2f}s for '{filename}'"
            )
            return duration

        except MutagenError as e:
            self._logger.error(f"Failed to analyze '{filename}': {e}")
            raise ValueError(f"Failed to analyze audio file '{filename}': {e}") from e
        except Exception as e:
            self._logger.error(f"Failed to analyze '{filename}': {e}")
            raise ValueError(f"Failed to analyze audio file '{filename}': {e}") from e

    def _validate_format(self, filename: str) -> None:
        """Validate file format."""
        ext = Path(filename).suffix.lower()
        if not ext:
            raise ValueError("File has no extension")
        if ext not in self._allowed_extensions:
            supported = ", ".join(sorted(self._allowed_extensions))
            raise ValueError(f"Unsupported format '{ext}'. Supported: {supported}")

    def _validate_file_size(self, file: BinaryIO, filename: str) -> None:
        """Validate file size."""
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > self._max_file_size_bytes:
            max_size_mb = self._max_file_size_bytes / (1024 * 1024)
            actual_size_mb = file_size / (1024 * 1024)
            raise ValueError(
                f"File '{filename}' is too large: {actual_size_mb:.1f}MB. "
                f"Maximum allowed: {max_size_mb:.0f}MB"
            )

    def _validate_duration(self, duration: float, filename: str) -> None:
        """Validate audio duration."""
        if duration <= 0:
            raise ValueError(f"Invalid audio duration: {duration}s")

        if duration > self._max_duration_seconds:
            max_hours = self._max_duration_seconds / 3600
            actual_hours = duration / 3600
            raise ValueError(
                f"Audio '{filename}' is too long: {actual_hours:.1f}h. "
                f"Maximum allowed: {max_hours:.0f}h"
            )
