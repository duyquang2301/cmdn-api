"""add_progress_metadata_to_meetings

Revision ID: 46d32f1ca0b4
Revises: 2040dc49ab40
Create Date: 2025-12-24 18:12:03.250505

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON

revision: str = "46d32f1ca0b4"
down_revision: str | None = "2040dc49ab40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "meetings",
        sa.Column(
            "progress_metadata",
            JSON,
            nullable=True,
            server_default=sa.text("'{}'::json"),
        ),
    )


def downgrade() -> None:
    op.drop_column("meetings", "progress_metadata")
