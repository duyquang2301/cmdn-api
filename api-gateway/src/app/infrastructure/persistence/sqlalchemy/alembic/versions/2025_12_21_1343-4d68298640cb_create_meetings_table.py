"""create_meetings_table

Revision ID: 4d68298640cb
Revises:
Create Date: 2025-12-21 13:43:56.119518

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON, UUID

revision: str = "4d68298640cb"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create meetings table
    op.create_table(
        "meetings",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("audio_url", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "processing",
                "transcribing",
                "transcribed",
                "transcribe_failed",
                "summarizing",
                "summarized",
                "summarize_failed",
                "completed",
                name="meeting_status",
            ),
            nullable=False,
            server_default="processing",
        ),
        sa.Column("transcribe_text", sa.Text(), nullable=True),
        sa.Column("summarize", sa.Text(), nullable=True),
        sa.Column("transcribe_segments", JSON, nullable=True),
        sa.Column("key_notes", JSON, nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meetings")),
    )


def downgrade() -> None:
    op.drop_table("meetings")
    op.execute("DROP TYPE IF EXISTS meeting_status")
