"""Meeting domain exports."""

from app.domain.model.meeting.meeting import Meeting
from app.domain.model.meeting.meeting_repository import MeetingRepository

__all__ = [
    "Meeting",
    "MeetingRepository",
]
