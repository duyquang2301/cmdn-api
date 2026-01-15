"""Task table mapping."""

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.domain.model.task.task import Task
from app.infrastructure.persistence.sqlalchemy.metadata import mapper_registry, metadata
from app.util.enums.task_status import TaskStatus

tasks_table = Table(
    "tasks",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column(
        "meeting_id",
        PGUUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("title", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column(
        "status",
        SQLEnum(
            TaskStatus,
            name="task_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=TaskStatus.PENDING,
    ),
    Column("assignee", String(255), nullable=True),
    Column("due_date", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_task() -> None:
    """Map Task entity to tasks table"""
    mapper_registry.map_imperatively(Task, tasks_table)
