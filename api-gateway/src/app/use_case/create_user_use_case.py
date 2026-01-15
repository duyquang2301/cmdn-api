"""Create user use case."""

from dataclasses import dataclass
from uuid import UUID

from app.domain.model.user.user import User
from app.domain.model.user.user_repository import UserRepository
from app.domain.support.logger.logger import Logger
from app.infrastructure.db_client.transaction_manager import TransactionManager
from app.util.enums.user_type import UserType
from app.util.result import Result, failure, success


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserUseCaseInput:
    """Input for create user use case."""

    auth0_user_id: str
    email: str | None = None
    user_type: UserType = UserType.FREE


@dataclass(frozen=True, slots=True)
class CreateUserUseCaseOutput:
    """Output for create user use case."""

    user_id: UUID
    auth0_user_id: str
    email: str | None
    user_type: UserType
    daily_quota_seconds: int | None


class CreateUserUseCase:
    """Create user use case after Auth0 login."""

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        logger: Logger,
    ) -> None:
        self._user_repo = user_repository
        self._transaction_manager = transaction_manager
        self._logger = logger

    async def execute(
        self, input: CreateUserUseCaseInput
    ) -> Result[CreateUserUseCaseOutput, Exception]:
        """Execute create user use case.

        This use case is idempotent - if user already exists, returns existing user.
        If user doesn't exist, creates new user with specified type.

        Args:
            input: Create user input with auth0_user_id, email, and user_type.

        Returns:
            Success with user data if created/found.
            Failure with Exception if database error occurs.
        """
        self._logger.info(
            f"Creating user: auth0_id={input.auth0_user_id}, type={input.user_type}"
        )

        try:
            # Check if user already exists
            existing_result = await self._user_repo.find_by_auth0_id(
                input.auth0_user_id
            )
            if not existing_result.success:
                return failure(existing_result.error)

            if existing_result.data is not None:
                # User already exists, return existing user
                user = existing_result.data
                self._logger.info(f"User already exists: {user.id}")

                return success(
                    CreateUserUseCaseOutput(
                        user_id=user.id,
                        auth0_user_id=user.auth0_user_id,
                        email=user.email,
                        user_type=user.user_type,
                        daily_quota_seconds=user.get_daily_quota_seconds(),
                    )
                )

            # Create new user
            user = User.create(
                auth0_user_id=input.auth0_user_id,
                email=input.email,
                user_type=input.user_type,
            )

            # Save user
            save_result = await self._user_repo.save(user)
            if not save_result.success:
                await self._transaction_manager.rollback()
                return failure(save_result.error)

            await self._transaction_manager.commit()

            self._logger.info(f"User created successfully: {user.id}")

            return success(
                CreateUserUseCaseOutput(
                    user_id=user.id,
                    auth0_user_id=user.auth0_user_id,
                    email=user.email,
                    user_type=user.user_type,
                    daily_quota_seconds=user.get_daily_quota_seconds(),
                )
            )

        except Exception as e:
            self._logger.error(f"Failed to create user: {e}")
            await self._transaction_manager.rollback()
            return failure(e)
