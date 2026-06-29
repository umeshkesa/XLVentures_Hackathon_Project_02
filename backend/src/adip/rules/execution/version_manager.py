"""RuleVersionManager — manages rule versioning.

Supports creating, retrieving, comparing, listing, restoring,
and marking active versions. Maintains version history with
metadata about each version's active state.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.rules.contracts.models import Rule
from adip.rules.execution.models import VersionRecord

log = structlog.get_logger(__name__)


class RuleVersionManager:
    """Manages version history for rules."""

    def __init__(self) -> None:
        self._versions: dict[str, list[VersionRecord]] = {}

    def create_version(
        self,
        rule: Rule,
        created_by: str = "",
        change_summary: str = "",
    ) -> VersionRecord:
        """Create a new version record for a rule."""
        rule_id = str(rule.rule_id)
        log.info("rule_version_manager.create_version", rule_id=rule_id)

        existing = self._versions.get(rule_id, [])
        version_number = (existing[-1].version_number + 1) if existing else 1
        parent = existing[-1].version_number if existing else None

        for v in existing:
            v.active = False

        record = VersionRecord(
            rule_id=rule.rule_id,
            version_number=version_number,
            parent_version=parent,
            created_by=created_by,
            change_summary=change_summary,
            active=True,
        )
        self._versions.setdefault(rule_id, []).append(record)
        log.info("rule_version_manager.create_version.complete", rule_id=rule_id, version=version_number)
        return record

    def get_version(self, rule_id: str, version_number: int) -> VersionRecord | None:
        """Retrieve a specific version by number."""
        versions = self._versions.get(rule_id, [])
        for v in versions:
            if v.version_number == version_number:
                return v
        return None

    def list_versions(self, rule_id: str) -> list[VersionRecord]:
        """List all versions for a rule, ordered by version number."""
        return sorted(self._versions.get(rule_id, []), key=lambda v: v.version_number)

    def get_active_version(self, rule_id: str) -> VersionRecord | None:
        """Return the currently active version for a rule."""
        versions = self._versions.get(rule_id, [])
        for v in versions:
            if v.active:
                return v
        return None

    def mark_active(self, rule_id: str, version_number: int) -> bool:
        """Mark a specific version as the active version."""
        versions = self._versions.get(rule_id, [])
        found = False
        for v in versions:
            v.active = v.version_number == version_number
            if v.version_number == version_number:
                found = True
        log.info("rule_version_manager.mark_active", rule_id=rule_id, version=version_number, found=found)
        return found

    def compare_versions(
        self,
        rule_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """Compare two versions and return their metadata differences."""
        va = self.get_version(rule_id, version_a)
        vb = self.get_version(rule_id, version_b)

        if va is None or vb is None:
            raise ValueError(f"Version not found: {version_a if va is None else version_b}")

        return {
            "rule_id": rule_id,
            "version_a": version_a,
            "version_b": version_b,
            "a_created": va.created_at.isoformat(),
            "b_created": vb.created_at.isoformat(),
            "a_created_by": va.created_by,
            "b_created_by": vb.created_by,
            "a_summary": va.change_summary,
            "b_summary": vb.change_summary,
            "a_active": va.active,
            "b_active": vb.active,
        }

    def restore_version(self, rule_id: str, version_number: int) -> VersionRecord | None:
        """Restore a previous version as a new active version (metadata only)."""
        original = self.get_version(rule_id, version_number)
        if original is None:
            return None

        log.info("rule_version_manager.restore_version", rule_id=rule_id, version=version_number)
        record = VersionRecord(
            rule_id=original.rule_id,
            version_number=original.version_number,
            parent_version=original.parent_version,
            created_by="restore",
            change_summary=f"Restored from version {version_number}",
            active=True,
        )
        self._versions.setdefault(rule_id, []).append(record)
        for v in self._versions[rule_id]:
            v.active = v.version_id == record.version_id
        return record

    def clear(self) -> None:
        """Clear all version data."""
        self._versions.clear()
