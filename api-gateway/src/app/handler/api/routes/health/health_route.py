"""Health check endpoint."""

from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    message: str


def health_route() -> APIRouter:
    """Health check route"""
    router = APIRouter()

    @router.get(
        "/",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
    )
    async def health_check() -> HealthResponse:
        """Health check endpoint"""
        return HealthResponse(
            status="ok",
            message="Service is healthy",
        )

    return router
