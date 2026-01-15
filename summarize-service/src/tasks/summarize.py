"""Celery tasks for summarization."""

import logging
from uuid import UUID

from src.config import settings
from src.database.repository import get_meeting
from src.database.session import get_session
from src.providers.llm import LLMClient
from src.services.meeting import (
    complete_summarization,
    fail_summarization,
    start_summarization,
    update_key_notes,
)
from src.services.summarization import (
    extract_key_notes,
    generate_tasks,
    summarize_transcript,
)

from .celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="audio.summarize.generate", bind=True)
def summarize_transcript_task(self, meeting_id: str):
    """Generate summary from transcript and trigger key notes + tasks generation."""
    meeting_uuid = UUID(meeting_id)
    logger.info(f"Starting summarization task for meeting {meeting_uuid}")

    try:
        with get_session() as session:
            # Start summarization
            start_summarization(session, meeting_uuid)

            # Get meeting
            meeting = get_meeting(session, meeting_uuid)
            transcript = meeting.transcribe_text

            if not transcript:
                raise ValueError("Meeting has no transcript")

            # Initialize AI client
            llm_client = LLMClient()

            # Generate summary
            summary = summarize_transcript(
                transcript, settings.summary_chunk_size, llm_client
            )

            # Save summary
            complete_summarization(session, meeting_uuid, summary)

            logger.info(f"Summary generated: {len(summary)} chars")

        # Trigger parallel tasks for key notes and tasks generation
        extract_key_notes_task.delay(meeting_id)
        generate_tasks_task.delay(meeting_id)

        return {
            "meeting_id": str(meeting_uuid),
            "summary_length": len(summary),
            "status": "summarized",
        }

    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        with get_session() as session:
            fail_summarization(session, meeting_uuid, str(e))
        raise


@app.task(name="extract_key_notes_task", bind=True)
def extract_key_notes_task(self, meeting_id: str):
    """Extract key notes from summary."""
    meeting_uuid = UUID(meeting_id)
    logger.info(f"Extracting key notes for meeting {meeting_uuid}")

    try:
        with get_session() as session:
            # Get meeting
            meeting = get_meeting(session, meeting_uuid)
            summary = meeting.summary_text

            if not summary:
                raise ValueError("Meeting has no summary")

            # Initialize AI client
            llm_client = LLMClient()

            # Extract key notes
            key_notes = extract_key_notes(summary, llm_client)

            # Save key notes
            update_key_notes(session, meeting_uuid, key_notes)

            logger.info(f"Extracted {len(key_notes)} key notes")

            return {
                "meeting_id": str(meeting_uuid),
                "key_notes_count": len(key_notes),
            }

    except Exception as e:
        logger.error(f"Key notes extraction failed: {e}", exc_info=True)
        raise


@app.task(name="generate_tasks_task", bind=True)
def generate_tasks_task(self, meeting_id: str):
    """Generate tasks from summary."""
    meeting_uuid = UUID(meeting_id)
    logger.info(f"Generating tasks for meeting {meeting_uuid}")

    try:
        with get_session() as session:
            # Get meeting
            meeting = get_meeting(session, meeting_uuid)
            summary = meeting.summary_text

            if not summary:
                raise ValueError("Meeting has no summary")

            # Initialize AI client
            llm_client = LLMClient()

            # Generate tasks
            tasks_count = generate_tasks(session, meeting_uuid, summary, llm_client)

            logger.info(f"Generated {tasks_count} tasks")

            return {
                "meeting_id": str(meeting_uuid),
                "tasks_count": tasks_count,
            }

    except Exception as e:
        logger.error(f"Task generation failed: {e}", exc_info=True)
        raise
