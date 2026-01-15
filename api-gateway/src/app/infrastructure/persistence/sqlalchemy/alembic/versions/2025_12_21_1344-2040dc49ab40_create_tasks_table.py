"""create_tasks_table

Revision ID: 2040dc49ab40
Revises: 4d68298640cb
Create Date: 2025-12-21 13:44:36.877896

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "2040dc49ab40"
down_revision: str | None = "4d68298640cb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("meeting_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "in_progress",
                "completed",
                "failed",
                name="task_status",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("assignee", sa.String(length=255), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
        sa.ForeignKeyConstraint(
            ["meeting_id"],
            ["meetings.id"],
            name=op.f("fk_tasks_meeting_id_meetings"),
            ondelete="CASCADE",
        ),
    )

    # Create index on meeting_id for faster lookups
    op.create_index(
        op.f("ix_tasks_meeting_id"),
        "tasks",
        ["meeting_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_meeting_id"), table_name="tasks")
    op.drop_table("tasks")
    op.execute("DROP TYPE IF EXISTS task_status")
