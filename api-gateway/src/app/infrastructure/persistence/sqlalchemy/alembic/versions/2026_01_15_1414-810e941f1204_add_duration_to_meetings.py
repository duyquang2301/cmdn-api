"""add_duration_to_meetings

Revision ID: 810e941f1204
Revises: 25c0586a3705
Create Date: 2026-01-15 14:14:12.054559

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "810e941f1204"
down_revision: Union[str, None] = "25c0586a3705"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add duration column to meetings table
    op.add_column(
        "meetings",
        sa.Column(
            "duration",
            sa.Float(),
            nullable=True,
            comment="Audio duration in seconds",
        ),
    )


def downgrade() -> None:
    # Remove duration column from meetings table
    op.drop_column("meetings", "duration")
