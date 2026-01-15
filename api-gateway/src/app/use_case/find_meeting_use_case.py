"""Find meeting by ID use case."""

import logging
from dataclasses import dataclass
from uuid import UUID

from app.domain.model.meeting.meeting import Meeting
from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.model.user.user_repository import UserRepository
from app.domain.support.logger.logger import Logger
from app.use_case.interfaces import UseCase
from app.util.exceptions import DatabaseError, MeetingNotFoundException, UnexpectedError
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class FindMeetingUseCaseInput:
    """Input for find meeting use case."""

    meeting_id: UUID
    auth0_user_id: str


FindMeetingUseCaseException = MeetingNotFoundException | DatabaseError | UnexpectedError


class FindMeetingUseCase(
    UseCase[FindMeetingUseCaseInput, Meeting, FindMeetingUseCaseException]
):
    """Find meeting by ID use case."""

    def __init__(
        self,
        *,
        meeting_repository: MeetingRepository,
        user_repository: UserRepository,
        logger: Logger,
    ) -> None:
        self._meeting_repository = meeting_repository
        self._user_repository = user_repository
        self._logger = logger

    async def execute(
        self, input: FindMeetingUseCaseInput
    ) -> Result[Meeting, FindMeetingUseCaseException]:
        """Execute find meeting use case."""
        self._logger.debug("execute find-meeting-use-case")
        self._logger.info(
            f"Find meeting: started. ID: '{input.meeting_id}', User: '{input.auth0_user_id}'"
        )

        # Get user from auth0_user_id
        user_result = await self._user_repository.find_by_auth0_id(input.auth0_user_id)
        if not user_result.success or user_result.data is None:
            self._logger.error(f"User not found: {input.auth0_user_id}")
            return failure(UnexpectedError(f"User not found: {input.auth0_user_id}"))

        user = user_result.data

        # Find meeting by ID and user_id
        find_result = await self._meeting_repository.find_by_id(
            input.meeting_id, user.id
        )

        if find_result.success is False:
            self._logger.error(f"Database error: {find_result.error}")
            return failure(DatabaseError(str(find_result.error)))

        meeting = find_result.data

        if meeting is None:
            self._logger.debug(
                f"Meeting not found or not owned by user: {input.meeting_id}"
            )
            return failure(MeetingNotFoundException(input.meeting_id))

        self._logger.info(f"Find meeting: done. ID: '{meeting.id}'")
        return success(meeting)
