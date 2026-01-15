"""update_user_duration_to_float_and_add_user_meeting_relationship

Revision ID: 23a8faff22f0
Revises: 810e941f1204
Create Date: 2026-01-15 16:15:21.162217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "23a8faff22f0"
down_revision: Union[str, None] = "810e941f1204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Change used_duration_seconds from Integer to Float in users table
    op.alter_column(
        "users",
        "used_duration_seconds",
        type_=sa.Float(),
        existing_type=sa.Integer(),
        existing_nullable=False,
        existing_server_default="0",
    )

    # 2. Add user_id column to meetings table
    op.add_column(
        "meetings",
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # 3. Create index on user_id
    op.create_index(
        "ix_meetings_user_id",
        "meetings",
        ["user_id"],
    )

    # 4. Add foreign key constraint
    op.create_foreign_key(
        "fk_meetings_user_id_users",
        "meetings",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # 1. Drop foreign key constraint
    op.drop_constraint("fk_meetings_user_id_users", "meetings", type_="foreignkey")

    # 2. Drop index
    op.drop_index("ix_meetings_user_id", table_name="meetings")

    # 3. Drop user_id column from meetings table
    op.drop_column("meetings", "user_id")

    # 4. Change used_duration_seconds back to Integer in users table
    op.alter_column(
        "users",
        "used_duration_seconds",
        type_=sa.Integer(),
        existing_type=sa.Float(),
        existing_nullable=False,
        existing_server_default="0",
    )
