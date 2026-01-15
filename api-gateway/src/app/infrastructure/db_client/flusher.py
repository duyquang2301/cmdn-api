"""Flusher interface (deprecated - use repository.save())."""

from typing import Protocol


class Flusher(Protocol):
    """
    Flusher interface.

    Flushes pending changes to database without committing.
    """

    async def flush(self) -> None:
        """Flush pending changes to database"""
        ...
