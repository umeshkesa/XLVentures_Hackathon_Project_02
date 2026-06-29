"""VersionManager — maintains version history for memory records.

Supports version increment, history tracking, rollback metadata,
latest version lookup, and version comparison.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.memory.contracts.models import MemoryRecord
from adip.memory.execution.models import VersionHistory

log = structlog.get_logger(__name__)


class VersionManager:
    """Tracks version history for memory records.

    Each record's version field is incremented on every update.
    A snapshot of the record is saved in the version history.
    """

    def __init__(self) -> None:
        self._history: dict[str, list[VersionHistory]] = {}

    def record_creation(self, record: MemoryRecord) -> int:
        """Record the initial version of a record.  Returns the version."""
        key = str(record.memory_id)
        self._history[key] = [
            VersionHistory(
                version_number=record.version,
                memory_id=record.memory_id,
                snapshot=record.model_dump(),
                reason="Record created",
            ),
        ]
        log.debug("version.created", memory_id=key, version=record.version)
        return record.version

    def increment(self, record: MemoryRecord) -> int:
        """Increment the version and record the snapshot.

        Returns the new version number.  Modifies the record in place.
        """
        key = str(record.memory_id)
        record.version += 1

        entry = VersionHistory(
            version_number=record.version,
            memory_id=record.memory_id,
            snapshot=record.model_dump(),
            reason="Record updated",
        )
        self._history.setdefault(key, []).append(entry)

        log.debug("version.incremented", memory_id=key, new_version=record.version)
        return record.version

    def get_history(self, memory_id: str) -> list[VersionHistory]:
        """Return the full version history for a record."""
        return list(self._history.get(memory_id, []))

    def get_latest_version(self, memory_id: str) -> int | None:
        """Return the latest version number, or None if unknown."""
        history = self._history.get(memory_id, [])
        if not history:
            return None
        return history[-1].version_number

    def get_snapshot(self, memory_id: str, version: int) -> dict[str, Any] | None:
        """Return the snapshot for a specific version, or None."""
        for entry in self._history.get(memory_id, []):
            if entry.version_number == version:
                return dict(entry.snapshot)
        return None

    def compare_versions(
        self,
        memory_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, tuple[Any, Any]]:
        """Compare two versions and return a dict of changed fields.

        Returns {field_name: (value_in_a, value_in_b)} for fields
        that differ between versions.
        """
        snap_a = self.get_snapshot(memory_id, version_a) or {}
        snap_b = self.get_snapshot(memory_id, version_b) or {}
        diffs: dict[str, tuple[Any, Any]] = {}
        all_keys = set(snap_a) | set(snap_b)
        for key in all_keys:
            va = snap_a.get(key)
            vb = snap_b.get(key)
            if va != vb:
                diffs[key] = (va, vb)
        return diffs

    def rollback_metadata(self, record: MemoryRecord, target_version: int) -> MemoryRecord:
        """Restore metadata from a previous version's snapshot.

        Returns a new record with the rolled-back metadata.
        Does NOT modify the original.
        """
        snapshot = self.get_snapshot(str(record.memory_id), target_version)
        if snapshot is None:
            raise ValueError(f"No snapshot found for version {target_version}")

        restored = record.model_copy(deep=True)
        restored.metadata = dict(snapshot.get("metadata", {}))
        restored.version = target_version
        restored.updated_at = datetime.now(UTC)

        log.info(
            "version.rollback",
            memory_id=str(record.memory_id),
            target_version=target_version,
        )
        return restored
