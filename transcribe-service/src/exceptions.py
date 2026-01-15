"""Custom exceptions."""


class TranscribeError(Exception):
    """Base exception for transcribe service."""


class ConfigurationError(TranscribeError):
    """Configuration error."""


class MeetingNotFoundError(TranscribeError):
    """Meeting not found."""

    def __init__(self, meeting_id: str):
        super().__init__(f"Meeting {meeting_id} not found")
        self.meeting_id = meeting_id


class MeetingStatusError(TranscribeError):
    """Invalid meeting status."""

    def __init__(self, meeting_id: str, current: str, required: str):
        super().__init__(
            f"Meeting {meeting_id} has status '{current}', requires '{required}'"
        )
        self.meeting_id = meeting_id
        self.current_status = current
        self.required_status = required


class AudioProcessingError(TranscribeError):
    """Audio processing failed."""


class TranscriptionFailedError(TranscribeError):
    """Transcription failed."""


class StorageError(TranscribeError):
    """Storage operation failed."""


class StreamingError(AudioProcessingError):
    """Base error for streaming operations."""


class S3ThrottlingError(StreamingError):
    """S3 throttling detected."""


class NetworkRetryExhausted(StreamingError):
    """All retry attempts exhausted."""
