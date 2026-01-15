"""Meeting repository functions."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.enums import MeetingStatus
from src.exceptions import MeetingNotFoundError
from src.models import Meeting

from .orm_models import MeetingModel


def to_domain(model: MeetingModel) -> Meeting:
    """Convert ORM model to domain model."""
    return Meeting(
        id=model.id,
        title=model.title,
        status=MeetingStatus(model.status),
        audio_url=model.audio_url,
        transcript=model.transcribe_text,
        summary=model.summarize,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(meeting: Meeting) -> MeetingModel:
    """Convert domain model to ORM model."""
    return MeetingModel(
        id=meeting.id,
        title=meeting.title,
        status=meeting.status.value,
        audio_url=meeting.audio_url,
        transcribe_text=meeting.transcript,
        summarize=meeting.summary,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


def get_meeting(session: Session, meeting_id: UUID) -> Meeting:
    """Get meeting by ID."""
    model = session.query(MeetingModel).filter(MeetingModel.id == meeting_id).first()
    if not model:
        raise MeetingNotFoundError(str(meeting_id))
    return to_domain(model)


def save_meeting(session: Session, meeting: Meeting) -> None:
    """Save or update meeting (does not commit)."""
    model = session.query(MeetingModel).filter(MeetingModel.id == meeting.id).first()

    if model:
        # Update existing
        model.title = meeting.title
        model.status = meeting.status.value
        model.audio_url = meeting.audio_url
        model.transcribe_text = meeting.transcript
        model.summarize = meeting.summary
        model.updated_at = meeting.updated_at
    else:
        # Create new
        model = to_model(meeting)
        session.add(model)

    session.flush()


def list_meetings(session: Session, limit: int = 100, offset: int = 0) -> list[Meeting]:
    """List meetings with pagination."""
    models = (
        session.query(MeetingModel)
        .order_by(MeetingModel.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return [to_domain(m) for m in models]
