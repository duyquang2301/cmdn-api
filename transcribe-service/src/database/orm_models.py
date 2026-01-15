"""SQLAlchemy ORM models."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, Float, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID

from .connection import Base


class MeetingModel(Base):
    """Meeting ORM model mapping to 'meetings' table."""

    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)
    duration = Column(Float, nullable=True, comment="Audio duration in seconds")
    status = Column(
        Enum(
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
        default="processing",
    )
    transcribe_text = Column(Text, nullable=True)
    summarize = Column(Text, nullable=True)
    transcribe_segments = Column(JSON, nullable=True)
    key_notes = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return (
            f"<MeetingModel(id={self.id}, title={self.title!r}, status={self.status})>"
        )
