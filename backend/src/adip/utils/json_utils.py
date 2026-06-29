"""JSON serialisation helpers with support for common non-JSON types."""

from __future__ import annotations

import json
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import PurePath
from typing import Any
from uuid import UUID


class ADIPJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles types commonly found in ADIP models.

    Supported types:

    * ``datetime`` / ``date`` / ``time``
    * ``UUID``
    * ``Decimal``
    * ``Enum`` (via ``.value``)
    * ``PurePath``
    * ``bytes`` (decoded as UTF-8)
    * ``set`` / ``frozenset`` (serialised as lists)
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime, date, time)):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, PurePath):
            return str(o)
        if isinstance(o, bytes):
            return o.decode("utf-8", errors="replace")
        if isinstance(o, (set, frozenset)):
            return list(o)
        return super().default(o)


def safe_dumps(obj: Any, **kwargs: Any) -> str:
    """Serialize *obj* to a JSON string, falling back to ``repr`` on failure.

    All ``**kwargs`` are forwarded to ``json.dumps``.
    """
    try:
        return json.dumps(obj, cls=ADIPJSONEncoder, **kwargs)
    except (TypeError, ValueError, OverflowError):
        return json.dumps(repr(obj))


def safe_loads(s: str | bytes | bytearray, **kwargs: Any) -> Any:
    """Deserialize a JSON string, returning ``None`` on failure.

    All ``**kwargs`` are forwarded to ``json.loads``.
    """
    try:
        return json.loads(s, **kwargs)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def pretty_json(obj: Any, **kwargs: Any) -> str:
    """Serialize *obj* as indented, human-readable JSON."""
    return safe_dumps(obj, indent=2, **kwargs)
