"""Exception classes for error handling."""

from dataclasses import dataclass


class ExhaustiveError(Exception):
    """Error used for exhaustive checks to ensure all cases are handled."""

    def __init__(self, value: object, message: str | None = None) -> None:
        if message is None:
            message = f"Unsupported type: {value}"
        super().__init__(message)
        self.value = value

    @property
    def name(self) -> str:
        return "ExhaustiveError"


# Unexpected error
UNEXPECTED_ERROR_MESSAGE = "An unexpected error occurred."


class UnexpectedError(Exception):
    """Unexpected error."""

    def __init__(self, message: str = UNEXPECTED_ERROR_MESSAGE) -> None:
        super().__init__(message)
        self.message = message

    @property
    def name(self) -> str:
        return "UnexpectedError"


# Request error
BAD_REQUEST_ERROR_MESSAGE = "There is a problem with the request"


class BadRequestError(Exception):
    """Request error."""

    def __init__(self, message: str = BAD_REQUEST_ERROR_MESSAGE) -> None:
        super().__init__(message)
        self.message = message

    @property
    def name(self) -> str:
        return "BadRequestError"


# DB Error
class DatabaseError(Exception):
    """Database error."""

    def __init__(self, message: str = "Database error occurred") -> None:
        super().__init__(message)
        self.message = message

    @property
    def name(self) -> str:
        return "DatabaseError"


# Access Denied Error
ACCESS_DENIED_MESSAGE = "Access Denied"


class AccessDeniedError(Exception):
    """Access denied error."""

    def __init__(self, message: str = ACCESS_DENIED_MESSAGE) -> None:
        super().__init__(message)
        self.message = message

    @property
    def name(self) -> str:
        return "AccessDeniedError"


# Forbidden Error
FORBIDDEN_MESSAGE = "Access to this resource on the server is denied"


class ForbiddenError(Exception):
    """Forbidden error."""

    def __init__(self, message: str = FORBIDDEN_MESSAGE) -> None:
        super().__init__(message)
        self.message = message

    @property
    def name(self) -> str:
        return "ForbiddenError"


class NotFoundError(Exception):
    """Base class for NotFound errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    @property
    def name(self) -> str:
        return self.__class__.__name__


class MeetingNotFoundException(NotFoundError):
    """Raised when a meeting is not found."""

    def __init__(self, meeting_id: str) -> None:
        super().__init__(f"Meeting not found(id: {meeting_id})")
        self.meeting_id = meeting_id


class TaskNotFoundException(NotFoundError):
    """Raised when a task is not found."""

    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task not found(id: {task_id})")
        self.task_id = task_id


class ValidationError(Exception):
    """Base class for validation errors."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.field = field

    @property
    def name(self) -> str:
        return self.__class__.__name__


class MeetingValidationError(ValidationError):
    """Meeting validation error"""

    pass


class TaskValidationError(ValidationError):
    """Task validation error"""

    pass


@dataclass
class QuotaExceededError(Exception):
    """Raised when upload would exceed user's quota."""

    message: str
    used_seconds: int
    daily_quota_seconds: int
    remaining_seconds: int
    requested_seconds: int

    def __str__(self) -> str:
        return self.message

    @property
    def name(self) -> str:
        return "QuotaExceededError"
