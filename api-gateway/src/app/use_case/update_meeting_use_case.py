"""Update meeting use case."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.support.logger.logger import Logger
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.util.enums.status import Status
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateMeetingUseCaseInput:
    """Input for update meeting use case."""

    meeting_id: UUID
    title: str | None = None
    description: str | None = None
    audio_url: str | None = None
    duration: float | None = None
    status: Status | None = None
    transcribe_text: str | None = None
    summarize: str | None = None
    transcribe_segments: list | None = None
    key_notes: list | None = None


@dataclass(frozen=True, slots=True)
class UpdateMeetingUseCaseOutput:
    """Output for update meeting use case."""

    id: UUID


class UpdateMeetingUseCase:
    """Update meeting use case."""

    def __init__(
        self,
        *,
        meeting_repository: MeetingRepository,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> None:
        self._meeting_repository = meeting_repository
        self._transaction_manager = transaction_manager
        self._logger = logger

    async def execute(
        self, input: UpdateMeetingUseCaseInput
    ) -> Result[UpdateMeetingUseCaseOutput, Exception]:
        """Execute update meeting use case."""
        self._logger.info(f"Update meeting: started. ID: '{input.meeting_id}'")

        try:
            find_result = await self._meeting_repository.find_by_id(input.meeting_id)

            if find_result.success is False:
                return failure(find_result.error)

            meeting = find_result.data

            if meeting is None:
                raise Exception(str(input.meeting_id))

            if input.title is not None:
                meeting.update_title(input.title)

            if input.description is not None:
                meeting.update_description(input.description)

            if input.audio_url is not None:
                meeting.set_audio_url(input.audio_url, input.duration)

            if input.duration is not None and input.audio_url is None:
                meeting.duration = input.duration
                meeting.updated_at = datetime.now(UTC)

            if input.status is not None:
                meeting.status = input.status
                meeting.updated_at = datetime.now(UTC)

            if input.transcribe_text is not None:
                meeting.transcribe_text = input.transcribe_text
                meeting.updated_at = datetime.now(UTC)

            if input.summarize is not None:
                meeting.summarize = input.summarize
                meeting.updated_at = datetime.now(UTC)

            if input.transcribe_segments is not None:
                meeting.transcribe_segments = input.transcribe_segments
                meeting.updated_at = datetime.now(UTC)

            if input.key_notes is not None:
                meeting.key_notes = input.key_notes
                meeting.updated_at = datetime.now(UTC)

            await self._transaction_manager.commit()

            self._logger.info(f"Update meeting: done. ID: '{meeting.id}'")

            return success(UpdateMeetingUseCaseOutput(id=meeting.id))

        except Exception as e:
            self._logger.error(f"Update meeting: failed. Error: {e!s}")
            await self._transaction_manager.rollback()
            return failure(e)
