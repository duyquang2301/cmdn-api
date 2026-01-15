"""SQLAlchemy mappings."""

from app.infrastructure.persistence.sqlalchemy.mappings.meeting_mapping import (
    map_meeting,
)
from app.infrastructure.persistence.sqlalchemy.mappings.task_mapping import map_task
from app.infrastructure.persistence.sqlalchemy.mappings.user_mapping import map_user


def map_all() -> None:
    """Map all entities to database tables"""
    map_user()
    map_meeting()
    map_task()


__all__ = ["map_all", "map_meeting", "map_task", "map_user"]
