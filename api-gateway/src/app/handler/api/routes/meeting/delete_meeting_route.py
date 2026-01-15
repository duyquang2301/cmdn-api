"""Delete meeting endpoint."""

from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response, status

from app.domain.support.logger.logger import Logger
from app.use_case.delete_meeting_use_case import (
    DeleteMeetingUseCase,
    DeleteMeetingUseCaseInput,
)
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    MeetingNotFoundException,
    UnexpectedError,
)
from app.util.response_models import ErrorResponse


def delete_meeting_route() -> APIRouter:
    """Delete meeting route"""
    router = APIRouter()

    @router.delete(
        "/{meeting_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            204: {"description": "Meeting deleted successfully"},
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
    async def delete_meeting(
        meeting_id: UUID,
        response: Response,
        use_case: FromDishka[DeleteMeetingUseCase],
        logger: FromDishka[Logger],
    ) -> None:
        """Delete meeting by ID."""
        try:
            input_data = DeleteMeetingUseCaseInput(meeting_id=meeting_id)
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

            return None

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name,
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
