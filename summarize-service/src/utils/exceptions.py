"""Custom exceptions."""

from uuid import UUID


class SummarizeServiceError(Exception):
    """Base exception."""

    pass


class MeetingNotFoundError(SummarizeServiceError):
    """Meeting not found."""

    def __init__(self, meeting_id: UUID):
        super().__init__(f"Meeting {meeting_id} not found")
        self.meeting_id = meeting_id


class InvalidStatusError(SummarizeServiceError):
    """Invalid meeting status."""

    pass


class AIServiceError(SummarizeServiceError):
    """AI service error."""

    pass


class ConfigurationError(SummarizeServiceError):
    """Invalid configuration."""

    pass
