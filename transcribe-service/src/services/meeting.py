"""Meeting lifecycle management services."""

from pathlib import Path
from uuid import UUID

from loguru import logger
from sqlalchemy.orm import Session

from src.cache.chunks import delete_chunks, get_all_chunks
from src.database.repository import get_meeting, save_meeting
from src.enums import MeetingStatus
from src.exceptions import MeetingStatusError
from src.models import Meeting

from .audio import cleanup_audio, stream_and_split_audio
from .transcription import merge_segments, segments_to_text


def start_transcription(
    session: Session,
    meeting_id: UUID,
    audio_url: str,
    upload_dir: Path,
    chunk_duration_ms: int,
) -> tuple[Meeting, int]:
    """Start transcription: stream audio, split into chunks, update status.

    Returns:
        Tuple of (meeting, number of chunks created)
    """
    logger.info(f"Starting transcription for meeting {meeting_id}")

    meeting = get_meeting(session, meeting_id)

    if not meeting.can_transcribe():
        raise MeetingStatusError(
            meeting_id=str(meeting_id),
            current=meeting.status.value,
            required="processing or transcribe_failed",
        )

    meeting.mark_transcribing()
    save_meeting(session, meeting)
    session.commit()

    meeting_dir = upload_dir / str(meeting_id)
    meeting_dir.mkdir(parents=True, exist_ok=True)

    num_chunks = stream_and_split_audio(audio_url, meeting_dir, chunk_duration_ms)

    logger.info(f"Created {num_chunks} chunks for meeting {meeting_id}")
    return meeting, num_chunks


def finalize_transcription(
    session: Session, meeting_id: UUID, upload_dir: Path
) -> Meeting:
    """Finalize transcription: merge chunks, update meeting, cleanup files.

    Returns:
        Updated meeting with transcript or error status
    """
    logger.info(f"Finalizing transcription for meeting {meeting_id}")

    meeting = get_meeting(session, meeting_id)
    chunks = get_all_chunks(meeting_id)

    if not chunks:
        logger.warning(f"No chunks found for meeting {meeting_id}")
        meeting.mark_failed("No chunks found")
        save_meeting(session, meeting)
        session.commit()
        return meeting

    logger.info(f"Retrieved {len(chunks)} chunks")

    failed_chunks = [c for c in chunks if not c.is_success]
    if failed_chunks:
        error_msg = f"{len(failed_chunks)} chunks failed: " + ", ".join(
            f"chunk {c.chunk_id}: {c.error}" for c in failed_chunks[:3]
        )
        logger.error(error_msg)
        meeting.mark_failed(error_msg)
        save_meeting(session, meeting)
        session.commit()
        return meeting

    all_segments = merge_segments([chunk.segments for chunk in chunks])
    transcript = segments_to_text(all_segments)

    logger.info(
        f"Created transcript: {len(all_segments)} segments, {len(transcript)} chars"
    )

    meeting.mark_transcribed(transcript)
    save_meeting(session, meeting)
    session.commit()

    cleanup_audio(upload_dir / str(meeting_id))
    delete_chunks(meeting_id)

    logger.info(f"Successfully finalized transcription for meeting {meeting_id}")
    return meeting


def mark_meeting_failed(
    session: Session, meeting_id: UUID, error_message: str
) -> Meeting:
    """Mark meeting as failed with error message."""
    logger.error(f"Marking meeting {meeting_id} as failed: {error_message}")

    meeting = get_meeting(session, meeting_id)
    meeting.mark_failed(error_message)
    save_meeting(session, meeting)
    session.commit()

    return meeting


def get_meeting_status(session: Session, meeting_id: UUID) -> MeetingStatus:
    """Get current meeting status."""
    return get_meeting(session, meeting_id).status


def update_meeting_audio_url(
    session: Session, meeting_id: UUID, audio_url: str
) -> Meeting:
    """Update meeting audio URL."""
    logger.info(f"Updating audio URL for meeting {meeting_id}")

    meeting = get_meeting(session, meeting_id)
    meeting.audio_url = audio_url
    save_meeting(session, meeting)
    session.commit()

    return meeting
