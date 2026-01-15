"""Transcription processing services."""

from pathlib import Path

from loguru import logger

from src.exceptions import TranscriptionFailedError
from src.models import Segment
from src.providers.base import TranscriptionProvider


def transcribe_audio_file(
    provider: TranscriptionProvider, audio_path: Path
) -> list[Segment]:
    """Transcribe audio file using provider.

    Returns:
        List of transcription segments with timestamps
    """
    try:
        logger.info(f"Transcribing {audio_path}")

        if not audio_path.exists():
            raise TranscriptionFailedError(f"Audio file not found: {audio_path}")

        segments = provider.transcribe(audio_path)

        logger.info(
            f"Transcribed {audio_path}: {len(segments)} segments, "
            f"duration {segments[-1].end if segments else 0:.2f}s"
        )

        return segments

    except TranscriptionFailedError:
        raise
    except Exception as e:
        raise TranscriptionFailedError(f"Failed to transcribe {audio_path}: {e}") from e


def adjust_segment_timestamps(
    segments: list[Segment], offset_seconds: float
) -> list[Segment]:
    """Adjust segment timestamps by adding offset for chunk merging."""
    return [
        Segment(
            start=segment.start + offset_seconds,
            end=segment.end + offset_seconds,
            text=segment.text,
        )
        for segment in segments
    ]


def merge_segments(chunks_segments: list[list[Segment]]) -> list[Segment]:
    """Merge segments from multiple chunks into single list."""
    return [segment for segments in chunks_segments for segment in segments]


def segments_to_text(segments: list[Segment]) -> str:
    """Convert segments to plain text transcript."""
    return " ".join(segment.text for segment in segments)
