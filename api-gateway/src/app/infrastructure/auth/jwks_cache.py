import logging
import time
from typing import Any

import httpx

from app.di_container.settings import settings
from app.infrastructure.auth.type import JwksCache

log = logging.getLogger(__name__)

JWKS_TTL_SECONDS = settings.auth0.jwks_cache_ttl


async def fetch_jwks(*, jwks_url: str) -> dict[str, Any]:
    """
    Fetch JWKS from Auth0.

    Args:
        jwks_url: Auth0 JWKS endpoint.

    Returns:
        JWKS payload.
    """
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        return response.json()


async def load_jwks(
    *,
    jwks_url: str,
    jwks_cache: JwksCache,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """
    Load JWKS from cache or fetch from Auth0.

    Uses in-memory cache with TTL.
    """
    now = time.time()

    if not force_refresh and jwks_cache["jwks"] and now < jwks_cache["expires_at"]:
        return jwks_cache["jwks"]

    jwks = await fetch_jwks(jwks_url=jwks_url)
    jwks_cache["jwks"] = jwks
    jwks_cache["expires_at"] = now + JWKS_TTL_SECONDS

    log.info("JWKS cache refreshed")
    return jwks
