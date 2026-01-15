"""Celery tasks for summarize service."""

from .celery_app import app
from .summarize import (
    extract_key_notes_task,
    generate_tasks_task,
    summarize_transcript_task,
)
from .worker import start_worker

__all__ = [
    "app",
    "extract_key_notes_task",
    "generate_tasks_task",
    "start_worker",
    "summarize_transcript_task",
]
