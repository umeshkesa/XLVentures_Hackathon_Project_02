"""KnowledgeVersionManager — manages document versioning.

Supports creating, updating, retrieving, comparing, and restoring
document versions. Maintains version history with metadata about
each version's lifecycle status and active state.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument
from adip.knowledge.enums import KnowledgeLifecycleStatus
from adip.knowledge.execution.models import KnowledgeVersionRecord

log = structlog.get_logger(__name__)


class KnowledgeVersionManager:
    """Manages version history for knowledge documents."""

    def __init__(self) -> None:
        self._versions: dict[str, list[KnowledgeVersionRecord]] = {}

    def create_version(
        self,
        document: KnowledgeDocument,
        created_by: str = "",
        change_summary: str = "",
    ) -> KnowledgeVersionRecord:
        """Create a new version record for a document."""
        doc_id = str(document.document_id)
        log.info("version_manager.create_version", document_id=doc_id)

        existing = self._versions.get(doc_id, [])
        version_number = (existing[-1].version_number + 1) if existing else 1
        parent = existing[-1].version_number if existing else None

        if existing:
            for v in existing:
                v.active = False

        record = KnowledgeVersionRecord(
            document_id=document.document_id,
            version_number=version_number,
            parent_version=parent,
            created_by=created_by,
            change_summary=change_summary,
            active=True,
        )
        self._versions.setdefault(doc_id, []).append(record)
        log.info("version_manager.create_version.complete", document_id=doc_id, version=version_number)
        return record

    def get_version(self, document_id: str, version_number: int) -> KnowledgeVersionRecord | None:
        """Retrieve a specific version by number."""
        versions = self._versions.get(document_id, [])
        for v in versions:
            if v.version_number == version_number:
                return v
        return None

    def list_versions(self, document_id: str) -> list[KnowledgeVersionRecord]:
        """List all versions for a document, ordered by version number."""
        return sorted(self._versions.get(document_id, []), key=lambda v: v.version_number)

    def get_active_version(self, document_id: str) -> KnowledgeVersionRecord | None:
        """Return the currently active version for a document."""
        versions = self._versions.get(document_id, [])
        for v in versions:
            if v.active:
                return v
        return None

    def mark_active(self, document_id: str, version_number: int) -> bool:
        """Mark a specific version as the active version."""
        versions = self._versions.get(document_id, [])
        found = False
        for v in versions:
            v.active = v.version_number == version_number
            if v.version_number == version_number:
                found = True
        log.info("version_manager.mark_active", document_id=document_id, version=version_number, found=found)
        return found

    def compare_versions(
        self,
        document_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """Compare two versions and return their differences."""
        va = self.get_version(document_id, version_a)
        vb = self.get_version(document_id, version_b)

        if va is None or vb is None:
            raise ValueError(f"Version not found: {version_a if va is None else version_b}")

        return {
            "document_id": document_id,
            "version_a": version_a,
            "version_b": version_b,
            "a_created": va.created_at.isoformat(),
            "b_created": vb.created_at.isoformat(),
            "a_created_by": va.created_by,
            "b_created_by": vb.created_by,
            "a_summary": va.change_summary,
            "b_summary": vb.change_summary,
            "a_lifecycle": va.lifecycle_status.value,
            "b_lifecycle": vb.lifecycle_status.value,
        }

    def restore_version(self, document_id: str, version_number: int) -> KnowledgeVersionRecord | None:
        """Restore a previous version as a new active version (metadata only)."""
        original = self.get_version(document_id, version_number)
        if original is None:
            return None

        log.info("version_manager.restore_version", document_id=document_id, version=version_number)
        record = KnowledgeVersionRecord(
            document_id=original.document_id,
            version_number=original.version_number,
            parent_version=original.parent_version,
            created_by="restore",
            change_summary=f"Restored from version {version_number}",
            active=True,
        )
        self._versions.setdefault(document_id, []).append(record)
        for v in self._versions[document_id]:
            v.active = v.version_id == record.version_id
        return record

    def update_lifecycle_status(
        self,
        document_id: str,
        version_number: int,
        status: KnowledgeLifecycleStatus,
    ) -> bool:
        """Update the lifecycle status of a specific version."""
        version = self.get_version(document_id, version_number)
        if version is None:
            return False
        log.info("version_manager.update_lifecycle_status", document_id=document_id, version=version_number, status=status.value)
        version.lifecycle_status = status
        return True

    def clear(self) -> None:
        """Clear all version data."""
        self._versions.clear()
