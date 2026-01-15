"""S3 file storage implementation."""

import logging
from pathlib import Path
from typing import Any, BinaryIO
from uuid import uuid4

from botocore.exceptions import ClientError

from app.domain.support.logger.logger import Logger
from app.util.result import Result, failure, success

log = logging.getLogger(__name__)


class S3StorageImpl:
    """S3 file storage implementation."""

    def __init__(
        self,
        *,
        client: Any,
        bucket_name: str,
        region: str,
        endpoint_url: str | None,
        logger: Logger,
    ) -> None:
        """Initialize S3 storage with client."""
        self._client = client
        self._bucket_name = bucket_name
        self._region = region
        self._endpoint_url = endpoint_url
        self._logger = logger

    async def upload_file(
        self,
        *,
        file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> Result[str, Exception]:
        """Upload file to S3 and return URL."""
        try:
            key = self._generate_key(filename)
            self._logger.info(
                f"Uploading file to S3: bucket={self._bucket_name}, key={key}"
            )

            await self._upload_to_s3(file, key, content_type)
            url = self._build_url(key)

            self._logger.info(f"File uploaded successfully: {url}")
            return success(url)
        except Exception as e:
            self._logger.error(f"Failed to upload file: {e}")
            return failure(e)

    def _generate_key(self, filename: str) -> str:
        """Generate unique storage key."""
        ext = Path(filename).suffix
        unique_filename = f"{uuid4()}{ext}"
        return f"audio/{unique_filename}"

    async def _upload_to_s3(self, file: BinaryIO, key: str, content_type: str) -> None:
        """Upload file to S3."""
        try:
            await self._client.upload_fileobj(
                file,
                self._bucket_name,
                key,
                ExtraArgs={"ContentType": content_type},
            )
        except ClientError as err:
            raise Exception(f"S3 upload failed: {err}") from err

    def _build_url(self, key: str) -> str:
        """Build public URL for uploaded file."""
        if self._endpoint_url:
            # MinIO or custom S3-compatible storage
            return f"{self._endpoint_url}/{self._bucket_name}/{key}"
        # AWS S3
        return f"https://{self._bucket_name}.s3.{self._region}.amazonaws.com/{key}"
