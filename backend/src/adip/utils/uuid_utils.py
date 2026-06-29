"""UUID generation and validation helpers."""

from __future__ import annotations

import uuid
from time import time_ns


def generate_uuid4() -> str:
    """Return a random UUID as a hex string with dashes."""
    return str(uuid.uuid4())


def generate_uuid4_hex() -> str:
    """Return a random UUID as a 32-character hex string (no dashes)."""
    return uuid.uuid4().hex


def generate_time_ordered_uuid() -> str:
    """Return a time-sortable UUID string.

    The first 12 hex characters encode the Unix timestamp in milliseconds
    (big-endian), followed by 20 random hex characters.  This makes the
    string roughly sortable by creation time while remaining unique.
    """
    timestamp_ms = time_ns() // 1_000_000
    ts_hex = f"{timestamp_ms:012x}"
    random_hex = uuid.uuid4().hex[:20]
    return f"{ts_hex}{random_hex}"


def is_valid_uuid(value: str, version: int | None = 4) -> bool:
    """Return ``True`` if *value* is a valid UUID hex string.

    Parameters
    ----------
    value:
        The string to check.
    version:
        Expected UUID version (``None`` = any).
    """
    try:
        u = uuid.UUID(hex=value)
    except (ValueError, AttributeError):
        return False
    return not (version is not None and u.version != version)
