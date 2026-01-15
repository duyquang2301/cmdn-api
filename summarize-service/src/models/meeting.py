"""Meeting model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Meeting(Base):
    """Meeting model."""

    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)
    duration = Column(Float, nullable=True, comment="Audio duration in seconds")
    status = Column(String(50), nullable=False, default="processing")
    transcribe_text = Column(Text, nullable=True)
    transcribe_segments = Column(JSONB, nullable=True)
    summary_text = Column(Text, nullable=True)
    key_notes = Column(JSONB, nullable=True)
    transcribe_total = Column(Integer, nullable=False, default=0)
    transcribe_done = Column(Integer, nullable=False, default=0)
    summarize_total = Column(Integer, nullable=False, default=0)
    summarize_done = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationship to Task model
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Meeting(id={self.id}, title={self.title!r}, status={self.status})"
