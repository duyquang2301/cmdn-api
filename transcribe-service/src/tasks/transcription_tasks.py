"""Celery tasks for audio transcription."""

from pathlib import Path
from uuid import UUID

from loguru import logger

from src.cache.chunks import count_chunks, save_chunk
from src.config import settings
from src.database.connection import get_session
from src.exceptions import TranscribeError
from src.models import ChunkResult
from src.providers.factory import create_provider
from src.services.meeting import (
    finalize_transcription,
    mark_meeting_failed,
    start_transcription,
)
from src.services.transcription import (
    adjust_segment_timestamps,
    transcribe_audio_file,
)

from .celery_app import app


@app.task(name="audio.transcribe.start", bind=True, max_retries=3)
def transcribe_audio_task(self, meeting_id: str, audio_url: str):
    """Start transcription: download audio, split into chunks, dispatch processing tasks."""
    try:
        logger.info(f"Starting transcription for meeting {meeting_id}")
        meeting_uuid = UUID(meeting_id)
        upload_dir = Path(settings.upload_dir)

        with get_session() as session:
            _meeting, total_chunks = start_transcription(
                session=session,
                meeting_id=meeting_uuid,
                audio_url=audio_url,
                upload_dir=upload_dir,
                chunk_duration_ms=settings.chunk_duration_ms,
            )

        logger.info(f"Created {total_chunks} chunks for meeting {meeting_id}")

        for chunk_id in range(total_chunks):
            offset_seconds = (chunk_id * settings.chunk_duration_ms) / 1000.0
            chunk_path = str(upload_dir / meeting_id / f"chunk_{chunk_id}.mp3")

            process_chunk_task.apply_async(
                args=(meeting_id, chunk_id, chunk_path, total_chunks, offset_seconds),
                task_id=f"chunk_{meeting_id}_{chunk_id}",
            )
            logger.debug(f"Dispatched chunk {chunk_id} for meeting {meeting_id}")

        return {
            "meeting_id": meeting_id,
            "total_chunks": total_chunks,
            "status": "chunks_dispatched",
        }
    except TranscribeError as e:
        logger.error(f"Transcription failed for meeting {meeting_id}: {e}")
        try:
            with get_session() as session:
                mark_meeting_failed(
                    session=session, meeting_id=UUID(meeting_id), error_message=str(e)
                )
        except Exception as mark_error:
            logger.error(f"Failed to mark meeting as failed: {mark_error}")
        raise self.retry(exc=e, countdown=60) from e
    except Exception as e:
        logger.exception(f"Unexpected error for meeting {meeting_id}: {e}")
        try:
            with get_session() as session:
                mark_meeting_failed(
                    session=session,
                    meeting_id=UUID(meeting_id),
                    error_message=f"Unexpected error: {e}",
                )
        except Exception as mark_error:
            logger.error(f"Failed to mark meeting as failed: {mark_error}")
        raise


