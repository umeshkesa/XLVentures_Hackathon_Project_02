"""Date parsing and formatting helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def format_iso(dt: datetime | None = None) -> str:
    """Return a timezone-aware ISO-8601 string.

    If *dt* is ``None``, the current UTC time is used.
    """
    if dt is None:
        dt = datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat()


def format_date_short(dt: datetime | None = None) -> str:
    """Return a short date string like ``2024-01-15``."""
    if dt is None:
        dt = datetime.now(UTC)
    return dt.strftime("%Y-%m-%d")


def format_datetime_human(dt: datetime | None = None) -> str:
    """Return a human-friendly string like ``Jan 15, 2024 14:30 UTC``."""
    if dt is None:
        dt = datetime.now(UTC)
    return dt.strftime("%b %d, %Y %H:%M %Z")


def format_relative(dt: datetime, *, now: datetime | None = None) -> str:
    """Return a relative time string (e.g. "3 minutes ago").

    Handles past and future dates up to one year.
    """
    now = now or datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    diff = abs(now - dt)
    is_past = dt < now

    if diff < timedelta(seconds=10):
        result = "just now"
    elif diff < timedelta(minutes=1):
        result = f"{int(diff.total_seconds())} seconds ago"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() // 60)
        result = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        result = f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=30):
        days = diff.days
        result = f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < timedelta(days=365):
        months = diff.days // 30
        result = f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = diff.days // 365
        result = f"{years} year{'s' if years != 1 else ''} ago"

    if not is_past:
        result = result.replace("ago", "from now")
    return result


def parse_iso(value: str) -> datetime | None:
    """Parse an ISO-8601 string into a timezone-aware datetime.

    Returns ``None`` on failure instead of raising.
    """
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, TypeError):
        return None
