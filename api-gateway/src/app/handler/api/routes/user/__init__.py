"""User routes."""

from fastapi import APIRouter, Depends

from app.handler.api.middleware.auth_middleware import verify_jwt_token
from app.handler.api.routes.user.create_user_route import create_user_route


def create_user_router() -> APIRouter:
    """Create user router with JWT authentication."""
    router = APIRouter(
        prefix="/users",
        tags=["users"],
        dependencies=[
            Depends(verify_jwt_token),
        ],
    )

    # Include user routes
    router.include_router(create_user_route())

    return router


__all__ = ["create_user_router"]
