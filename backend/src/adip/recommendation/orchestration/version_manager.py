"""RecommendationVersionManager — manages recommendation versions.

Supports version creation, history, active version tracking,
and comparison. Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

log = structlog.get_logger(__name__)


class VersionRecord(BaseModel):
    """A version record for a recommendation.

    Attributes:
        version_id: Unique version identifier.
        recommendation_id: The recommendation this version belongs to.
        version_number: Sequential version number.
        description: Description of this version.
        data: The version data snapshot.
        created_by: Who created this version.
        is_active: Whether this is the active version.
        created_at: When the version was created.
    """
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_id: str = Field(default="")
    version_number: int = Field(default=1, ge=1)
    description: str = Field(default="")
    data: dict[str, Any] = Field(default_factory=dict)
    created_by: str = Field(default="system")
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RecommendationVersionManager:
    """Manages versions for recommendation results.

    Deterministic placeholder for version creation, history,
    active version tracking, and comparison.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[VersionRecord]] = {}
        self._active: dict[str, str] = {}

    def create_version(
        self,
        recommendation_id: str = "",
        data: dict[str, Any] | None = None,
        description: str = "",
        created_by: str = "system",
        make_active: bool = True,
    ) -> VersionRecord:
        """Create a new version for a recommendation.

        Args:
            recommendation_id: The recommendation ID.
            data: The version data.
            description: Description of this version.
            created_by: Who created this version.
            make_active: Whether to make this the active version.

        Returns:
            The created VersionRecord.
        """
        if recommendation_id not in self._versions:
            self._versions[recommendation_id] = []
        version_number = len(self._versions[recommendation_id]) + 1

        if make_active:
            for v in self._versions.get(recommendation_id, []):
                v.is_active = False

        record = VersionRecord(
            recommendation_id=recommendation_id,
            version_number=version_number,
            description=description,
            data=data or {},
            created_by=created_by,
            is_active=make_active,
        )
        self._versions[recommendation_id].append(record)
        if make_active:
            self._active[recommendation_id] = record.version_id
        log.info("version.created", recommendation_id=recommendation_id, version=version_number)
        return record

    def get_version_history(self, recommendation_id: str) -> list[VersionRecord]:
        """Get all versions for a recommendation.

        Args:
            recommendation_id: The recommendation identifier.

        Returns:
            List of VersionRecord sorted by version number.
        """
        versions = self._versions.get(recommendation_id, [])
        return sorted(versions, key=lambda v: v.version_number)

    def get_active_version(self, recommendation_id: str) -> VersionRecord | None:
        """Get the active version for a recommendation.

        Args:
            recommendation_id: The recommendation identifier.

        Returns:
            The active VersionRecord if found, None otherwise.
        """
        active_id = self._active.get(recommendation_id)
        if active_id is None:
            versions = self._versions.get(recommendation_id, [])
            return versions[-1] if versions else None
        for v in self._versions.get(recommendation_id, []):
            if v.version_id == active_id:
                return v
        return None

    def set_active_version(self, recommendation_id: str, version_number: int) -> VersionRecord | None:
        """Set a specific version as the active version.

        Args:
            recommendation_id: The recommendation identifier.
            version_number: The version number to activate.

        Returns:
            The activated VersionRecord if found, None otherwise.
        """
        versions = self._versions.get(recommendation_id, [])
        for v in versions:
            v.is_active = v.version_number == version_number
            if v.version_number == version_number:
                self._active[recommendation_id] = v.version_id
        target = next((v for v in versions if v.version_number == version_number), None)
        if target:
            log.info("version.activated", recommendation_id=recommendation_id, version=version_number)
        return target

    def compare_versions(
        self,
        recommendation_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """Compare two versions of a recommendation.

        Args:
            recommendation_id: The recommendation identifier.
            version_a: First version number.
            version_b: Second version number.

        Returns:
            Dictionary with comparison results.
        """
        versions = self._versions.get(recommendation_id, [])
        va = next((v for v in versions if v.version_number == version_a), None)
        vb = next((v for v in versions if v.version_number == version_b), None)
        return {
            "recommendation_id": recommendation_id,
            "version_a": version_a,
            "version_b": version_b,
            "version_a_exists": va is not None,
            "version_b_exists": vb is not None,
            "data_changed": (va is not None and vb is not None and va.data != vb.data),
            "version_a_data": va.data if va else {},
            "version_b_data": vb.data if vb else {},
        }

    def clear(self) -> None:
        """Clear all versions."""
        self._versions.clear()
        self._active.clear()

    def count(self) -> int:
        """Get the total number of version records."""
        return sum(len(v) for v in self._versions.values())
