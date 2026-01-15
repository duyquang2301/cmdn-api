"""List meetings endpoint."""

import math
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.handler.api.middleware.auth_middleware import get_jwt_payload
from app.domain.support.logger.logger import Logger
from app.use_case.find_meeting_list_use_case import (
    FindMeetingListUseCase,
    FindMeetingListUseCaseInput,
    MeetingListItem,
)
from app.util.enums.status import Status
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    UnexpectedError,
)
from app.util.response_models import ErrorResponse, PaginatedResponse, PaginationMeta


class FindMeetingListRequest(BaseModel):
    """Query parameters for listing meetings"""

    model_config = ConfigDict(frozen=True)

    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 10
    status: Status | None = None


def find_meeting_list_route() -> APIRouter:
    """Find meeting list route"""
    router = APIRouter()

    @router.get(
        "/",
        status_code=status.HTTP_200_OK,
        responses={
            200: {
                "description": "Meeting list retrieved successfully",
                "model": PaginatedResponse[MeetingListItem],
            },
            500: {
                "description": "Internal server error",
                "model": ErrorResponse,
            },
        },
    )
    @inject
    async def find_meeting_list(
        request: Annotated[FindMeetingListRequest, Depends()],
        response: Response,
        use_case: FromDishka[FindMeetingListUseCase],
        logger: FromDishka[Logger],
        jwt_payload: dict = Depends(get_jwt_payload),
    ) -> PaginatedResponse[MeetingListItem] | ErrorResponse:
        """Get paginated list of meetings."""
        try:
            auth0_user_id = jwt_payload.get("sub")
            if not auth0_user_id:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return ErrorResponse(
                    name="UnauthorizedError", message="Invalid token: missing user ID"
                )

            offset = (request.page - 1) * request.page_size
            limit = request.page_size

            input_data = FindMeetingListUseCaseInput(
                auth0_user_id=auth0_user_id,
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
            total_pages = math.ceil(data["total"] / request.page_size)

            return PaginatedResponse(
                data=data["items"],
                meta=PaginationMeta(
                    page=request.page,
                    page_size=request.page_size,
                    total_items=data["total"],
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
