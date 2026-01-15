"""Database layer for transcribe service.

This module provides database connection management, ORM models,
and repository functions for interacting with the meetings table.
"""

from .connection import Base, SessionLocal, engine, get_session, init_db
from .orm_models import MeetingModel
from .repository import get_meeting, list_meetings, save_meeting, to_domain, to_model

__all__ = [
    # Connection
    "Base",
    # ORM Models
    "MeetingModel",
    "SessionLocal",
    "engine",
    # Repository functions
    "get_meeting",
    "get_session",
    "init_db",
    "list_meetings",
    "save_meeting",
    "to_domain",
    "to_model",
]
