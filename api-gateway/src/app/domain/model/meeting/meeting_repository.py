"""Meeting repository interface."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.domain.model.meeting.meeting import Meeting
from app.util.enums.status import Status
from app.util.result import Result


@dataclass(frozen=True)
class MeetingStatusInProgress:
    """DTO for meeting status and progress"""

    id: UUID
    status: Status
    transcribe_total: int
    transcribe_done: int
    summarize_total: int
    summarize_done: int


class MeetingRepository(Protocol):
    """Repository interface for Meeting aggregate."""

    async def find_by_id(self, id: UUID, user_id: UUID) -> Result[Meeting | None, Exception]:
        """Find meeting by ID."""
        ...

    async def find_many(
        self,
        *,
        user_id: UUID | None = None,
        limit: int = 10,
        offset: int = 0,
        status: Status | None = None,
    ) -> Result[list[Meeting], Exception]:
        """Find multiple meetings with pagination."""
        ...

    async def find_status_in_progress_by_id(
        self, id: UUID
    ) -> Result[MeetingStatusInProgress | None, Exception]:
        """Find status in progress by ID"""
        ...

    async def count(
        self, *, user_id: UUID | None = None, status: Status | None = None
    ) -> Result[int, Exception]:
        """Count meetings."""
        ...

    async def save(self, meeting: Meeting) -> Result[None, Exception]:
        """Save meeting (insert or update)."""
        ...

    async def delete(self, meeting: Meeting) -> Result[None, Exception]:
        """Delete meeting."""
        ...
