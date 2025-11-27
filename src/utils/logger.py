"""
Logging configuration and setup.

This module configures the application logger using loguru.
"""

import sys
from pathlib import Path
from loguru import logger

from src.config import settings


def setup_logger() -> None:
    """Configure the application logger with appropriate handlers."""
    # Remove default handler
    logger.remove()

    # Add console handler with formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    # Add file handler if log file path is specified
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            settings.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
        )

    logger.info("Logger configured successfully")

