"""Logging configuration for Korame."""

import logging
from rich.logging import RichHandler
from app.config import get_settings


def setup_logging() -> logging.Logger:
    """
    Set up logging with Rich formatter.

    Returns:
        Root logger
    """
    settings = get_settings()

    # Create logger
    logger = logging.getLogger("korame")

    # Set level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Add Rich handler
    handler = RichHandler(rich_tracebacks=True)
    handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(message)s",
        datefmt="[%X]"
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Get logger instance
logger = setup_logging()

