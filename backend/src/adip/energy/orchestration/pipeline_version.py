"""DomainPipelineVersion — tracks pipeline versions.

Supports version creation, active version management,
and version history tracking for the energy domain
pipeline. Deterministic placeholder.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.energy.orchestration.models import DomainPipelineVersion

log = structlog.get_logger(__name__)


class DomainPipelineVersionManager:
    """Manages pipeline versions for the energy domain.

    Tracks pipeline configuration versions, supports
    activation and history retrieval. Deterministic
    placeholder implementation.
    """

    def __init__(self) -> None:
        self._versions: dict[str, DomainPipelineVersion] = {}
        self._active_version: str | None = None

    def create_version(
        self,
        pipeline_name: str,
        config: dict[str, Any] | None = None,
        change_description: str = "",
        created_by: str = "system",
        correlation_id: str = "",
    ) -> DomainPipelineVersion:
        """Create a new pipeline version.

        Args:
            pipeline_name: Name of the pipeline.
            config: Pipeline configuration.
            change_description: Description of changes.
            created_by: Who created the version.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created DomainPipelineVersion.
        """
        existing = self._get_versions_for_pipeline(pipeline_name)
        version_number = max((v.version_number for v in existing), default=0) + 1

        pipeline_version = DomainPipelineVersion(
            pipeline_name=pipeline_name,
            version_number=version_number,
            is_active=False,
            config=config or {},
            change_description=change_description,
            created_by=created_by,
            created_at=datetime.now(UTC),
        )
        vid = str(pipeline_version.version_id)
        self._versions[vid] = pipeline_version
        log.info(
            "pipeline_version.created",
            version_id=vid,
            pipeline_name=pipeline_name,
            version_number=version_number,
            correlation_id=correlation_id,
        )
        return pipeline_version

    def activate_version(
        self,
        version_id: str,
        correlation_id: str = "",
    ) -> DomainPipelineVersion | None:
        """Activate a pipeline version.

        Args:
            version_id: The version identifier to activate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The activated DomainPipelineVersion, or None if not found.
        """
        version = self._versions.get(version_id)
        if version is None:
            log.warning(
                "pipeline_version.not_found",
                version_id=version_id,
                correlation_id=correlation_id,
            )
            return None

        # Deactivate previous active
        if self._active_version and self._active_version in self._versions:
            prev = self._versions[self._active_version]
            self._versions[self._active_version] = prev.model_copy(
                update={"is_active": False}
            )

        self._versions[version_id] = version.model_copy(update={"is_active": True})
        self._active_version = version_id
        log.info(
            "pipeline_version.activated",
            version_id=version_id,
            pipeline_name=version.pipeline_name,
            version_number=version.version_number,
            correlation_id=correlation_id,
        )
        return self._versions[version_id]

    def get_active_version(
        self,
        pipeline_name: str,
    ) -> DomainPipelineVersion | None:
        """Get the active version for a pipeline.

        Args:
            pipeline_name: Name of the pipeline.

        Returns:
            Active DomainPipelineVersion if found, None otherwise.
        """
        if self._active_version:
            version = self._versions.get(self._active_version)
            if version and version.pipeline_name == pipeline_name:
                return version
        # Fallback: find active by pipeline name
        for v in self._versions.values():
            if v.pipeline_name == pipeline_name and v.is_active:
                return v
        return None

    def get_version(self, version_id: str) -> DomainPipelineVersion | None:
        """Get a version by ID.

        Args:
            version_id: The version identifier.

        Returns:
            DomainPipelineVersion if found, None otherwise.
        """
        return self._versions.get(version_id)

    def get_version_history(
        self,
        pipeline_name: str,
    ) -> list[DomainPipelineVersion]:
        """Get version history for a pipeline.

        Args:
            pipeline_name: Name of the pipeline.

        Returns:
            List of DomainPipelineVersion instances sorted by version number.
        """
        versions = self._get_versions_for_pipeline(pipeline_name)
        return sorted(versions, key=lambda v: v.version_number, reverse=True)

    def _get_versions_for_pipeline(
        self,
        pipeline_name: str,
    ) -> list[DomainPipelineVersion]:
        """Get all versions for a pipeline.

        Args:
            pipeline_name: Name of the pipeline.

        Returns:
            List of matching DomainPipelineVersion instances.
        """
        return [v for v in self._versions.values() if v.pipeline_name == pipeline_name]

    def count(self) -> int:
        """Get the number of pipeline versions.

        Returns:
            The count of pipeline versions.
        """
        return len(self._versions)

    def clear(self) -> None:
        """Clear all pipeline versions."""
        self._versions.clear()
        self._active_version = None
        log.info("pipeline_versions.cleared")
