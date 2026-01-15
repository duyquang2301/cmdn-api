"""Application enums."""

from enum import Enum


class MeetingStatus(str, Enum):
    """Meeting status."""

    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    SUMMARIZING = "summarizing"
    SUMMARIZED = "summarized"
    COMPLETED = "completed"
    TRANSCRIBE_FAILED = "transcribe_failed"
    SUMMARIZE_FAILED = "summarize_failed"
    FAILED = "failed"
