"""Enumerations."""

from enum import Enum


class MeetingStatus(str, Enum):
    """Meeting status."""

    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    TRANSCRIBE_FAILED = "transcribe_failed"
    SUMMARIZE_FAILED = "summarize_failed"

    @property
    def is_failed(self) -> bool:
        """Check if status indicates failure."""
        return self in {self.TRANSCRIBE_FAILED, self.SUMMARIZE_FAILED}

    @property
    def is_complete(self) -> bool:
        """Check if status indicates completion."""
        return self in {self.TRANSCRIBED, self.COMPLETED}


class TranscriptionProvider(str, Enum):
    """Transcription provider."""

    MLX = "mlx"
    GPU = "gpu"
    LITELLM = "litellm"


class URLType(str, Enum):
    """URL type for audio sources."""

    S3_DIRECT = "s3_direct"  # s3://bucket/key - requires boto3
    HTTP = "http"  # http://, https://, and S3 presigned URLs - use requests
