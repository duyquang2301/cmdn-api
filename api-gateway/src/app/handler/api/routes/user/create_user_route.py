"""Create user endpoint."""

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.domain.support.logger.logger import Logger
from app.handler.api.middleware.auth_middleware import get_jwt_payload
from app.use_case.create_user_use_case import (
    CreateUserUseCase,
    CreateUserUseCaseInput,
)
from app.util.enums.user_type import UserType
from app.util.exceptions import UNEXPECTED_ERROR_MESSAGE, DatabaseError, UnexpectedError
from app.util.response_models import ErrorResponse


class CreateUserRequest(BaseModel):
    """Request body for creating user."""

    model_config = ConfigDict(frozen=True)

    email: str | None = Field(None, description="User email address")
    user_type: UserType = Field(
        default=UserType.FREE,
        description="User type (FREE, PREMIUM, ENTERPRISE)",
    )


class CreateUserResponse(BaseModel):
    """Response for create user."""

    model_config = ConfigDict(frozen=True)

    user_id: str = Field(..., description="User ID")
    auth0_user_id: str = Field(..., description="Auth0 user ID")
    email: str | None = Field(None, description="User email")
    user_type: UserType = Field(..., description="User type")
    daily_quota_seconds: int | None = Field(
        None, description="Daily quota in seconds (null for unlimited)"
    )
    message: str = Field(..., description="Success message")


def create_user_route() -> APIRouter:
    """Create user route."""
    router = APIRouter()

    @router.post(
        "/",
        status_code=status.HTTP_201_CREATED,
        summary="Create user after Auth0 login",
        description=(
            "Create a new user in the system after successful Auth0 authentication. "
            "This endpoint is idempotent - if the user already exists, it returns the existing user. "
            "The auth0_user_id is extracted from the JWT token."
        ),
        responses={
            201: {
                "description": "User created successfully or already exists",
                "model": CreateUserResponse,
            },
            400: {
                "description": "Invalid request",
                "model": ErrorResponse,
            },
            401: {
                "description": "Unauthorized - invalid or missing JWT token",
                "model": ErrorResponse,
            },
            500: {
                "description": "Internal server error",
                "model": ErrorResponse,
            },
        },
    )
    @inject
    async def create_user(
        request: CreateUserRequest,
        response: Response,
        use_case: FromDishka[CreateUserUseCase],
        logger: FromDishka[Logger],
        jwt_payload: dict = Depends(get_jwt_payload),
    ) -> CreateUserResponse | ErrorResponse:
        """Create a new user after Auth0 login.

        The auth0_user_id is automatically extracted from the JWT token.
        If the user already exists, returns the existing user information.

        Args:
            request: User creation request with optional email and user_type.
            jwt_payload: JWT payload containing auth0_user_id (from middleware).
            use_case: Create user use case (injected by Dishka).
            logger: Logger instance (injected by Dishka).

        Returns:
            CreateUserResponse with user data or ErrorResponse on failure.
        """
        try:
            # Extract auth0_user_id from JWT
            auth0_user_id = jwt_payload.get("sub")
            if not auth0_user_id:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return ErrorResponse(
                    name="UnauthorizedError",
                    message="Missing user ID in token",
                )

            # Create input
            input_data = CreateUserUseCaseInput(
                auth0_user_id=auth0_user_id,
                email=request.email,
                user_type=request.user_type,
            )

            # Execute use case
            result = await use_case.execute(input_data)

            if not result.success:
                error = result.error
                if isinstance(error, ValueError):
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return ErrorResponse(
                        name="ValidationError",
                        message=str(error),
                    )
                if isinstance(error, (UnexpectedError, DatabaseError)):
                    logger.error(f"{UNEXPECTED_ERROR_MESSAGE}: {error}")
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    return ErrorResponse(
                        name="InternalServerError",
                        message=UNEXPECTED_ERROR_MESSAGE,
                    )

                # Generic error
                logger.error(f"Failed to create user: {error}")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return ErrorResponse(
                    name="InternalServerError",
                    message=UNEXPECTED_ERROR_MESSAGE,
                )

            output = result.data
            return CreateUserResponse(
                user_id=str(output.user_id),
                auth0_user_id=output.auth0_user_id,
                email=output.email,
                user_type=output.user_type,
                daily_quota_seconds=output.daily_quota_seconds,
                message="User created successfully",
            )

        except Exception as error:
            logger.error(f"Unexpected error in create_user: {error}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(
                name="InternalServerError",
                message=UNEXPECTED_ERROR_MESSAGE,
            )

    return router
