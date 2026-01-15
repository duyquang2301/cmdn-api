"""AI Summarization service."""

import json
import logging
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.database.repository import save_tasks
from src.models import Task
from src.providers.llm import LLMClient
from src.utils.prompts import (
    CHUNK_SUMMARY_PROMPT,
    GENERATE_TASKS_PROMPT,
    KEY_NOTES_PROMPT,
    MERGE_SUMMARIES_PROMPT,
)
from src.utils.text import TextChunker

logger = logging.getLogger(__name__)


def summarize_transcript(
    transcript: str, max_chunk_size: int, llm_client: LLMClient
) -> str:
    """Summarize transcript with automatic chunking if needed."""
    chunker = TextChunker()

    # Check if chunking needed
    if not chunker.should_chunk(transcript, max_chunk_size):
        logger.info(f"Direct summarization ({len(transcript)} chars)")
        prompt = CHUNK_SUMMARY_PROMPT.format(text=transcript)
        return llm_client.generate(prompt)

    # Chunk and summarize
    chunks = chunker.chunk(transcript, max_chunk_size)
    logger.info(f"Chunked summarization: {len(chunks)} chunks")

    summaries = []
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Processing chunk {i}/{len(chunks)}")
        prompt = CHUNK_SUMMARY_PROMPT.format(text=chunk)
        summary = llm_client.generate(prompt)
        summaries.append(summary)

    # Merge summaries
    logger.info(f"Merging {len(summaries)} summaries")
    merged_text = "\n\n".join(summaries)
    prompt = MERGE_SUMMARIES_PROMPT.format(text=merged_text)
    return llm_client.generate(prompt)


def extract_key_notes(summary: str, llm_client: LLMClient) -> list[dict]:
    """Extract key notes from summary."""
    logger.info("Extracting key notes")
    prompt = KEY_NOTES_PROMPT.format(text=summary)
    response = llm_client.generate(prompt)

    try:
        # Parse JSON response
        key_notes = json.loads(response)
        logger.info(f"Extracted {len(key_notes)} key notes")
        return key_notes
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse key notes JSON: {e}")
        return []


def generate_tasks(
    session: Session, meeting_id: UUID, summary: str, llm_client: LLMClient
) -> int:
    """Generate tasks from summary and save to database."""
    try:
        logger.info("Generating tasks from summary")
        prompt = GENERATE_TASKS_PROMPT.format(text=summary)
        response = llm_client.generate(prompt)

        # Parse JSON response
        tasks_data = json.loads(response)
        if not tasks_data:
            logger.info("No tasks generated")
            return 0

        # Create Task objects
        tasks = [
            Task(
                id=uuid4(),
                meeting_id=meeting_id,
                title=task_data.get("title", ""),
                description=task_data.get("description"),
                status="pending",
                assignee=task_data.get("assignee"),
                due_date=task_data.get("due_date"),
                priority=task_data.get("priority", "medium"),
            )
            for task_data in tasks_data
        ]

        # Save to database
        count = save_tasks(session, tasks)
        session.commit()
        logger.info(f"Created {count} tasks")
        return count

    except Exception as e:
        logger.warning(f"Failed to generate tasks: {e}")
        return 0
