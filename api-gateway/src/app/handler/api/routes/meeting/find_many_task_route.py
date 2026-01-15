"""List tasks endpoint."""

import math
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.domain.support.logger.logger import Logger
from app.use_case.find_many_task_use_case import (
    FindManyTaskUseCase,
    FindManyTaskUseCaseInput,
    TaskItem,
)
from app.util.enums.task_status import TaskStatus
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    UnexpectedError,
)
from app.util.response_models import ErrorResponse, PaginatedResponse, PaginationMeta


class FindManyTaskRequest(BaseModel):
    """Query parameters for listing tasks"""

    model_config = ConfigDict(frozen=True)

    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 10
    status: TaskStatus | None = None


def find_many_task_route() -> APIRouter:
    """Find many tasks route"""
    router = APIRouter()

    @router.get(
        "/{meeting_id}/tasks",
        status_code=status.HTTP_200_OK,
        responses={
            200: {
                "description": "Task list retrieved successfully",
                "model": PaginatedResponse[TaskItem],
            },
            500: {
                "description": "Internal server error",
                "model": ErrorResponse,
            },
        },
    )
    @inject
    async def find_many_task(
        meeting_id: UUID,
        request: Annotated[FindManyTaskRequest, Depends()],
        response: Response,
        use_case: FromDishka[FindManyTaskUseCase],
        logger: FromDishka[Logger],
    ) -> PaginatedResponse[TaskItem] | ErrorResponse:
        """Get paginated list of tasks for a meeting."""
        try:
            offset = (request.page - 1) * request.page_size
            limit = request.page_size

            input_data = FindManyTaskUseCaseInput(
                meeting_id=meeting_id,
                limit=limit,
                offset=offset,
                status=request.status,
            )

            use_case_result = await use_case.execute(input_data)

            if not use_case_result.success:
                error = use_case_result.error

                if isinstance(error, (UnexpectedError, DatabaseError)):
                    logger.error(f"{UNEXPECTED_ERROR_MESSAGE}: {error}")
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    return ErrorResponse(
                        name=error.name,
                        message=UNEXPECTED_ERROR_MESSAGE,
                    )

                raise ExhaustiveError(error)

            data = use_case_result.data
            total_pages = math.ceil(data.total / request.page_size)

            return PaginatedResponse(
                data=data.items,
                meta=PaginationMeta(
                    page=request.page,
                    page_size=request.page_size,
                    total_items=data.total,
                    total_pages=total_pages,
                ),
            )

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name,
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
