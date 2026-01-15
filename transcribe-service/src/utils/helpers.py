"""General helper functions."""

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from src.enums import URLType


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string (e.g., '1h 23m 45s')."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human-readable string (e.g., '1.5 GB')."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def safe_uuid(value: str | UUID) -> UUID:
    """Safely convert string or UUID to UUID."""
    return value if isinstance(value, UUID) else UUID(value)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """Split list into chunks of specified size."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters."""
    for char in '<>:"/\\|?*':
        filename = filename.replace(char, "_")
    filename = filename.strip(". ")
    return filename or "unnamed"


def detect_url_type(url: str) -> tuple[URLType, dict[str, str]]:
    """
    Detect URL type and extract relevant information.

    Args:
        url: The URL to analyze

    Returns:
        Tuple of (URLType, metadata dict)
        - For S3 direct URLs (s3://bucket/key): metadata contains 'bucket' and 'key'
        - For HTTP URLs (including S3 presigned): metadata is empty
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    url = url.strip()

    # Check for S3 direct URL (s3://bucket/key)
    if url.startswith("s3://"):
        parts = url[5:].split("/", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(f"Invalid S3 direct URL format: {url}")

        return URLType.S3_DIRECT, {"bucket": parts[0], "key": parts[1]}

    # All other URLs (HTTP, HTTPS, S3 presigned) are treated as HTTP
    # Validate it's a proper URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {url}") from e

    if not parsed.scheme:
        raise ValueError(f"URL missing scheme: {url}")

    if not parsed.netloc:
        raise ValueError(f"URL missing network location: {url}")

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")

    return URLType.HTTP, {}
