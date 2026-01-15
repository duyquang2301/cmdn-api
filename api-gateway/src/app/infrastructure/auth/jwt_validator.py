import json
import logging
from typing import Any

import jwt
from jwt.algorithms import RSAAlgorithm

from app.infrastructure.auth.jwks_cache import load_jwks
from app.infrastructure.auth.type import JwksCache
from app.util.auth_exceptions import (
    InvalidTokenError,
    TokenVerificationInternalError,
    UnauthorizedError,
)

log = logging.getLogger(__name__)


def extract_kid(*, token: str) -> str:
    """
    Extract `kid` from JWT header without verifying signature.
    """
    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError:
        raise InvalidTokenError("Invalid token header")

    kid = header.get("kid")
    if not kid:
        raise InvalidTokenError("Token missing 'kid'")

    return kid


def find_signing_key(
    *,
    kid: str,
    jwks: dict[str, Any],
):
    """
    Find RSA public key in JWKS by kid.
    """
    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))

    raise KeyError("Signing key not found")


class JWTValidator:
    """JWT token validator using Auth0 JWKS."""

    def __init__(
        self,
        *,
        audience: str,
        issuer_base_url: str,
    ) -> None:
        """Initialize JWT validator."""
        self.audience = audience
        self.issuer = issuer_base_url.rstrip("/") + "/"
        self.jwks_url = f"{self.issuer}.well-known/jwks.json"

        # In-memory JWKS cache
        self._jwks_cache: JwksCache = {
            "jwks": None,
            "expires_at": 0.0,
        }

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify JWT access token."""
        if not token:
            raise UnauthorizedError("Missing token")

        try:
            kid = extract_kid(token=token)

            jwks = await load_jwks(
                jwks_url=self.jwks_url,
                jwks_cache=self._jwks_cache,
            )

            try:
                signing_key = find_signing_key(kid=kid, jwks=jwks)
            except KeyError:
                log.info("Signing key not found, refreshing JWKS")
                jwks = await load_jwks(
                    jwks_url=self.jwks_url,
                    jwks_cache=self._jwks_cache,
                    force_refresh=True,
                )
                signing_key = find_signing_key(kid=kid, jwks=jwks)

            return jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )

        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token expired")

        except jwt.InvalidAudienceError:
            raise UnauthorizedError("Invalid token audience")

        except jwt.InvalidIssuerError:
            raise UnauthorizedError("Invalid token issuer")

        except (InvalidTokenError, KeyError):
            raise InvalidTokenError("Invalid token")

        except Exception as exc:
            log.exception("JWT verification failed")
            raise TokenVerificationInternalError("Token verification failed") from exc
