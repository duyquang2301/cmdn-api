"""Meeting repository implementation."""

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.meeting.meeting import Meeting
from app.domain.model.meeting.meeting_repository import MeetingStatusInProgress
from app.util.enums.status import Status
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


class MeetingRepositoryImpl:
    """SQLAlchemy implementation of MeetingRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, id: UUID, user_id: UUID) -> Result[Meeting | None, Exception]:
        """Find meeting by ID."""
        try:
            result = await self._session.execute(
                select(Meeting).where(Meeting.id == id, Meeting.user_id == user_id)
            )
            meeting = result.scalar_one_or_none()
            return success(meeting)
        except SQLAlchemyError as e:
            log.error(f"Failed to find meeting by ID: {e}")
            return failure(e)

    async def find_many(
        self,
        *,
        user_id: UUID | None = None,
        limit: int = 10,
        offset: int = 0,
        status: Status | None = None,
    ) -> Result[list[Meeting], Exception]:
        """Find multiple meetings with pagination."""
        try:
            query = select(Meeting)

            if user_id is not None:
                query = query.where(Meeting.user_id == user_id)

            if status is not None:
                query = query.where(Meeting.status == status)

            query = (
                query.order_by(Meeting.created_at.desc()).limit(limit).offset(offset)
            )

            result = await self._session.execute(query)
            meetings = list(result.scalars().all())
            return success(meetings)
        except SQLAlchemyError as e:
            log.error(f"Failed to find meetings: {e}")
            return failure(e)

    async def find_status_in_progress_by_id(
        self, id: UUID
    ) -> Result[MeetingStatusInProgress | None, Exception]:
        """Find status in progress by ID"""
        try:
            stmt = select(
                Meeting.id,
                Meeting.status,
                Meeting.transcribe_total,
                Meeting.transcribe_done,
                Meeting.summarize_total,
                Meeting.summarize_done,
            ).where(Meeting.id == id)

            result = await self._session.execute(stmt)
            row = result.one_or_none()

            if row is None:
                return success(None)

            return success(MeetingStatusInProgress(*row))
        except SQLAlchemyError as e:
            log.error(f"Failed to find meeting status by ID: {e}")
            return failure(e)

    async def count(
        self, *, user_id: UUID | None = None, status: Status | None = None
    ) -> Result[int, Exception]:
        """Count meetings."""
        try:
            query = select(func.count()).select_from(Meeting)

            if user_id is not None:
                query = query.where(Meeting.user_id == user_id)

            if status is not None:
                query = query.where(Meeting.status == status)

            result = await self._session.execute(query)
            count = result.scalar_one()
            return success(count)
        except SQLAlchemyError as e:
            log.error(f"Failed to count meetings: {e}")
            return failure(e)

    async def save(self, meeting: Meeting) -> Result[None, Exception]:
        """Save meeting to database."""
        try:
            self._session.add(meeting)
            await self._session.flush()
            return success(None)
        except SQLAlchemyError as e:
            log.error(f"Failed to save meeting: {e}")
            return failure(e)

    async def delete(self, meeting: Meeting) -> Result[None, Exception]:
        """Delete meeting from database."""
        try:
            await self._session.delete(meeting)
            await self._session.flush()
            return success(None)
        except SQLAlchemyError as e:
            log.error(f"Failed to delete meeting: {e}")
            return failure(e)
