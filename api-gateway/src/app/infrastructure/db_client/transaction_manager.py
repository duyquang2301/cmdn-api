"""Transaction manager interface."""

from typing import Protocol


class TransactionManager(Protocol):
    """
    Transaction manager interface.

    Manages database transaction lifecycle.
    """

    async def commit(self) -> None:
        """Commit current transaction"""
        ...

    async def rollback(self) -> None:
        """Rollback current transaction"""
        ...
