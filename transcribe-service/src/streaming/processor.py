"""Streaming audio processor."""

import logging
from io import BytesIO
from pathlib import Path

from pydub import AudioSegment

from src.exceptions import AudioProcessingError

from .stream_reader import HTTPStreamReader, S3StreamReader

logger = logging.getLogger(__name__)


class StreamingAudioProcessor:
    """Stream audio and split into chunks without saving original file."""

    def __init__(self):
        self.s3_reader = S3StreamReader()
        self.http_reader = HTTPStreamReader()

    def stream_and_split(
        self,
        url: str,
        output_dir: Path,
        chunk_duration_ms: int,
        stream_chunk_size: int = 8192,
    ) -> int:
        """Stream audio and split into chunks."""
        chunk_count = 0

        try:
            # Select reader based on URL scheme
            reader = self.s3_reader if url.startswith("s3://") else self.http_reader
            logger.info(f"Streaming from {url}")

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Stream audio into memory
            buffer = BytesIO()
            for data in reader.stream(url, stream_chunk_size):
                buffer.write(data)

            # Load and split audio
            buffer.seek(0)
            audio = AudioSegment.from_file(buffer, format="mp3")
            duration_ms = len(audio)
            total_chunks = (duration_ms + chunk_duration_ms - 1) // chunk_duration_ms

            logger.info(f"Splitting {duration_ms}ms audio into {total_chunks} chunks")

            # Save chunks
            for i in range(total_chunks):
                start = i * chunk_duration_ms
                end = min(start + chunk_duration_ms, duration_ms)
                chunk = audio[start:end]
                chunk.export(str(output_dir / f"chunk_{i}.mp3"), format="mp3")
                chunk_count += 1

            logger.info(f"Created {chunk_count} chunks")
            return chunk_count

        except Exception as e:
            logger.error(f"Stream/split failed: {e}", exc_info=True)
            self._cleanup_chunks(output_dir, chunk_count)
            raise AudioProcessingError(f"Failed to stream and split audio: {e}") from e

    def _cleanup_chunks(self, output_dir: Path, chunk_count: int) -> None:
        """Remove partial chunks on failure."""
        if chunk_count == 0:
            return

        try:
            logger.info(f"Cleaning up {chunk_count} partial chunks")
            for i in range(chunk_count):
                chunk_path = output_dir / f"chunk_{i}.mp3"
                if chunk_path.exists():
                    chunk_path.unlink()

            # Remove directory if empty
            if output_dir.exists() and not any(output_dir.iterdir()):
                output_dir.rmdir()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
