"""Meeting status enum."""

from enum import StrEnum


class Status(StrEnum):
    """Meeting status enumeration"""

    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    TRANSCRIBE_FAILED = "transcribe_failed"
    SUMMARIZING = "summarizing"
    SUMMARIZED = "summarized"
    COMPLETED = "completed"
    SUMMARIZE_FAILED = "summarize_failed"
