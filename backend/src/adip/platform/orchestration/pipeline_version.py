"""DefaultPlatformPipelineVersionManager — manages pipeline versioning."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PipelineVersionRecord
from adip.platform.interfaces import PlatformPipelineVersionManager

logger = structlog.get_logger(__name__)


class DefaultPlatformPipelineVersionManager(PlatformPipelineVersionManager):
    """Manages pipeline version creation, activation, and history tracking."""

    def __init__(self) -> None:
        self._versions: dict[str, PipelineVersionRecord] = {}
        self._active_version: str | None = None
        self._counter = 0
        logger.debug("pipeline_version_manager.initialized")

    def create_version(
        self,
        platform_version: str,
        modules: list[str],
        stage_count: int,
    ) -> PipelineVersionRecord:
        self._counter += 1
        pipeline_version = f"pipeline-v{self._counter}"

        record = PipelineVersionRecord(
            pipeline_version=pipeline_version,
            platform_version=platform_version,
            is_active=False,
            stage_count=stage_count,
            modules=sorted(modules),
            metadata={
                "created_by": "DefaultPlatformPipelineVersionManager",
            },
        )
        self._versions[pipeline_version] = record
        logger.debug("pipeline_version.created", version=pipeline_version, platform=platform_version)
        return record

    def activate_version(self, pipeline_version: str) -> PipelineVersionRecord | None:
        if pipeline_version not in self._versions:
            logger.warning("pipeline_version.not_found", version=pipeline_version)
            return None

        for v in self._versions.values():
            v.is_active = False

        self._versions[pipeline_version].is_active = True
        self._active_version = pipeline_version
        logger.info("pipeline_version.activated", version=pipeline_version)
        return self._versions[pipeline_version]

    def get_active_version(self) -> PipelineVersionRecord | None:
        if self._active_version and self._active_version in self._versions:
            return self._versions[self._active_version]
        return None

    def get_version_history(self) -> list[PipelineVersionRecord]:
        return list(self._versions.values())
