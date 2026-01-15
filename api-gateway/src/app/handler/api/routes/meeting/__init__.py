"""Meeting routes."""

from fastapi import APIRouter, Depends

from app.handler.api.middleware.auth_middleware import verify_jwt_token
from app.handler.api.routes.meeting.create_meeting_route import create_meeting_route
from app.handler.api.routes.meeting.delete_meeting_route import delete_meeting_route
from app.handler.api.routes.meeting.find_many_task_route import find_many_task_route
from app.handler.api.routes.meeting.find_meeting_list_route import (
    find_meeting_list_route,
)
from app.handler.api.routes.meeting.find_meeting_route import find_meeting_route
from app.handler.api.routes.meeting.find_meeting_status_route import (
    find_meeting_status_route,
)
from app.handler.api.routes.meeting.update_meeting_route import update_meeting_route
from app.handler.api.routes.meeting.upload_audio_route import upload_audio_route


def create_meeting_router() -> APIRouter:
    """Create meeting router with JWT authentication."""
    router = APIRouter(
        prefix="/meetings",
        tags=["meetings"],
        dependencies=[
            Depends(verify_jwt_token),
        ],
    )

    # Include all meeting routes
    router.include_router(create_meeting_route())
    router.include_router(find_meeting_route())
    router.include_router(find_meeting_list_route())
    router.include_router(update_meeting_route())
    router.include_router(delete_meeting_route())
    router.include_router(find_meeting_status_route())
    router.include_router(find_many_task_route())
    router.include_router(upload_audio_route())

    return router


__all__ = ["create_meeting_router"]
