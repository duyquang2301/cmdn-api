"""Upload audio endpoint."""

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from app.domain.support.logger.logger import Logger
from app.handler.api.middleware.auth_middleware import get_jwt_payload
from app.use_case.upload_audio_use_case import (
    UploadAudioUseCase,
    UploadAudioUseCaseInput,
    UploadAudioUseCaseOutput,
)
from app.util.exceptions import (
    UNEXPECTED_ERROR_MESSAGE,
    DatabaseError,
    ExhaustiveError,
    QuotaExceededError,
    UnexpectedError,
)
from app.util.response_models import DataResponse, ErrorResponse


def upload_audio_route() -> APIRouter:
    """Upload audio route."""
    router = APIRouter()

    @router.post(
        "/upload",
        status_code=status.HTTP_201_CREATED,
        responses={
            201: {
                "description": "Audio uploaded successfully",
                "model": DataResponse[UploadAudioUseCaseOutput],
            },
            400: {"description": "Bad request", "model": ErrorResponse},
            401: {"description": "Unauthorized", "model": ErrorResponse},
            429: {"description": "Quota exceeded", "model": ErrorResponse},
            500: {"description": "Internal server error", "model": ErrorResponse},
        },
    )
    @inject
    async def upload_audio(
        file: UploadFile = File(..., description="Audio file to upload"),
        response: Response = None,
        use_case: FromDishka[UploadAudioUseCase] = None,
        logger: FromDishka[Logger] = None,
        jwt_payload: dict = Depends(get_jwt_payload),
    ) -> DataResponse[UploadAudioUseCaseOutput] | ErrorResponse:
        """Upload audio file and create meeting."""
        try:
            if not file.filename:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return ErrorResponse(
                    name="BadRequestError", message="Filename is required"
                )

            auth0_user_id = jwt_payload.get("sub")
            if not auth0_user_id:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return ErrorResponse(
                    name="UnauthorizedError", message="Invalid token: missing user ID"
                )

            input_data = UploadAudioUseCaseInput(
                file=file.file,
                filename=file.filename,
                content_type=file.content_type or "audio/mpeg",
                auth0_user_id=auth0_user_id,
                email=jwt_payload.get("email"),
            )

            result = await use_case.execute(input_data)

            if not result.success:
                return _handle_error(result.error, response, logger)

            return DataResponse(data=result.data)

        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name=UnexpectedError().name, message=UNEXPECTED_ERROR_MESSAGE
            )

    return router


def _handle_error(
    error: Exception, response: Response, logger: Logger
) -> ErrorResponse:
    """Handle use case errors and return appropriate response."""
    if isinstance(error, QuotaExceededError):
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return ErrorResponse(
            name=error.name,
            message=str(error),
            details={
                "used_seconds": error.used_seconds,
                "daily_quota_seconds": error.daily_quota_seconds,
                "remaining_seconds": error.remaining_seconds,
                "requested_seconds": error.requested_seconds,
            },
        )

    if isinstance(error, ValueError):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(name="BadRequestError", message=str(error))

    if isinstance(error, (UnexpectedError, DatabaseError)):
        logger.error(f"{UNEXPECTED_ERROR_MESSAGE}: {error}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ErrorResponse(name=error.name, message=UNEXPECTED_ERROR_MESSAGE)

    raise ExhaustiveError(error)
