"""User type enum with quota mappings."""

from enum import StrEnum


class UserType(StrEnum):
    """User subscription types with associated quotas."""

    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

    def get_daily_quota_seconds(self) -> int | None:
        """Get daily quota in seconds (None for unlimited)."""
        quotas = {
            UserType.FREE: 7200,  # 2 hours
            UserType.PREMIUM: 18000,  # 5 hours
            UserType.ENTERPRISE: None,  # Unlimited
        }
        return quotas[self]