@app.task(name="audio.transcribe.chunk", bind=True, max_retries=3)
def process_chunk_task(
    self,
    meeting_id: str,
    chunk_id: int,
    chunk_path: str,
    total_chunks: int,
    offset_seconds: float,
):
    """Process single audio chunk: transcribe, adjust timestamps, save to cache."""
    try:
        logger.info(
            f"Processing chunk {chunk_id}/{total_chunks} for meeting {meeting_id}"
        )
        meeting_uuid = UUID(meeting_id)
        chunk_path_obj = Path(chunk_path)

        provider = create_provider()
        segments = transcribe_audio_file(provider=provider, audio_path=chunk_path_obj)
        logger.info(f"Transcribed chunk {chunk_id}: {len(segments)} segments")

        adjusted_segments = adjust_segment_timestamps(
            segments=segments, offset_seconds=offset_seconds
        )

        chunk_result = ChunkResult(
            chunk_id=chunk_id, segments=adjusted_segments, status="success", error=None
        )
        save_chunk(meeting_uuid, chunk_result)
        logger.info(f"Saved chunk {chunk_id} to cache")

        completed_chunks = count_chunks(meeting_uuid)
        logger.info(
            f"Meeting {meeting_id}: {completed_chunks}/{total_chunks} chunks completed"
        )

        if completed_chunks == total_chunks:
            logger.info(
                f"All chunks complete, dispatching merge for meeting {meeting_id}"
            )
            merge_chunks_task.apply_async(
                args=(meeting_id,), task_id=f"merge_{meeting_id}"
            )

        return {
            "meeting_id": meeting_id,
            "chunk_id": chunk_id,
            "segments": len(adjusted_segments),
            "completed_chunks": completed_chunks,
            "total_chunks": total_chunks,
        }
    except TranscribeError as e:
        logger.error(
            f"Failed to process chunk {chunk_id} for meeting {meeting_id}: {e}"
        )
        try:
            chunk_result = ChunkResult(
                chunk_id=chunk_id, segments=[], status="failed", error=str(e)
            )
            save_chunk(UUID(meeting_id), chunk_result)
            logger.info(f"Saved failed chunk {chunk_id} to cache")
        except Exception as save_error:
            logger.error(f"Failed to save error chunk: {save_error}")
        raise self.retry(exc=e, countdown=30) from e
    except Exception as e:
        logger.exception(
            f"Unexpected error processing chunk {chunk_id} for meeting {meeting_id}: {e}"
        )
        try:
            chunk_result = ChunkResult(
                chunk_id=chunk_id,
                segments=[],
                status="failed",
                error=f"Unexpected error: {e}",
            )
            save_chunk(UUID(meeting_id), chunk_result)
        except Exception as save_error:
            logger.error(f"Failed to save error chunk: {save_error}")
        raise


@app.task(name="audio.transcribe.merge", bind=True, max_retries=3)
def merge_chunks_task(self, meeting_id: str):
    """Merge all chunks, finalize transcription, trigger summarization."""
    try:
        logger.info(f"Merging chunks for meeting {meeting_id}")
        meeting_uuid = UUID(meeting_id)
        upload_dir = Path(settings.upload_dir)

        with get_session() as session:
            meeting = finalize_transcription(
                session=session, meeting_id=meeting_uuid, upload_dir=upload_dir
            )

        if meeting.transcript:
            logger.info(
                f"Successfully merged chunks: {len(meeting.transcript)} characters"
            )

            try:
                app.send_task(
                    "audio.summarize.generate",
                    args=(meeting_id,),
                    queue="audio.summarize",
                )
                logger.info(f"Dispatched summarization for meeting {meeting_id}")
            except Exception as e:
                logger.warning(f"Failed to dispatch summarization: {e}")

            return {
                "meeting_id": meeting_id,
                "transcript_length": len(meeting.transcript),
                "status": "completed",
            }
        logger.error(f"No transcript generated for meeting {meeting_id}")
        return {
            "meeting_id": meeting_id,
            "status": "failed",
            "error": "No transcript generated",
        }
    except TranscribeError as e:
        logger.error(f"Failed to merge chunks for meeting {meeting_id}: {e}")
        try:
            with get_session() as session:
                mark_meeting_failed(
                    session=session, meeting_id=UUID(meeting_id), error_message=str(e)
                )
        except Exception as mark_error:
            logger.error(f"Failed to mark meeting as failed: {mark_error}")
        raise self.retry(exc=e, countdown=60) from e
    except Exception as e:
        logger.exception(
            f"Unexpected error merging chunks for meeting {meeting_id}: {e}"
        )
        try:
            with get_session() as session:
                mark_meeting_failed(
                    session=session,
                    meeting_id=UUID(meeting_id),
                    error_message=f"Unexpected error: {e}",
                )
        except Exception as mark_error:
            logger.error(f"Failed to mark meeting as failed: {mark_error}")
        raise
