"""Find many tasks use case."""

import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.model.task.task_repository import TaskRepository
from app.domain.support.logger.logger import Logger
from app.util.enums.task_status import TaskStatus
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class FindManyTaskUseCaseInput:
    """Input for find many tasks use case."""

    meeting_id: UUID
    limit: int = 10
    offset: int = 0
    status: TaskStatus | None = None


@dataclass(frozen=True)
class TaskItem:
    """Single task item."""

    id: UUID
    meeting_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    assignee: str | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class FindManyTaskUseCaseOutput:
    """Output for find many tasks use case."""

    items: list[TaskItem]
    total: int
    limit: int
    offset: int


class FindManyTaskUseCase:
    """Find many tasks by meeting ID use case."""

    def __init__(
        self,
        task_repository: TaskRepository,
        logger: Logger,
    ) -> None:
        self._task_repository = task_repository
        self._logger = logger

    async def execute(
        self, input: FindManyTaskUseCaseInput
    ) -> Result[FindManyTaskUseCaseOutput, Exception]:
        """Execute find many tasks use case."""
        self._logger.info(f"Find tasks for meeting: {input.meeting_id}")

        tasks_result = await self._task_repository.find_by_meeting_id(
            input.meeting_id,
            limit=input.limit,
            offset=input.offset,
            status=input.status,
        )

        if tasks_result.is_failure():
            self._logger.error(f"Failed to find tasks: {tasks_result.error}")
            return failure(tasks_result.error)

        count_result = await self._task_repository.count_by_meeting_id(
            input.meeting_id,
            status=input.status,
        )

        if count_result.is_failure():
            self._logger.error(f"Failed to count tasks: {count_result.error}")
            return failure(count_result.error)

        tasks = tasks_result.data
        total = count_result.data

        items = [
            TaskItem(
                id=task.id,
                meeting_id=task.meeting_id,
                title=task.title,
                description=task.description,
                status=task.status,
                assignee=task.assignee,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
            for task in tasks
        ]

        output = FindManyTaskUseCaseOutput(
            items=items,
            total=total,
            limit=input.limit,
            offset=input.offset,
        )

        self._logger.info(f"Find tasks: done. Found {len(items)} tasks")
        return success(output)
