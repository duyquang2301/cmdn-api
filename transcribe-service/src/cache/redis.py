"""Redis client management."""

import redis
from redis.exceptions import ConnectionError as RedisConnectionError

from src.config import settings


class _RedisClientHolder:
    """Holder for Redis client singleton."""

    _instance: redis.Redis | None = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get or create Redis client."""
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.redis_url,
                decode_responses=settings.redis_decode_responses,
            )
        return cls._instance


def get_redis() -> redis.Redis:
    """Get Redis client (singleton)."""
    return _RedisClientHolder.get_client()


def ping_redis() -> bool:
    """Check Redis connection health."""
    try:
        return get_redis().ping()
    except (RedisConnectionError, Exception):
        return False
