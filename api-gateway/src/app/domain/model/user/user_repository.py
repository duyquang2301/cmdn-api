"""User repository interface."""

from abc import ABC, abstractmethod

from app.domain.model.user.user import User
from app.util.result import Result


class UserRepository(ABC):
    """Repository interface for User entity."""

    @abstractmethod
    async def find_by_auth0_id(
        self, auth0_user_id: str
    ) -> Result[User | None, Exception]:
        """Find user by Auth0 user ID."""
        pass

    @abstractmethod
    async def save(self, user: User) -> Result[User, Exception]:
        """Save or update user."""
        pass

    @abstractmethod
    async def get_or_create(
        self,
        auth0_user_id: str,
        email: str | None = None,
    ) -> Result[User, Exception]:
        """Get existing user or create new one with default FREE type."""
        pass
