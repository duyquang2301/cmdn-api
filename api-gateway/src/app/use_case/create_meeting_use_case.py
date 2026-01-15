"""Create meeting use case."""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.domain.model.meeting.meeting import Meeting
from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.support.logger.logger import Logger
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.util.enums.status import Status
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateMeetingUseCaseInput:
    """Input for create meeting use case."""

    title: str
    description: str | None = None
    audio_url: str | None = None


class CreateMeetingUseCaseOutput(TypedDict):
    """Output for create meeting use case."""

    id: UUID


class CreateMeetingUseCase:
    """Create new meeting use case."""

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
        self, input: CreateMeetingUseCaseInput
    ) -> Result[CreateMeetingUseCaseOutput, Exception]:
        """Execute create meeting use case."""
        self._logger.info(f"Create meeting: started. Title: '{input.title}'")

        try:
            meeting = Meeting.create(
                title=input.title,
                description=input.description,
                audio_url=input.audio_url,
                status=Status.PROCESSING,
            )

            save_result = await self._meeting_repository.save(meeting)

            if save_result.success is False:
                return failure(save_result.error)

            await self._transaction_manager.commit()

            self._logger.info(f"Create meeting: done. ID: '{meeting.id}'")

            return success(CreateMeetingUseCaseOutput(id=meeting.id))

        except Exception as e:
            self._logger.error(f"Create meeting: failed. Error: {e!s}")
            await self._transaction_manager.rollback()
            return failure(e)
