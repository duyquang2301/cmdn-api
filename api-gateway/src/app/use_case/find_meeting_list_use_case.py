"""Find meeting list use case."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
from uuid import UUID

from app.domain.model.meeting.meeting_repository import MeetingRepository
from app.domain.model.user.user_repository import UserRepository
from app.domain.support.logger.logger import Logger
from app.use_case.interfaces import UseCase
from app.util.enums.status import Status
from app.util.exceptions import DatabaseError, UnexpectedError
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


class MeetingListItem(TypedDict):
    """Single meeting item in list."""

    id: UUID
    user_id: UUID | None
    title: str
    description: str | None
    audio_url: str | None
    duration: float | None
    status: Status
    transcribe_text: str | None
    summarize: str | None
    transcribe_segments: list | None
    key_notes: list | None
    transcribe_total: int
    transcribe_done: int
    summarize_total: int
    summarize_done: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class FindMeetingListUseCaseInput:
    """Input for find meeting list use case."""

    auth0_user_id: str
    limit: int = 10
    offset: int = 0
    status: Status | None = None


class FindMeetingListUseCaseOutput(TypedDict):
    """Output for find meeting list use case."""

    items: list[MeetingListItem]
    total: int
    limit: int
    offset: int


FindMeetingListUseCaseException = DatabaseError | UnexpectedError


class FindMeetingListUseCase(
    UseCase[
        FindMeetingListUseCaseInput,
        FindMeetingListUseCaseOutput,
        FindMeetingListUseCaseException,
    ]
):
    """Find meeting list use case with pagination."""

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
        self, input: FindMeetingListUseCaseInput
    ) -> Result[FindMeetingListUseCaseOutput, FindMeetingListUseCaseException]:
        """Execute find meeting list use case."""
        self._logger.debug("execute find-meeting-list-use-case")
        self._logger.info(
            f"Find meeting list: started. User: '{input.auth0_user_id}', "
            f"Limit: {input.limit}, Offset: {input.offset}, Status: {input.status}"
        )

        # Get user from auth0_user_id
        user_result = await self._user_repository.find_by_auth0_id(input.auth0_user_id)
        if not user_result.success or user_result.data is None:
            self._logger.error(f"User not found: {input.auth0_user_id}")
            return failure(UnexpectedError(f"User not found: {input.auth0_user_id}"))

        user = user_result.data

        # Find meetings by user_id
        find_result = await self._meeting_repository.find_many(
            user_id=user.id,
            limit=input.limit,
            offset=input.offset,
            status=input.status,
        )

        if find_result.success is False:
            self._logger.error(f"Database error: {find_result.error}")
            return failure(DatabaseError(str(find_result.error)))

        count_result = await self._meeting_repository.count(
            user_id=user.id, status=input.status
        )

        if count_result.success is False:
            self._logger.error(f"Database error: {count_result.error}")
            return failure(DatabaseError(str(count_result.error)))

        items = [
            MeetingListItem(
                id=meeting.id,
                user_id=meeting.user_id,
                title=meeting.title,
                description=meeting.description,
                audio_url=meeting.audio_url,
                duration=meeting.duration,
                status=meeting.status,
                transcribe_text=meeting.transcribe_text,
                summarize=meeting.summarize,
                transcribe_segments=meeting.transcribe_segments,
                key_notes=meeting.key_notes,
                transcribe_total=meeting.transcribe_total,
                transcribe_done=meeting.transcribe_done,
                summarize_total=meeting.summarize_total,
                summarize_done=meeting.summarize_done,
                created_at=meeting.created_at,
                updated_at=meeting.updated_at,
            )
            for meeting in find_result.data
        ]

        self._logger.info(f"Find meeting list: done. Found {len(items)} meetings")

        return success(
            FindMeetingListUseCaseOutput(
                items=items,
                total=count_result.data,
                limit=input.limit,
                offset=input.offset,
            )
        )
