"""Result type for error handling."""

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    """Success result type."""

    success: bool = True
    data: T = None  # type: ignore

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class Failure(Generic[E]):
    """Failure result type."""

    success: bool = False
    error: E = None  # type: ignore

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True


# Result type - Union of Success and Failure
Result = Union[Success[T], Failure[E]]


def success(data: T) -> Success[T]:
    """Create a Success result."""
    return Success(data=data)


def failure(error: E) -> Failure[E]:
    """Create a Failure result."""
    return Failure(error=error)
