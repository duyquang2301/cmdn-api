"""Create meeting endpoint."""

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.domain.support.logger.logger import Logger
from app.use_case.create_meeting_use_case import (
    CreateMeetingUseCase,
    CreateMeetingUseCaseInput,
)
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    MeetingValidationError,
    UnexpectedError,
)
from app.util.response_models import CreatedResponse, ErrorResponse


class CreateMeetingRequest(BaseModel):
    """Request body for creating meeting"""

    model_config = ConfigDict(frozen=True)

    title: str = Field(..., min_length=1, max_length=255, description="Meeting title")
    description: str | None = Field(None, description="Meeting description")
    audio_url: str | None = Field(None, description="URL to audio file")


def create_meeting_route() -> APIRouter:
    """Create meeting route"""
    router = APIRouter()

    @router.post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses={
            201: {
                "description": "Meeting created successfully",
                "model": CreatedResponse,
            },
            400: {
                "description": "Validation error",
                "model": ErrorResponse,
            },
            500: {
                "description": "Internal server error",
                "model": ErrorResponse,
            },
        },
    )
    @inject
    async def create_meeting(
        request: CreateMeetingRequest,
        response: Response,
        use_case: FromDishka[CreateMeetingUseCase],
        logger: FromDishka[Logger],
    ) -> CreatedResponse | ErrorResponse:
        """Create a new meeting."""
        try:
            if not request.title or not request.title.strip():
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorResponse(
                    name="BadRequestError",
                    message="Title cannot be empty",
                )

            input_data = CreateMeetingUseCaseInput(
                title=request.title,
                description=request.description,
                audio_url=request.audio_url,
            )

            result = await use_case.execute(input_data)

            if not result.success:
                error = result.error
                if isinstance(error, MeetingValidationError):
                    response.status_code = status.HTTP_400_BAD_REQUEST
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

            return CreatedResponse(
                id=str(result.data["id"]),
                message="Meeting created successfully",
            )

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name,
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
