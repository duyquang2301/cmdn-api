"""Get meeting status use case."""

import logging
from dataclasses import dataclass
from uuid import UUID

from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.support.logger.logger import Logger
from app.util.enums.status import Status
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class FindMeetingStatusUseCaseInput:
    """Input for get meeting status use case."""

    meeting_id: UUID


@dataclass(frozen=True)
class FindMeetingStatusUseCaseOutput:
    """Output for get meeting status use case."""

    meeting_id: UUID
    status: Status
    transcribe_done: int
    transcribe_total: int
    summarize_done: int
    summarize_total: int


class FindMeetingStatusUseCase:
    """Get meeting status use case."""

    def __init__(
        self,
        meeting_repository: MeetingRepository,
        logger: Logger,
    ) -> None:
        self._meeting_repository = meeting_repository
        self._logger = logger

    async def execute(
        self, input: FindMeetingStatusUseCaseInput
    ) -> Result[FindMeetingStatusUseCaseOutput, Exception]:
        """Execute get meeting status use case."""
        self._logger.info(f"Get meeting status: {input.meeting_id}")

        result = await self._meeting_repository.find_status_in_progress_by_id(
            input.meeting_id
        )

        if result.is_failure():
            self._logger.error(f"Failed to get meeting status: {result.error}")
            return failure(result.error)

        meeting = result.data
        if meeting is None:
            error = Exception(f"Meeting not found: {input.meeting_id}")
            self._logger.error(str(error))
            return failure(error)

        output = FindMeetingStatusUseCaseOutput(
            meeting_id=meeting.id,
            status=meeting.status,
            transcribe_done=meeting.transcribe_done,
            transcribe_total=meeting.transcribe_total,
            summarize_done=meeting.summarize_done,
            summarize_total=meeting.summarize_total,
        )

        self._logger.info(f"Get meeting status: done. Status={meeting.status}")
        return success(output)
