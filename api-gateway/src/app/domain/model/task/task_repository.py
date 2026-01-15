"""Task repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.model.task.task import Task
from app.util.enums.task_status import TaskStatus
from app.util.result import Result


class TaskRepository(Protocol):
    """Repository interface for Task aggregate."""

    async def find_by_meeting_id(
        self,
        meeting_id: UUID,
        *,
        limit: int = 10,
        offset: int = 0,
        status: TaskStatus | None = None,
    ) -> Result[list[Task], Exception]:
        """Find tasks by meeting ID."""
        ...

    async def count_by_meeting_id(
        self,
        meeting_id: UUID,
        *,
        status: TaskStatus | None = None,
    ) -> Result[int, Exception]:
        """Count tasks by meeting ID."""
        ...

    async def save(self, task: Task) -> Result[None, Exception]:
        """Save task (insert or update)."""
        ...

    async def delete(self, task: Task) -> Result[None, Exception]:
        """Delete task."""
        ...
