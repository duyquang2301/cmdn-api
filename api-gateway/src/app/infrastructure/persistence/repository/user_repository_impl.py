"""User repository implementation."""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.user.user import User
from app.domain.model.user.user_repository import UserRepository
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_auth0_id(
        self, auth0_user_id: str
    ) -> Result[User | None, Exception]:
        """Find user by Auth0 user ID."""
        try:
            result = await self._session.execute(
                select(User).where(User.auth0_user_id == auth0_user_id)
            )
            user = result.scalar_one_or_none()
            return success(user)
        except SQLAlchemyError as e:
            log.error(f"Failed to find user by auth0_user_id: {e}")
            return failure(e)

    async def save(self, user: User) -> Result[User, Exception]:
        """Save or update user."""
        try:
            # Update the updated_at timestamp
            user.updated_at = datetime.now(UTC)

            # Merge will handle both insert and update
            merged_user = await self._session.merge(user)
            await self._session.flush()
            return success(merged_user)
        except SQLAlchemyError as e:
            log.error(f"Failed to save user: {e}")
            return failure(e)

    async def get_or_create(
        self,
        auth0_user_id: str,
        email: str | None = None,
    ) -> Result[User, Exception]:
        """Get existing user or create new one with default FREE type."""
        try:
            # First, try to find existing user
            find_result = await self.find_by_auth0_id(auth0_user_id)

            if not find_result.success:
                return failure(find_result.error)

            if find_result.data is not None:
                # User exists, return it
                return success(find_result.data)

            # User doesn't exist, create new one
            new_user = User.create(
                auth0_user_id=auth0_user_id,
                email=email,
            )

            # Save the new user
            save_result = await self.save(new_user)

            if not save_result.success:
                return failure(save_result.error)

            log.info(f"Created new user: {auth0_user_id} with type FREE")
            return success(save_result.data)

        except Exception as e:
            log.error(f"Failed to get or create user: {e}")
            return failure(e)
