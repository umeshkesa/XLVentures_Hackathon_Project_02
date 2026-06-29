"""GovernancePipelineVersion — pipeline version management.

Supports version creation, active version tracking, version
history, and comparison for the governance pipeline.
Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class PipelineVersionRecord:
    """Record of a governance pipeline version."""

    def __init__(
        self,
        version_id: str,
        version_number: int,
        pipeline_name: str,
        description: str,
        is_active: bool,
        stages: list[str],
    ) -> None:
        self.version_id = version_id
        self.version_number = version_number
        self.pipeline_name = pipeline_name
        self.description = description
        self.is_active = is_active
        self.stages = stages
        self.created_at = datetime.now(UTC)


class GovernancePipelineVersion:
    """Manages governance pipeline versions.

    Supports:
    - Version creation with stage snapshots
    - Active version tracking
    - Version history retrieval
    - Version comparison

    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._versions: dict[str, PipelineVersionRecord] = {}
        self._pipeline_versions: dict[str, list[str]] = {}
        self._active_versions: dict[str, str] = {}

    def create_version(
        self,
        pipeline_name: str,
        description: str = "",
        stages: list[str] | None = None,
        set_active: bool = True,
        correlation_id: str = "",
    ) -> PipelineVersionRecord:
        """Create a new pipeline version.

        Args:
            pipeline_name: The pipeline name.
            description: Description of this version.
            stages: List of stage names in this version.
            set_active: Whether to set this version as active.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            PipelineVersionRecord for the new version.
        """
        current_versions = self._pipeline_versions.get(pipeline_name, [])
        version_number = len(current_versions) + 1

        version = PipelineVersionRecord(
            version_id=str(uuid.uuid4()),
            version_number=version_number,
            pipeline_name=pipeline_name,
            description=description or f"Version {version_number}",
            is_active=set_active,
            stages=stages or [],
        )
        self._versions[version.version_id] = version
        if pipeline_name not in self._pipeline_versions:
            self._pipeline_versions[pipeline_name] = []
        self._pipeline_versions[pipeline_name].append(version.version_id)

        if set_active:
            self._active_versions[pipeline_name] = version.version_id

        log.info(
            "pipeline_version.created",
            version_id=version.version_id,
            pipeline_name=pipeline_name,
            version_number=version_number,
            correlation_id=correlation_id,
        )
        return version

    def get_active_version(self, pipeline_name: str) -> PipelineVersionRecord | None:
        """Get the active version for a pipeline.

        Args:
            pipeline_name: The pipeline name.

        Returns:
            PipelineVersionRecord if found, None otherwise.
        """
        version_id = self._active_versions.get(pipeline_name)
        if version_id is None:
            return None
        return self._versions.get(version_id)

    def set_active_version(
        self,
        version_id: str,
        correlation_id: str = "",
    ) -> bool:
        """Set a specific version as active.

        Args:
            version_id: The version identifier to activate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if activated, False if version not found.
        """
        version = self._versions.get(version_id)
        if version is None:
            return False
        version.is_active = True
        self._active_versions[version.pipeline_name] = version_id
        log.info(
            "pipeline_version.activated",
            version_id=version_id,
            pipeline_name=version.pipeline_name,
            correlation_id=correlation_id,
        )
        return True

    def get_version(self, version_id: str) -> PipelineVersionRecord | None:
        """Get a version by ID.

        Args:
            version_id: The version identifier.

        Returns:
            PipelineVersionRecord if found, None otherwise.
        """
        return self._versions.get(version_id)

    def get_versions_for_pipeline(
        self,
        pipeline_name: str,
    ) -> list[PipelineVersionRecord]:
        """Get all versions for a pipeline.

        Args:
            pipeline_name: The pipeline name.

        Returns:
            List of PipelineVersionRecord for the pipeline.
        """
        version_ids = self._pipeline_versions.get(pipeline_name, [])
        return [self._versions[vid] for vid in version_ids if vid in self._versions]

    def compare_versions(
        self,
        version_id_a: str,
        version_id_b: str,
    ) -> dict[str, Any]:
        """Compare two pipeline versions.

        Args:
            version_id_a: First version identifier.
            version_id_b: Second version identifier.

        Returns:
            Dict with comparison results.
        """
        va = self._versions.get(version_id_a)
        vb = self._versions.get(version_id_b)
        if va is None or vb is None:
            return {"error": "One or both versions not found"}

        return {
            "version_a": va.version_number,
            "version_b": vb.version_number,
            "pipeline_name": va.pipeline_name,
            "same_name": va.pipeline_name == vb.pipeline_name,
            "same_stages": va.stages == vb.stages,
            "stages_a": va.stages,
            "stages_b": vb.stages,
            "added_stages": [s for s in vb.stages if s not in va.stages],
            "removed_stages": [s for s in va.stages if s not in vb.stages],
        }

    def count(self) -> int:
        """Get the total number of versions.

        Returns:
            The total version count.
        """
        return len(self._versions)

    def clear(self) -> None:
        """Clear all versions."""
        self._versions.clear()
        self._pipeline_versions.clear()
        self._active_versions.clear()
