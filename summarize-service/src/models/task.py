"""Task model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.meeting import Base


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    assignee = Column(String(255), nullable=True)
    due_date = Column(String(50), nullable=True)
    priority = Column(String(50), nullable=False, default="medium")
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Relationship to Meeting model
    meeting = relationship("Meeting", back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title!r}, status={self.status})"
