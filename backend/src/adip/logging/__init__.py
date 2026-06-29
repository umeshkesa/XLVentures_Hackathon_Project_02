"""Structured logging package."""

import structlog


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to *name*.

    Usage::

        from adip.logging import get_logger

        logger = get_logger(__name__)
        logger.info("event", key="value")
    """
    return structlog.get_logger(name)
