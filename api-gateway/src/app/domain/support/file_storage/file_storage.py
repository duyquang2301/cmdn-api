"""File storage interface."""

from typing import BinaryIO, Protocol

from app.util.result import Result


class FileStorage(Protocol):
    """
    File storage interface for domain layer.

    Implementation will be in infrastructure (S3, local, etc.)
    """

    async def upload_file(
        self,
        *,
        file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> Result[str, Exception]:
        """
        Upload file and return URL.

        Returns:
            Result with file URL on success, error on failure
        """
        ...

    async def delete_file(self, file_url: str) -> Result[None, Exception]:
        """Delete file by URL"""
        ...

    async def get_presigned_url(
        self,
        *,
        file_url: str,
        expires_in: int = 3600,
    ) -> Result[str, Exception]:
        """Get presigned URL for temporary access"""
        ...
