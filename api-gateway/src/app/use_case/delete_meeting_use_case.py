"""Delete meeting use case."""

import logging
from dataclasses import dataclass
from uuid import UUID

from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.support.logger.logger import Logger
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteMeetingUseCaseInput:
    """Input for delete meeting use case."""

    meeting_id: UUID


@dataclass(frozen=True, slots=True)
class DeleteMeetingUseCaseOutput:
    """Output for delete meeting use case."""

    success: bool


class DeleteMeetingUseCase:
    """Delete meeting use case."""

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
        self, input: DeleteMeetingUseCaseInput
    ) -> Result[DeleteMeetingUseCaseOutput, Exception]:
        """Execute delete meeting use case."""
        self._logger.info(f"Delete meeting: started. ID: '{input.meeting_id}'")

        try:
            find_result = await self._meeting_repository.find_by_id(input.meeting_id)

            if find_result.success is False:
                return failure(find_result.error)

            meeting = find_result.data

            if meeting is None:
                raise Exception(str(input.meeting_id))

            delete_result = await self._meeting_repository.delete(meeting)

            if delete_result.success is False:
                return failure(delete_result.error)

            await self._transaction_manager.commit()

            self._logger.info(f"Delete meeting: done. ID: '{input.meeting_id}'")

            return success(DeleteMeetingUseCaseOutput(success=True))

        except Exception as e:
            self._logger.error(f"Delete meeting: failed. Error: {e!s}")
            await self._transaction_manager.rollback()
            return failure(e)
