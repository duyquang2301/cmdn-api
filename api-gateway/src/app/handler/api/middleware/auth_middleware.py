"""Authentication middleware for FastAPI."""

import logging

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.auth.jwt_validator import JWTValidator
from app.util.auth_exceptions import (
    InvalidTokenError,
    TokenVerificationInternalError,
    UnauthorizedError,
)

log = logging.getLogger(__name__)

# Security scheme for OpenAPI
security = HTTPBearer(auto_error=False)


@inject
async def verify_jwt_token(
    jwt_validator: FromDishka[JWTValidator],
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> dict:
    """Verify JWT token from Authorization header."""
    # Check if credentials exist
    if not credentials:
        log.info("Missing Authorization header")
        raise UnauthorizedError("Missing authorization token")

    token = credentials.credentials

    try:
        # Verify token
        payload = await jwt_validator.verify_token(token)
        log.debug(f"Token verified successfully for subject: {payload.get('sub')}")
        return payload

    except (UnauthorizedError, InvalidTokenError, TokenVerificationInternalError):
        # Re-raise auth exceptions - will be caught by global handler
        raise

    except Exception as e:
        log.error(f"Unexpected error in auth middleware: {e!s}")
        raise TokenVerificationInternalError("Authentication failed")


@inject
async def get_jwt_payload(
    jwt_validator: FromDishka[JWTValidator],
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> dict:
    """Get JWT payload from Authorization header.

    Extracts and validates JWT token, returning the payload with:
    - sub: Auth0 user ID (auth0_user_id)
    - email: User email (optional)
    - Other JWT claims

    Raises:
        UnauthorizedError: If token is missing or invalid
    """
    
    # Check if credentials exist
    if not credentials:
        log.info("Missing Authorization header")
        raise UnauthorizedError("Missing authorization token")

    token = credentials.credentials

    try:
        # Verify token
        payload = await jwt_validator.verify_token(token)
        log.debug(f"Token verified successfully for subject: {payload.get('sub')}")
        return payload

    except (UnauthorizedError, InvalidTokenError, TokenVerificationInternalError):
        # Re-raise auth exceptions - will be caught by global handler
        raise

    except Exception as e:
        log.error(f"Unexpected error in auth middleware: {e!s}")
        raise TokenVerificationInternalError("Authentication failed")
