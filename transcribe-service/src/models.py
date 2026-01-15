"""Domain models using dataclasses."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from .enums import MeetingStatus


@dataclass
class Segment:
    """Audio transcription segment with timing information."""

    start: float  # Start time in seconds
    end: float  # End time in seconds
    text: str  # Transcribed text

    def __post_init__(self):
        if self.start < 0 or self.end < 0:
            raise ValueError("Timestamps must be non-negative")
        if self.start > self.end:
            raise ValueError("Start time must be before end time")

    @property
    def duration(self) -> float:
        """Segment duration in seconds."""
        return self.end - self.start


@dataclass
class ChunkResult:
    """Result from processing a single audio chunk."""

    chunk_id: int
    segments: list[Segment]
    status: str  # "success" or "failed"
    error: str | None = None

    @property
    def is_success(self) -> bool:
        """Check if chunk was processed successfully."""
        return self.status == "success"

    @property
    def segment_count(self) -> int:
        """Number of segments in chunk."""
        return len(self.segments)


@dataclass
class Meeting:
    """Meeting domain model."""

    id: UUID
    title: str
    status: MeetingStatus
    audio_url: str | None = None
    transcript: str | None = None
    summary: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def mark_processing(self) -> None:
        """Mark meeting as processing."""
        self.status = MeetingStatus.PROCESSING
        self._update_timestamp()

    def mark_transcribing(self) -> None:
        """Mark meeting as transcribing."""
        self.status = MeetingStatus.TRANSCRIBING
        self._update_timestamp()

    def mark_transcribed(self, transcript: str) -> None:
        """Mark meeting as transcribed."""
        self.status = MeetingStatus.TRANSCRIBED
        self.transcript = transcript
        self._update_timestamp()

    def mark_failed(self, error: str) -> None:
        """Mark meeting as failed."""
        self.status = MeetingStatus.TRANSCRIBE_FAILED
        self._update_timestamp()

    def can_transcribe(self) -> bool:
        """Check if meeting can be transcribed."""
        return self.status in {
            MeetingStatus.PROCESSING,
            MeetingStatus.TRANSCRIBE_FAILED,
        }
