"""Task aggregate root."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.model.base import Entity
from app.util.enums.task_status import TaskStatus


class Task(Entity):
    """Task entity"""

    def __init__(
        self,
        *,
        id: UUID,
        meeting_id: UUID,
        title: str,
        description: str | None = None,
        status: TaskStatus = TaskStatus.PENDING,
        assignee: str | None = None,
        due_date: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id)
        self.meeting_id = meeting_id
        self.title = title
        self.description = description
        self.status = status
        self.assignee = assignee
        self.due_date = due_date
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    @staticmethod
    def create(
        *,
        id: UUID | None = None,
        meeting_id: UUID,
        title: str,
        description: str | None = None,
        status: TaskStatus = TaskStatus.PENDING,
        assignee: str | None = None,
        due_date: datetime | None = None,
    ) -> "Task":
        """Factory method with validation"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        if len(title) > 255:
            raise ValueError("Task title cannot exceed 255 characters")

        now = datetime.now(UTC)
        return Task(
            id=id or uuid4(),
            meeting_id=meeting_id,
            title=title.strip(),
            description=description.strip() if description else None,
            status=status,
            assignee=assignee,
            due_date=due_date,
            created_at=now,
            updated_at=now,
        )

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title!r}, status={self.status})"
