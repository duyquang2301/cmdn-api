"""create_users_table

Revision ID: 25c0586a3705
Revises: a1b2c3d4e5f6
Create Date: 2026-01-11 22:27:30.511175

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "25c0586a3705"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table (SQLAlchemy will automatically create the enum)
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("auth0_user_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column(
            "user_type",
            sa.Enum("free", "premium", "enterprise", name="user_type_enum"),
            nullable=False,
            server_default="free",
        ),
        sa.Column(
            "used_duration_seconds",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("auth0_user_id", name=op.f("uq_users_auth0_user_id")),
    )

    # Create indexes for users table
    op.create_index(op.f("ix_users_auth0_user_id"), "users", ["auth0_user_id"])
    op.create_index(op.f("ix_users_user_type"), "users", ["user_type"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f("ix_users_user_type"), table_name="users")
    op.drop_index(op.f("ix_users_auth0_user_id"), table_name="users")

    # Drop users table
    op.drop_table("users")

    # Drop user_type enum
    op.execute("DROP TYPE IF EXISTS user_type_enum")
