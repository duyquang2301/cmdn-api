"""Celery task queue implementation."""

import logging
from typing import Any
from uuid import UUID

from celery import Celery

from app.domain.support.logger.logger import Logger
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


class CeleryQueueImpl:
    """Celery task queue implementation."""

    def __init__(self, *, celery_app: Celery, logger: Logger) -> None:
        """Initialize with Celery app instance."""
        self._celery = celery_app
        self._logger = logger

    def send_transcribe_task(
        self,
        meeting_id: UUID,
        audio_url: str,
    ) -> Result[str, Exception]:
        """Send transcription task to queue"""
        try:
            self._logger.info(f"Sending transcribe task for meeting: {meeting_id}")

            result = self._celery.send_task(
                "audio.transcribe.start",  # Clean task name
                args=[str(meeting_id), audio_url],
                queue="audio.transcribe",  # Clean queue name
            )

            self._logger.info(f"Transcribe task sent: {result.id}")
            return success(result.id)
        except Exception as e:
            self._logger.error(f"Failed to send transcribe task: {e}")
            return failure(e)

    def send_task(
        self,
        *,
        task_name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        queue: str | None = None,
    ) -> Result[str, Exception]:
        """Generic task sender"""
        try:
            self._logger.info(f"Sending task: {task_name}")

            result = self._celery.send_task(
                task_name,
                args=args or [],
                kwargs=kwargs or {},
                queue=queue,
            )

            self._logger.info(f"Task sent: {result.id}")
            return success(result.id)
        except Exception as e:
            self._logger.error(f"Failed to send task: {e}")
            return failure(e)
