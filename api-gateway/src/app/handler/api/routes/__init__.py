"""API routes."""

from fastapi import APIRouter

from app.handler.api.routes.health import health_route
from app.handler.api.routes.meeting import create_meeting_router
from app.handler.api.routes.user import create_user_router


def create_api_router() -> APIRouter:
    """Create API router."""
    router = APIRouter(prefix="/api/v1")
    router.include_router(create_meeting_router())
    router.include_router(create_user_router())
    return router


def create_root_router() -> APIRouter:
    """Create root router."""
    router = APIRouter()
    router.include_router(health_route(), prefix="/health", tags=["health"])
    router.include_router(create_api_router())
    return router


__all__ = ["create_api_router", "create_root_router"]
