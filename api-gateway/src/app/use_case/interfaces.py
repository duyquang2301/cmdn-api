"""Use case interfaces."""

from typing import Generic, Protocol, TypeVar

from app.util.result import Result

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")
TException = TypeVar("TException", bound=Exception)


class UseCase(Protocol, Generic[TInput, TOutput, TException]):
    """Base use case interface."""

    async def execute(self, input: TInput) -> Result[TOutput, TException]:
        """Execute use case with input and return result."""
        ...
