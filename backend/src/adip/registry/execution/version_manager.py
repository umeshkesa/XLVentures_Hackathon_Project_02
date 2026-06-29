"""RegistryVersionManager — manages version history for registry entries.

Supports creating, updating, comparing versions, tracking active
versions, and retrieving version history.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.registry.contracts.models import RegistryEntry
from adip.registry.execution.models import VersionRecord

log = structlog.get_logger(__name__)


class RegistryVersionManager:
    """Manages version history for registry entries.

    Tracks all versions of an entry, supports retrieving specific
    versions, comparing versions, and listing version history.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[VersionRecord]] = {}  # entry_id → versions

    def create_version(
        self,
        entry: RegistryEntry,
        release_notes: str = "",
        created_by: str = "",
    ) -> VersionRecord:
        """Create a new version record for an entry."""
        log.info(
            "registry_version_manager.create_version",
            entry_id=str(entry.entry_id),
            version=entry.version,
        )
        eid = str(entry.entry_id)
        existing = self._versions.get(eid, [])
        previous_version = existing[-1].version if existing else ""

        # Deactivate previous active version
        for v in existing:
            if v.is_active:
                v.is_active = False

        record = VersionRecord(
            entry_id=entry.entry_id,
            entry_name=entry.name,
            version=entry.version,
            previous_version=previous_version,
            is_active=True,
            snapshot=entry.model_dump(),
            release_notes=release_notes,
            created_by=created_by,
        )
        existing.append(record)
        self._versions[eid] = existing
        return record

    def get_version(self, entry_id: str, version: str) -> VersionRecord | None:
        """Retrieve a specific version of an entry."""
        log.info("registry_version_manager.get_version", entry_id=entry_id, version=version)
        records = self._versions.get(entry_id, [])
        for r in records:
            if r.version == version:
                return r
        return None

    def get_version_history(self, entry_id: str) -> list[VersionRecord]:
        """Retrieve the version history for an entry."""
        log.info("registry_version_manager.get_version_history", entry_id=entry_id)
        return self._versions.get(entry_id, [])

    def get_active_version(self, entry_id: str) -> VersionRecord | None:
        """Get the currently active version of an entry."""
        log.info("registry_version_manager.get_active_version", entry_id=entry_id)
        records = self._versions.get(entry_id, [])
        for r in records:
            if r.is_active:
                return r
        return records[-1] if records else None

    def compare_versions(
        self,
        entry_id: str,
        version_a: str,
        version_b: str,
    ) -> dict[str, Any]:
        """Compare two versions of an entry. Returns diff dictionary."""
        log.info("registry_version_manager.compare_versions", entry_id=entry_id, a=version_a, b=version_b)
        va = self.get_version(entry_id, version_a)
        vb = self.get_version(entry_id, version_b)
        if va is None or vb is None:
            return {"error": "One or both versions not found", "version_a_found": va is not None, "version_b_found": vb is not None}
        diff: dict[str, Any] = {
            "entry_id": entry_id,
            "version_a": version_a,
            "version_b": version_b,
            "version_a_created": va.created_at.isoformat(),
            "version_b_created": vb.created_at.isoformat(),
            "name_changed": va.entry_name != vb.entry_name,
            "snapshot_changed": va.snapshot != vb.snapshot,
        }
        return diff

    def rollback(self, entry_id: str, version: str) -> VersionRecord | None:
        """Rollback an entry to a previous version (creates a new version)."""
        log.info("registry_version_manager.rollback", entry_id=entry_id, target_version=version)
        target = self.get_version(entry_id, version)
        if target is None:
            return None
        rollback_record = VersionRecord(
            entry_id=uuid.UUID(entry_id),
            entry_name=target.entry_name,
            version=f"{target.version}-rollback",
            previous_version=version,
            is_active=True,
            snapshot=dict(target.snapshot),
            release_notes=f"Rollback to version {version}",
            created_by="system",
        )
        records = self._versions.get(entry_id, [])
        for r in records:
            if r.is_active:
                r.is_active = False
        records.append(rollback_record)
        self._versions[entry_id] = records
        return rollback_record

    def clear(self) -> int:
        """Clear all version records. Returns count of records cleared."""
        count = sum(len(v) for v in self._versions.values())
        self._versions.clear()
        return count
