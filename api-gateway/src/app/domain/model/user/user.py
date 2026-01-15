"""User entity."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.model.base import Entity
from app.util.enums.user_type import UserType


class User(Entity):
    """User domain entity."""

    def __init__(
        self,
        *,
        id: UUID,
        auth0_user_id: str,
        email: str | None,
        user_type: UserType,
        used_duration_seconds: float,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id=id)
        self.auth0_user_id = auth0_user_id
        self.email = email
        self.user_type = user_type
        self.used_duration_seconds = used_duration_seconds
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(
        auth0_user_id: str,
        email: str | None = None,
        user_type: UserType = UserType.FREE,
    ) -> "User":
        """Create a new user with defaults."""
        if not auth0_user_id or not auth0_user_id.strip():
            raise ValueError("auth0_user_id cannot be empty")

        now = datetime.now(UTC)
        return User(
            id=uuid4(),
            auth0_user_id=auth0_user_id.strip(),
            email=email.strip() if email else None,
            user_type=user_type,
            used_duration_seconds=0,
            created_at=now,
            updated_at=now,
        )

    def get_daily_quota_seconds(self) -> int | None:
        """Get daily quota in seconds (None for unlimited)."""
        return self.user_type.get_daily_quota_seconds()

    def increment_usage(self, duration_seconds: float) -> None:
        """Increment used duration."""
        if duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        self.used_duration_seconds += duration_seconds

    def reset_usage(self) -> None:
        """Reset used duration to 0."""
        self.used_duration_seconds = 0

    def __repr__(self) -> str:
        return f"User(id={self.id}, auth0_user_id={self.auth0_user_id!r}, user_type={self.user_type})"
