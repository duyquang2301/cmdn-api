"""Database repository."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.models import Meeting, Task
from src.utils.enums import MeetingStatus
from src.utils.exceptions import MeetingNotFoundError


def get_meeting(session: Session, meeting_id: UUID) -> Meeting:
    """Get meeting by ID.

    Raises:
        MeetingNotFoundError: If meeting not found
    """
    meeting = session.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise MeetingNotFoundError(meeting_id)
    return meeting


def update_meeting_status(
    session: Session, meeting_id: UUID, status: MeetingStatus
) -> Meeting:
    """Update meeting status."""
    meeting = get_meeting(session, meeting_id)
    meeting.status = status.value
    session.add(meeting)
    return meeting


def update_meeting_summary(
    session: Session, meeting_id: UUID, summary: str, key_notes: list[dict]
) -> Meeting:
    """Update meeting with summary and key notes."""
    meeting = get_meeting(session, meeting_id)
    meeting.summary_text = summary
    meeting.key_notes = key_notes
    meeting.status = MeetingStatus.SUMMARIZED.value
    session.add(meeting)
    return meeting


def update_key_notes(
    session: Session, meeting_id: UUID, key_notes: list[dict]
) -> Meeting:
    """Update meeting with key notes."""
    meeting = get_meeting(session, meeting_id)
    meeting.key_notes = key_notes
    session.add(meeting)
    return meeting


def save_tasks(session: Session, tasks: list[Task]) -> int:
    """Save multiple tasks in batch."""
    session.add_all(tasks)
    return len(tasks)
