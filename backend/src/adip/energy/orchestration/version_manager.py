"""EnergyVersionManager — manages version tracking for energy entities.

Provides version creation, retrieval, and comparison for energy
domain entities. Deterministic placeholder implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.energy.orchestration.models import EnergyVersionRecord

log = structlog.get_logger(__name__)


class EnergyVersionManager:
    """Manages version tracking for energy domain entities.

    Deterministic placeholder that creates, stores, and retrieves
    version records for energy domain entities.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[EnergyVersionRecord]] = {}

    def create_version(
        self,
        entity_id: str,
        entity_type: str,
        data: dict[str, Any] | None = None,
        created_by: str = "system",
        change_description: str = "",
        correlation_id: str = "",
    ) -> EnergyVersionRecord:
        """Create a new version for an entity.

        Args:
            entity_id: The entity identifier.
            entity_type: Type of entity.
            data: Versioned data snapshot.
            created_by: Who or what created this version.
            change_description: Description of changes.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created EnergyVersionRecord.
        """
        existing = self._versions.get(entity_id, [])
        version_number = len(existing) + 1

        version = EnergyVersionRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            version_number=version_number,
            data=data or {},
            created_by=created_by,
            change_description=change_description,
            timestamp=datetime.now(UTC),
        )
        existing.append(version)
        self._versions[entity_id] = existing

        log.info(
            "version.created",
            version_id=str(version.version_id),
            entity_id=entity_id,
            version_number=version_number,
            correlation_id=correlation_id,
        )
        return version

    def get_versions(
        self,
        entity_id: str,
    ) -> list[EnergyVersionRecord]:
        """Get all versions for an entity.

        Args:
            entity_id: The entity identifier.

        Returns:
            List of EnergyVersionRecord instances.
        """
        return self._versions.get(entity_id, [])

    def get_latest_version(
        self,
        entity_id: str,
    ) -> EnergyVersionRecord | None:
        """Get the latest version for an entity.

        Args:
            entity_id: The entity identifier.

        Returns:
            Latest EnergyVersionRecord if found, None otherwise.
        """
        versions = self._versions.get(entity_id, [])
        return versions[-1] if versions else None

    def compare_versions(
        self,
        entity_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """Compare two versions of an entity.

        Args:
            entity_id: The entity identifier.
            version_a: First version number.
            version_b: Second version number.

        Returns:
            Dict with comparison results.
        """
        versions = self._versions.get(entity_id, [])
        va = next((v for v in versions if v.version_number == version_a), None)
        vb = next((v for v in versions if v.version_number == version_b), None)

        if va is None or vb is None:
            return {"error": "Version not found", "changed": True}

        return {
            "version_a": version_a,
            "version_b": version_b,
            "changed": va.data != vb.data,
            "changes_detected": len(set(va.data.keys()) ^ set(vb.data.keys())),
        }

    def count(self) -> int:
        """Get the total number of versions.

        Returns:
            Total version count.
        """
        return sum(len(v) for v in self._versions.values())

    def count_for_entity(self, entity_id: str) -> int:
        """Get the number of versions for an entity.

        Args:
            entity_id: The entity identifier.

        Returns:
            Version count for the entity.
        """
        return len(self._versions.get(entity_id, []))

    def clear(self) -> None:
        """Clear all versions."""
        self._versions.clear()
        log.info("versions.cleared")
