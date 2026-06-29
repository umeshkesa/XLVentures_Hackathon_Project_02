"""Structured logging configuration."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog

from adip.config.settings import LoggingConfig
from adip.core.constants import LogFormat


def _add_module_info(logger: logging.Logger, method_name: str, event_dict: dict) -> dict:
    """Inject the logger's fully-qualified module name into the event dict."""
    event_dict["module"] = logger.name
    return event_dict


def configure_logging(config: LoggingConfig) -> None:
    """Configure structured logging for the whole application.

    Sets up *structlog* on top of the standard-library ``logging`` subsystem so that
    third-party libraries are also captured.  Output is sent to *stdout* and,
    optionally, to a ``RotatingFileHandler``.
    """
    level = getattr(logging, config.level.value, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    handlers: list[logging.Handler] = [console]

    if config.file_path:
        path = Path(config.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                filename=str(path),
                maxBytes=config.file_max_bytes,
                backupCount=config.file_backup_count,
                encoding="utf-8",
            )
        )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.PositionalArgumentsFormatter(),
    ]
    if config.include_module:
        shared_processors.insert(1, _add_module_info)

    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    renderer = (
        structlog.processors.JSONRenderer()
        if config.format == LogFormat.JSON
        else structlog.dev.ConsoleRenderer()
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    for handler in handlers:
        handler.setFormatter(formatter)
        root.addHandler(handler)
