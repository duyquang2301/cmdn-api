"""API response models."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    """
    Standard data response wrapper.
    Use for single resource GET requests.

    Example:
        return DataResponse(data=meeting)
    """

    data: T


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response.
    Use for list/collection GET requests.

    Example:
        return PaginatedResponse(data=meetings, meta=pagination_meta)
    """

    data: list[T]
    meta: PaginationMeta


class CreatedResponse(BaseModel):
    """
    Standard created resource response.
    Use for POST requests (201 Created).

    Example:
        return CreatedResponse(id=str(meeting.id), message="Meeting created")
    """

    id: str
    message: str = "Resource created successfully"


class MessageResponse(BaseModel):
    """
    Standard message-only response.
    Use for operations that don't return data.

    Example:
        return MessageResponse(message="Operation completed")
    """

    message: str


class ErrorResponse(BaseModel):
    """Standard error response format."""

    name: str = Field(..., description="Error name (e.g., 'MeetingNotFoundException')")
    message: str = Field(..., description="Error message")
    details: dict | None = Field(
        None, description="Additional error details (optional)"
    )


# Note: HTTP status codes are set in route decorators, NOT in response body
# Examples:
# - @router.get("/", status_code=status.HTTP_200_OK)
# - @router.post("/", status_code=status.HTTP_201_CREATED)
# - @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
