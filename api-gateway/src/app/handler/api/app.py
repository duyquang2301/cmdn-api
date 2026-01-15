"""FastAPI application."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.handler.api.routes import create_root_router
from app.infrastructure.persistence.sqlalchemy.mappings import map_all
from app.util.auth_exceptions import (
    InvalidTokenError,
    TokenVerificationInternalError,
    UnauthorizedError,
)
from app.util.exceptions import AccessDeniedError, UnexpectedError

log = logging.getLogger(__name__)


def create_web_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Audio Transcription API",
        description="API Gateway for audio transcription and meeting management",
        version="1.0.0",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )

    app.include_router(create_root_router())

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> ORJSONResponse:
        """Global exception handler."""
        log.error(
            "Unhandled exception caught by FastAPI",
            exc_info=True,
            extra={"path": request.url.path, "error": str(exc)},
        )

        # Handle authentication errors
        if isinstance(exc, (UnauthorizedError, InvalidTokenError)):
            log.info(f"Authentication failed: {exc.message}")
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "name": "UnauthorizedError",
                    "message": "Authentication failed",
                },
            )

        if isinstance(exc, TokenVerificationInternalError):
            log.error(f"Token verification internal error: {exc.message}")
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "name": exc.name,
                    "message": exc.message,
                },
            )

        # Check for specific error types
        if isinstance(exc, AccessDeniedError):
            return ORJSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "name": exc.name,
                    "message": exc.message,
                },
            )

        # Default: return UnexpectedError
        unexpected_error = UnexpectedError()
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "name": unexpected_error.name,
                "message": unexpected_error.message,
            },
        )

    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan."""
    map_all()
    yield
    if hasattr(app.state, "dishka_container"):
        await app.state.dishka_container.close()
