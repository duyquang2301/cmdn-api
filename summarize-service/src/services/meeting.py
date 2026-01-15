"""Meeting operations service."""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from src.database.repository import get_meeting, update_meeting_status
from src.utils.enums import MeetingStatus
from src.utils.exceptions import InvalidStatusError

logger = logging.getLogger(__name__)


def start_summarization(session: Session, meeting_id: UUID) -> None:
    """Mark meeting as summarizing.

    Raises:
        InvalidStatusError: If meeting is not in transcribed status
    """
    logger.info(f"Starting summarization for meeting {meeting_id}")
    meeting = get_meeting(session, meeting_id)

    if meeting.status not in {MeetingStatus.TRANSCRIBED.value}:
        raise InvalidStatusError(f"Cannot summarize meeting in status {meeting.status}")

    update_meeting_status(session, meeting_id, MeetingStatus.SUMMARIZING)
    session.commit()


def complete_summarization(session: Session, meeting_id: UUID, summary: str) -> None:
    """Complete summarization with summary text."""
    logger.info(f"Saving summary for meeting {meeting_id}")
    meeting = get_meeting(session, meeting_id)
    meeting.summary_text = summary
    meeting.status = MeetingStatus.SUMMARIZED.value
    session.add(meeting)
    session.commit()


def update_key_notes(session: Session, meeting_id: UUID, key_notes: list[dict]) -> None:
    """Update meeting with key notes."""
    logger.info(f"Saving key notes for meeting {meeting_id}")
    meeting = get_meeting(session, meeting_id)
    meeting.key_notes = key_notes
    session.add(meeting)
    session.commit()


def fail_summarization(session: Session, meeting_id: UUID, error: str) -> None:
    """Mark summarization as failed."""
    logger.error(f"Summarization failed for meeting {meeting_id}: {error}")
    meeting = get_meeting(session, meeting_id)
    meeting.status = MeetingStatus.SUMMARIZE_FAILED.value
    meeting.error_message = error
    session.add(meeting)
    session.commit()
