"""Chunk storage operations using Redis."""

import json
from uuid import UUID

from src.exceptions import StorageError
from src.models import ChunkResult, Segment

from .redis import get_redis


def _chunk_key(meeting_id: UUID, chunk_id: int) -> str:
    """Generate Redis key for chunk."""
    return f"chunks:{meeting_id}:{chunk_id}"


def _chunk_pattern(meeting_id: UUID) -> str:
    """Generate Redis pattern for all chunks of meeting."""
    return f"chunks:{meeting_id}:*"


def _serialize_chunk(chunk: ChunkResult) -> str:
    """Serialize chunk to JSON."""
    data = {
        "chunk_id": chunk.chunk_id,
        "status": chunk.status,
        "error": chunk.error,
        "segments": [
            {"start": s.start, "end": s.end, "text": s.text} for s in chunk.segments
        ],
    }
    return json.dumps(data)


def _deserialize_chunk(data: str) -> ChunkResult:
    """Deserialize chunk from JSON."""
    parsed = json.loads(data)
    return ChunkResult(
        chunk_id=parsed["chunk_id"],
        status=parsed["status"],
        error=parsed.get("error"),
        segments=[
            Segment(start=s["start"], end=s["end"], text=s["text"])
            for s in parsed["segments"]
        ],
    )


def save_chunk(meeting_id: UUID, chunk: ChunkResult) -> None:
    """Save chunk to Redis with 1-hour expiration."""
    try:
        redis = get_redis()
        key = _chunk_key(meeting_id, chunk.chunk_id)
        redis.set(key, _serialize_chunk(chunk))
        redis.expire(key, 3600)
    except Exception as e:
        raise StorageError(f"Failed to save chunk {chunk.chunk_id}: {e}") from e


def get_chunk(meeting_id: UUID, chunk_id: int) -> ChunkResult | None:
    """Get chunk from Redis."""
    try:
        redis = get_redis()
        key = _chunk_key(meeting_id, chunk_id)
        data = redis.get(key)
        return _deserialize_chunk(data) if data else None
    except json.JSONDecodeError as e:
        raise StorageError(f"Failed to parse chunk {chunk_id}: {e}") from e
    except Exception as e:
        raise StorageError(f"Failed to get chunk {chunk_id}: {e}") from e


def get_all_chunks(meeting_id: UUID) -> list[ChunkResult]:
    """Get all chunks for meeting, sorted by chunk_id."""
    try:
        redis = get_redis()
        pattern = _chunk_pattern(meeting_id)
        keys = redis.keys(pattern)

        chunks = []
        for key in keys:
            data = redis.get(key)
            if data:
                chunks.append(_deserialize_chunk(data))

        return sorted(chunks, key=lambda c: c.chunk_id)
    except json.JSONDecodeError as e:
        raise StorageError(f"Failed to parse chunks: {e}") from e
    except Exception as e:
        raise StorageError(f"Failed to get chunks: {e}") from e


def count_chunks(meeting_id: UUID) -> int:
    """Count chunks for meeting."""
    try:
        redis = get_redis()
        pattern = _chunk_pattern(meeting_id)
        return len(redis.keys(pattern))
    except Exception as e:
        raise StorageError(f"Failed to count chunks: {e}") from e


def delete_chunks(meeting_id: UUID) -> None:
    """Delete all chunks for meeting."""
    try:
        redis = get_redis()
        pattern = _chunk_pattern(meeting_id)
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
    except Exception as e:
        raise StorageError(f"Failed to delete chunks: {e}") from e
