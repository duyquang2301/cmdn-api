"""Flusher implementation (deprecated)."""

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


class FlusherImpl:
    """
    SQLAlchemy flusher implementation.

    Flushes pending changes to database without committing.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def flush(self) -> None:
        """Flush pending changes to database"""
        try:
            await self._session.flush()
            log.debug("Session flushed successfully")
        except SQLAlchemyError as e:
            log.error(f"Failed to flush session: {e}")
            raise
