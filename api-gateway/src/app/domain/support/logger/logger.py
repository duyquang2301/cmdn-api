"""Logger interface."""

from typing import Any, Protocol


class Logger(Protocol):
    """
    Logger interface.

    Each log level refers to standard logging practices:
    - debug: Any information related to what is happening within the program
    - info: Actions initiated by the user, system operations
    - warning: Potential state that may cause errors in the future
    - error: All error states
    """

    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug message.

        Args:
            message: Log message
            **kwargs: Additional data
        """
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log info message.

        Args:
            message: Log message
            **kwargs: Additional data
        """
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log warning message.

        Args:
            message: Log message
            **kwargs: Additional data
        """
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """
        Log error message.

        Args:
            message: Log message
            **kwargs: Additional data
        """
        ...
