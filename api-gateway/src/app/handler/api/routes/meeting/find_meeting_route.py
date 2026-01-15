"""Find meeting endpoint."""

from datetime import datetime
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from app.handler.api.middleware.auth_middleware import get_jwt_payload
from app.domain.support.logger.logger import Logger
from app.use_case.find_meeting_use_case import (
    FindMeetingUseCase,
    FindMeetingUseCaseInput,
)
from app.util.enums.status import Status
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    MeetingNotFoundException,
    UnexpectedError,
)
from app.util.response_models import DataResponse, ErrorResponse


class FindMeetingResponse(BaseModel):
    """Response for find meeting"""

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


def find_meeting_route() -> APIRouter:
    """Find meeting route"""
    router = APIRouter()

    @router.get(
        "/{meeting_id}",
        status_code=status.HTTP_200_OK,
        responses={
            200: {
                "description": "Meeting retrieved successfully",
                "model": DataResponse[FindMeetingResponse],
            },
            404: {
                "description": "Meeting not found",
                "model": ErrorResponse,
            },
            500: {
                "description": "Internal server error",
                "model": ErrorResponse,
            },
        },
    )
    @inject
    async def find_meeting(
        meeting_id: UUID,
        response: Response,
        use_case: FromDishka[FindMeetingUseCase],
        logger: FromDishka[Logger],
        jwt_payload: dict = Depends(get_jwt_payload),
    ) -> DataResponse[FindMeetingResponse] | ErrorResponse:
        """Find meeting by ID."""
        try:
            
            auth0_user_id = jwt_payload.get("sub")
            if not auth0_user_id:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return ErrorResponse(
                    name="UnauthorizedError", message="Invalid token: missing user ID"
                )
            input_data = FindMeetingUseCaseInput(
                meeting_id=meeting_id,
                auth0_user_id=auth0_user_id
            )
            use_case_result = await use_case.execute(input_data)

            if not use_case_result.success:
                error = use_case_result.error

                if isinstance(error, MeetingNotFoundException):
                    logger.error(error.message)
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return ErrorResponse(
                        name=error.name,
                        message=error.message,
                    )

                if isinstance(error, (UnexpectedError, DatabaseError)):
                    logger.error(f"{UNEXPECTED_ERROR_MESSAGE}: {error}")
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    return ErrorResponse(
                        name=error.name,
                        message=UNEXPECTED_ERROR_MESSAGE,
                    )

                raise ExhaustiveError(error)

            meeting = use_case_result.data

            return DataResponse(
                data=FindMeetingResponse(
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
            )

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name,
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
