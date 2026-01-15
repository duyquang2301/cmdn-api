"""Task repository implementation."""

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.task.task import Task
from app.util.enums.task_status import TaskStatus
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


class TaskRepositoryImpl:
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, id: UUID) -> Result[Task | None, Exception]:
        """Find task by ID."""
        try:
            result = await self._session.execute(select(Task).where(Task.id == id))
            task = result.scalar_one_or_none()
            return success(task)
        except SQLAlchemyError as e:
            log.error(f"Failed to find task by ID: {e}")
            return failure(e)

    async def find_by_meeting_id(
        self,
        meeting_id: UUID,
        *,
        limit: int = 10,
        offset: int = 0,
        status: TaskStatus | None = None,
    ) -> Result[list[Task], Exception]:
        """Find tasks by meeting ID with pagination."""
        try:
            query = select(Task).where(Task.meeting_id == meeting_id)

            if status is not None:
                query = query.where(Task.status == status)

            query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)

            result = await self._session.execute(query)
            tasks = list(result.scalars().all())
            return success(tasks)
        except SQLAlchemyError as e:
            log.error(f"Failed to find tasks by meeting ID: {e}")
            return failure(e)

    async def count_by_meeting_id(
        self,
        meeting_id: UUID,
        *,
        status: TaskStatus | None = None,
    ) -> Result[int, Exception]:
        """Count tasks by meeting ID."""
        try:
            query = (
                select(func.count())
                .select_from(Task)
                .where(Task.meeting_id == meeting_id)
            )

            if status is not None:
                query = query.where(Task.status == status)

            result = await self._session.execute(query)
            count = result.scalar_one()
            return success(count)
        except SQLAlchemyError as e:
            log.error(f"Failed to count tasks: {e}")
            return failure(e)

    async def save(self, task: Task) -> Result[None, Exception]:
        """Save task to database."""
        try:
            self._session.add(task)
            await self._session.flush()
            return success(None)
        except SQLAlchemyError as e:
            log.error(f"Failed to save task: {e}")
            return failure(e)

    async def delete(self, task: Task) -> Result[None, Exception]:
        """Delete task from database."""
        try:
            await self._session.delete(task)
            await self._session.flush()
            return success(None)
        except SQLAlchemyError as e:
            log.error(f"Failed to delete task: {e}")
            return failure(e)
