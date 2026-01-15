"""Stream reader implementations for S3 and HTTP."""

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from urllib.parse import urlparse

import boto3
import requests
from botocore.exceptions import ClientError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.exceptions import (
    NetworkRetryExhausted,
    S3ThrottlingError,
    StreamingError,
)

logger = logging.getLogger(__name__)


class StreamReader(ABC):
    """Base interface for streaming audio data."""

    @abstractmethod
    def stream(self, url: str, chunk_size: int = 8192) -> Iterator[bytes]:
        """Stream data from URL in chunks."""
        pass


class S3StreamReader(StreamReader):
    """Stream audio from S3 using boto3."""

    def __init__(self, max_attempts: int = 3, backoff_base: float = 2.0):
        self.s3_client = boto3.client("s3")
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base

    def _parse_s3_url(self, url: str) -> tuple[str, str]:
        """Parse S3 URL to extract bucket and key."""
        try:
            if url.startswith("s3://"):
                parsed = urlparse(url)
                return parsed.netloc, parsed.path.lstrip("/")

            raise StreamingError(f"Invalid S3 URL format: {url}")
        except Exception as e:
            raise StreamingError(f"Failed to parse S3 URL: {e}") from e

    def stream(self, url: str, chunk_size: int = 8192) -> Iterator[bytes]:
        """Stream from S3 with retry logic."""
        bucket, key = self._parse_s3_url(url)

        for attempt in range(self.max_attempts):
            try:
                logger.debug(
                    f"Streaming from s3://{bucket}/{key} (attempt {attempt + 1})"
                )
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                stream = response["Body"]

                while True:
                    chunk = stream.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

                return

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")

                if error_code == "SlowDown" and attempt < self.max_attempts - 1:
                    wait_time = self.backoff_base**attempt
                    logger.warning(f"S3 throttling, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue

                raise S3ThrottlingError(f"S3 error: {error_code}") from e

            except Exception as e:
                if attempt < self.max_attempts - 1:
                    wait_time = self.backoff_base**attempt
                    logger.warning(f"Stream error, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue

                raise NetworkRetryExhausted(
                    f"Failed after {self.max_attempts} attempts"
                ) from e


class HTTPStreamReader(StreamReader):
    """Stream audio from HTTP/HTTPS."""

    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0):
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_attempts,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def stream(self, url: str, chunk_size: int = 8192) -> Iterator[bytes]:
        """Stream from HTTP with retry logic."""
        try:
            logger.debug(f"Streaming from {url}")
            with self.session.get(url, stream=True, timeout=300) as response:
                response.raise_for_status()

                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        yield chunk

        except requests.exceptions.RetryError as e:
            raise NetworkRetryExhausted("HTTP retry exhausted") from e
        except requests.exceptions.RequestException as e:
            raise StreamingError(f"HTTP error: {e}") from e
