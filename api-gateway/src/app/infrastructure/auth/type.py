from typing import Any, TypedDict


class JwksCache(TypedDict):
    jwks: dict[str, Any] | None
    expires_at: float
