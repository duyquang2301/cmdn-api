"""add_progress_fields_to_meetings

Revision ID: a1b2c3d4e5f6
Revises: 46d32f1ca0b4
Create Date: 2025-12-25 01:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "46d32f1ca0b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop old progress_metadata column
    op.drop_column("meetings", "progress_metadata")

    # Add new progress fields
    op.add_column(
        "meetings",
        sa.Column("transcribe_total", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "meetings",
        sa.Column("transcribe_done", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "meetings",
        sa.Column("summarize_total", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "meetings",
        sa.Column("summarize_done", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    # Remove progress fields
    op.drop_column("meetings", "summarize_done")
    op.drop_column("meetings", "summarize_total")
    op.drop_column("meetings", "transcribe_done")
    op.drop_column("meetings", "transcribe_total")

    # Add back progress_metadata column
    op.add_column(
        "meetings",
        sa.Column(
            "progress_metadata",
            sa.dialects.postgresql.JSON,
            nullable=True,
            server_default=sa.text("'{}'::json"),
        ),
    )
