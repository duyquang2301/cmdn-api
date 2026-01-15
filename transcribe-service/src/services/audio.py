"""Audio processing services."""

import shutil
from pathlib import Path

from loguru import logger

from src.exceptions import AudioProcessingError
from src.streaming.processor import StreamingAudioProcessor


def stream_and_split_audio(url: str, output_dir: Path, chunk_duration_ms: int) -> int:
    """Stream audio from URL and split into chunks.

    Downloads audio via streaming (no original file saved) and splits into
    fixed-duration chunks for parallel transcription processing.

    Args:
        url: Audio URL (s3://bucket/key or HTTP/HTTPS)
        output_dir: Directory to save chunks (chunk_0.mp3, chunk_1.mp3, ...)
        chunk_duration_ms: Duration of each chunk in milliseconds

    Returns:
        Number of chunks created
    """
    try:
        logger.info(f"Streaming and splitting audio from {url}")
        processor = StreamingAudioProcessor()
        num_chunks = processor.stream_and_split(url, output_dir, chunk_duration_ms)
        logger.info(f"Created {num_chunks} chunks")
        return num_chunks
    except Exception as e:
        raise AudioProcessingError(f"Failed to stream and split audio: {e}") from e


def cleanup_audio(meeting_dir: Path) -> None:
    """Remove meeting directory and all audio chunks."""
    try:
        if meeting_dir.exists():
            logger.info(f"Cleaning up {meeting_dir}")
            shutil.rmtree(meeting_dir)
    except OSError as e:
        raise AudioProcessingError(f"Failed to cleanup {meeting_dir}: {e}") from e
