from __future__ import annotations

import hashlib
import json
from typing import Any

import structlog

log = structlog.get_logger(__name__)


def row_hash(row: dict[str, str]) -> str:
    """Compute a deterministic hash for a row dict (sorted keys)."""
    normalized = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class DeduplicationResult:
    def __init__(self) -> None:
        self.imported: list[dict[str, str]] = []
        self.skipped: list[dict[str, str]] = []
        self.duplicates: list[dict[str, str]] = []

    @property
    def imported_count(self) -> int:
        return len(self.imported)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)


class InMemoryDeduplicator:
    """Simple in-memory deduplicator that tracks seen hashes during an import run."""

    def __init__(self) -> None:
        self._seen_hashes: set[str] = set()
        self._seen_keys: dict[str, set[str]] = {}

    def add_key_index(self, key_name: str) -> None:
        """Register a key field for exact-match deduplication."""
        if key_name not in self._seen_keys:
            self._seen_keys[key_name] = set()

    def is_duplicate_by_hash(self, row: dict[str, str]) -> bool:
        """Check if a row's content hash has been seen before."""
        h = row_hash(row)
        if h in self._seen_hashes:
            return True
        self._seen_hashes.add(h)
        return False

    def is_duplicate_by_key(self, key_name: str, row: dict[str, str]) -> bool:
        """Check if a row's key value has been seen before."""
        if key_name not in self._seen_keys:
            self._seen_keys[key_name] = set()
        val = row.get(key_name, "")
        if val in self._seen_keys[key_name]:
            return True
        self._seen_keys[key_name].add(val)
        return False

    def deduplicate(
        self,
        rows: list[dict[str, str]],
        key_fields: list[str] | None = None,
        use_hash: bool = True,
    ) -> DeduplicationResult:
        """Deduplicate a list of rows."""
        result = DeduplicationResult()
        for row in rows:
            if use_hash and self.is_duplicate_by_hash(row):
                result.duplicates.append(row)
                continue
            if key_fields:
                is_dup = False
                for kf in key_fields:
                    if self.is_duplicate_by_key(kf, row):
                        result.duplicates.append(row)
                        is_dup = True
                        break
                if is_dup:
                    continue
            result.imported.append(row)
        return result

    def reset(self) -> None:
        """Clear all seen hashes and keys."""
        self._seen_hashes.clear()
        self._seen_keys.clear()


class DatabaseDeduplicator:
    """Deduplicator that tracks seen keys across the database."""

    def __init__(self, existing_keys: dict[str, set[str]] | None = None) -> None:
        self._existing_keys: dict[str, set[str]] = existing_keys or {}
        self._new_keys: dict[str, set[str]] = {}

    def load_existing_keys(self, key_name: str, values: set[str]) -> None:
        """Pre-populate existing keys from the database."""
        self._existing_keys[key_name] = values

    def is_duplicate(
        self, key_name: str, value: str
    ) -> bool:
        """Check if a key value exists in DB or has been seen this run."""
        existing = self._existing_keys.get(key_name, set())
        new = self._new_keys.get(key_name, set())
        if value in existing or value in new:
            return True
        if key_name not in self._new_keys:
            self._new_keys[key_name] = set()
        self._new_keys[key_name].add(value)
        return False

    def new_keys_since_last_check(self, key_name: str) -> set[str]:
        """Return and clear newly seen keys for the given index."""
        result = self._new_keys.get(key_name, set()).copy()
        if key_name in self._new_keys:
            self._new_keys[key_name] = set()
        return result
