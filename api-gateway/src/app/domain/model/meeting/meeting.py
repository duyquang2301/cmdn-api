"""Meeting aggregate root."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.domain.model.base import Entity
from app.util.enums.status import Status


class Meeting(Entity):
    """Meeting aggregate root"""

    def __init__(
        self,
        *,
        id: UUID,
        title: str,
        description: str | None = None,
        audio_url: str | None = None,
        duration: float | None = None,
        user_id: UUID | None = None,
        status: Status = Status.PROCESSING,
        transcribe_text: str | None = None,
        summarize: str | None = None,
        transcribe_segments: list[dict[str, Any]] | None = None,
        key_notes: list[str] | None = None,
        transcribe_total: int = 0,
        transcribe_done: int = 0,
        summarize_total: int = 0,
        summarize_done: int = 0,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id)
        self.title = title
        self.description = description
        self.audio_url = audio_url
        self.duration = duration
        self.user_id = user_id
        self.status = status
        self.transcribe_text = transcribe_text
        self.summarize = summarize
        self.transcribe_segments = transcribe_segments
        self.key_notes = key_notes
        self.transcribe_total = transcribe_total
        self.transcribe_done = transcribe_done
        self.summarize_total = summarize_total
        self.summarize_done = summarize_done
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    @staticmethod
    def create(
        *,
        id: UUID | None = None,
        title: str,
        description: str | None = None,
        audio_url: str | None = None,
        duration: float | None = None,
        user_id: UUID | None = None,
        status: Status = Status.PROCESSING,
    ) -> "Meeting":
        """Factory method with validation"""
        if not title or not title.strip():
            raise ValueError("Meeting title cannot be empty")

        if len(title) > 255:
            raise ValueError("Meeting title cannot exceed 255 characters")

        now = datetime.now(UTC)
        return Meeting(
            id=id or uuid4(),
            title=title.strip(),
            description=description.strip() if description else None,
            audio_url=audio_url,
            duration=duration,
            user_id=user_id,
            status=status,
            transcribe_text=None,
            summarize=None,
            transcribe_segments=None,
            key_notes=None,
            created_at=now,
            updated_at=now,
        )

    def __repr__(self) -> str:
        return f"Meeting(id={self.id}, title={self.title!r}, status={self.status})"

    # Business methods
    def update_title(self, new_title: str) -> None:
        if not new_title or not new_title.strip():
            raise ValueError("Meeting title cannot be empty")
        if len(new_title) > 255:
            raise ValueError("Meeting title cannot exceed 255 characters")
        self.title = new_title.strip()
        self.updated_at = datetime.now(UTC)

    def update_description(self, new_description: str | None) -> None:
        self.description = new_description.strip() if new_description else None
        self.updated_at = datetime.now(UTC)

    def set_audio_url(self, audio_url: str, duration: float | None = None) -> None:
        self.audio_url = audio_url
        if duration is not None:
            self.duration = duration
        self.updated_at = datetime.now(UTC)

    def set_transcribe_result(
        self,
        transcribe_text: str,
        transcribe_segments: list[dict[str, Any]] | None = None,
    ) -> None:
        self.transcribe_text = transcribe_text
        self.transcribe_segments = (
            transcribe_segments if transcribe_segments is not None else []
        )
        self.status = Status.TRANSCRIBED
        self.updated_at = datetime.now(UTC)

    def set_summarize_result(
        self,
        summarize: str,
        key_notes: list[str] | None = None,
    ) -> None:
        self.summarize = summarize
        self.key_notes = key_notes if key_notes is not None else []
        self.status = Status.COMPLETED
        self.updated_at = datetime.now(UTC)

    def mark_as_failed(self) -> None:
        self.status = Status.FAILED
        self.updated_at = datetime.now(UTC)
