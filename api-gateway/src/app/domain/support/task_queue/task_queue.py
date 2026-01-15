"""Task queue interface."""

from typing import Any, Protocol
from uuid import UUID

from app.util.result import Result


class TaskQueue(Protocol):
    def send_transcribe_task(
        self, meeting_id: UUID, audio_url: str
    ) -> Result[str, Exception]:
        """
        Send transcription task to queue.

        """
        ...

    def send_task(
        self,
        *,
        task_name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        queue: str | None = None,
    ) -> Result[str, Exception]:
        """Generic task sender"""
        ...
