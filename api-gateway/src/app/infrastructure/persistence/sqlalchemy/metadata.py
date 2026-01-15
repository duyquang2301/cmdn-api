"""SQLAlchemy metadata."""

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

# Create metadata for all tables
metadata = MetaData()

# Create mapper registry for imperative mapping
mapper_registry = registry(metadata=metadata)
