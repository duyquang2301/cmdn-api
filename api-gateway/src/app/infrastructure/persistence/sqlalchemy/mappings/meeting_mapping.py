"""Meeting table mapping."""

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import (
    JSON,
    UUID as PGUUID,
)

from app.domain.model.meeting.meeting import Meeting
from app.infrastructure.persistence.sqlalchemy.metadata import mapper_registry, metadata
from app.util.enums.status import Status

# Define meetings table
meetings_table = Table(
    "meetings",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
    Column("title", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("audio_url", Text, nullable=True),
    Column("duration", Float, nullable=True, comment="Audio duration in seconds"),
    Column(
        "status",
        SQLEnum(
            Status,
            name="meeting_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=Status.PROCESSING,
    ),
    Column("transcribe_text", Text, nullable=True),
    Column("summarize", Text, nullable=True),
    Column("transcribe_segments", JSON, nullable=True),
    Column("key_notes", JSON, nullable=True),
    Column("transcribe_total", Integer, nullable=False, server_default="0"),
    Column("transcribe_done", Integer, nullable=False, server_default="0"),
    Column("summarize_total", Integer, nullable=False, server_default="0"),
    Column("summarize_done", Integer, nullable=False, server_default="0"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_meeting() -> None:
    """
    Map Meeting entity to meetings table using imperative mapping.

    This keeps domain entities clean from SQLAlchemy dependencies.
    """
    mapper_registry.map_imperatively(Meeting, meetings_table)
