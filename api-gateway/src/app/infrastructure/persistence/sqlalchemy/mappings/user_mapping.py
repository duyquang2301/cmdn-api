"""User table mapping."""

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.domain.model.user.user import User
from app.infrastructure.persistence.sqlalchemy.metadata import mapper_registry, metadata
from app.util.enums.user_type import UserType

# Define users table
users_table = Table(
    "users",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("auth0_user_id", String(255), unique=True, nullable=False, index=True),
    Column("email", String(255), nullable=True),
    Column(
        "user_type",
        SQLEnum(
            UserType,
            name="user_type_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="free",
    ),
    Column("used_duration_seconds", Float, nullable=False, server_default="0"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_user() -> None:
    """Map User entity to users table."""
    mapper_registry.map_imperatively(User, users_table)
