"""Transaction manager implementation."""

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


class TransactionManagerImpl:
    """
    SQLAlchemy transaction manager implementation.

    Manages database transaction lifecycle.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """Commit current transaction"""
        try:
            await self._session.commit()
            log.debug("Transaction committed successfully")
        except SQLAlchemyError as e:
            log.error(f"Failed to commit transaction: {e}")
            raise

    async def rollback(self) -> None:
        """Rollback current transaction"""
        try:
            await self._session.rollback()
            log.debug("Transaction rolled back successfully")
        except SQLAlchemyError as e:
            log.error(f"Failed to rollback transaction: {e}")
            raise
