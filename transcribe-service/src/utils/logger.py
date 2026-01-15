"""Logging setup using loguru."""

import sys

from loguru import logger

from src.config import settings


def setup_logger() -> None:
    """Setup loguru logger with configuration from settings."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level.upper(),
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )
    logger.info(f"Logger initialized: {settings.log_level.upper()}")


setup_logger()
