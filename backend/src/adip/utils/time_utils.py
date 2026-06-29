"""Time-related utilities: timestamps, duration measurement, formatting."""

from __future__ import annotations

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(UTC)


def utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return utcnow().isoformat()


def now_timestamp() -> float:
    """Return the current Unix timestamp as a float."""
    return time.time()


def format_timestamp(ts: float) -> str:
    """Convert a Unix timestamp to an ISO-8601 string."""
    return datetime.fromtimestamp(ts, tz=UTC).isoformat()


def elapsed(start: float, end: float | None = None) -> float:
    """Return the elapsed wall-clock seconds between *start* and *end*.

    If *end* is ``None``, ``time.monotonic()`` is used.
    """
    return (end if end is not None else time.monotonic()) - start


def elapsed_ms(start: float, end: float | None = None) -> float:
    """Return the elapsed wall-clock **milliseconds** between *start* and *end*."""
    return elapsed(start, end) * 1000


@contextmanager
def measure_time() -> Generator[Callable[[], float], Any, None]:
    """Context manager that yields a callable returning elapsed seconds.

    Usage::

        with measure_time() as elapsed:
            do_something()
        logger.info("took %s s", elapsed())
    """

    start = time.monotonic()

    def _elapsed() -> float:
        return time.monotonic() - start

    yield _elapsed
