"""Dependency injection container.

Provides DI configuration using Dishka with settings management.

Usage:
    >>> from app.di_container import create_container, settings
    >>> container = create_container()
    >>> print(settings.database.url)
"""

from app.di_container.container import create_container, get_providers
from app.di_container.settings import get_settings, settings

__all__ = [
    "create_container",
    "get_providers",
    "get_settings",
    "settings",
]
