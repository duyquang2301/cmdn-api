"""Update meeting endpoint."""

from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.domain.support.logger.logger import Logger
from app.use_case.update_meeting_use_case import (
    UpdateMeetingUseCase,
    UpdateMeetingUseCaseInput,
    UpdateMeetingUseCaseOutput,
)
from app.util.enums.status import Status
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    MeetingNotFoundException,
    MeetingValidationError,
    UnexpectedError,
)
from app.util.response_models import DataResponse, ErrorResponse


class UpdateMeetingRequest(BaseModel):
    """Request body for updating meeting"""

    model_config = ConfigDict(frozen=True)

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    audio_url: str | None = None
    duration: float | None = Field(None, gt=0, description="Audio duration in seconds")
    status: Status | None = None
    transcribe_text: str | None = None
    summarize: str | None = None
    transcribe_segments: list | None = None
    key_notes: list | None = None


def update_meeting_route() -> APIRouter:
    """Update meeting route"""
    router = APIRouter()

    @router.put(
        "/{meeting_id}",
        status_code=status.HTTP_200_OK,
        responses={
            200: {
                "description": "Meeting updated successfully",
                "model": DataResponse[UpdateMeetingUseCaseOutput],
            },
            400: {
                "description": "Validation error",
                "model": ErrorResponse,
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
    async def update_meeting(
        meeting_id: UUID,
        request: UpdateMeetingRequest,
        response: Response,
        use_case: FromDishka[UpdateMeetingUseCase],
        logger: FromDishka[Logger],
    ) -> DataResponse[UpdateMeetingUseCaseOutput] | ErrorResponse:
        """Update meeting by ID."""
        try:
            input_data = UpdateMeetingUseCaseInput(
                meeting_id=meeting_id,
                title=request.title,
                description=request.description,
                audio_url=request.audio_url,
                duration=request.duration,
                status=request.status,
                transcribe_text=request.transcribe_text,
                summarize=request.summarize,
                transcribe_segments=request.transcribe_segments,
                key_notes=request.key_notes,
            )

            use_case_result = await use_case.execute(input_data)

            if not use_case_result.success:
                error = use_case_result.error

                if isinstance(error, MeetingValidationError):
                    logger.error(error.message)
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return ErrorResponse(
                        name=error.name,
                        message=error.message,
                    )

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

            return DataResponse(data=use_case_result.data)

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name,
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
