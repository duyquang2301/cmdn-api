"""Get meeting status endpoint."""

from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response, status

from app.domain.support.logger.logger import Logger
from app.use_case.find_meeting_status_use_case import (
    FindMeetingStatusUseCase,
    FindMeetingStatusUseCaseInput,
    FindMeetingStatusUseCaseOutput,
)
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    MeetingNotFoundException,
    UnexpectedError,
)
from app.util.response_models import DataResponse, ErrorResponse


def find_meeting_status_route() -> APIRouter:
    """Get meeting status route"""
    router = APIRouter()

    @router.get(
        "/{meeting_id}/status",
        status_code=status.HTTP_200_OK,
        responses={
            200: {
                "description": "Meeting status retrieved successfully",
                "model": DataResponse[FindMeetingStatusUseCaseOutput],
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
    async def find_meeting_status(
        meeting_id: UUID,
        response: Response,
        use_case: FromDishka[FindMeetingStatusUseCase],
        logger: FromDishka[Logger],
    ) -> DataResponse[FindMeetingStatusUseCaseOutput] | ErrorResponse:
        """Get meeting status by ID."""
        try:
            input_data = FindMeetingStatusUseCaseInput(meeting_id=meeting_id)
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

            return DataResponse(data=use_case_result.data)

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name,
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
