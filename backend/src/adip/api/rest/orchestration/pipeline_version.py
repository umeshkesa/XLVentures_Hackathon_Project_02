"""APIPipelineVersion — supports version creation, active version tracking, and history.

Phase 3.5 pipeline versioning for production integration.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class PipelineVersionRecord:
    """A single pipeline version record."""

    def __init__(self, version: str, description: str = "", metadata: dict[str, Any] | None = None) -> None:
        self.record_id: UUID = uuid4()
        self.version: str = version
        self.description: str = description
        self.metadata: dict[str, Any] = metadata or {}
        self.created_at: datetime = datetime.now(UTC)
        self.is_active: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": str(self.record_id),
            "version": self.version,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class APIPipelineVersion:
    """Manages pipeline version creation, activation, and history."""

    def __init__(self) -> None:
        self._records: dict[str, PipelineVersionRecord] = {}
        self._active_version: str | None = None

    def create_version(self, version: str, description: str = "", metadata: dict[str, Any] | None = None) -> PipelineVersionRecord:
        record = PipelineVersionRecord(version, description, metadata)
        if self._active_version is None:
            record.is_active = True
            self._active_version = version
        self._records[version] = record
        logger.info("pipeline_version.created", version=version)
        return record

    def get_active_version(self) -> str | None:
        return self._active_version

    def set_active_version(self, version: str) -> bool:
        record = self._records.get(version)
        if record is None:
            return False
        if self._active_version and self._active_version in self._records:
            self._records[self._active_version].is_active = False
        record.is_active = True
        self._active_version = version
        logger.info("pipeline_version.activated", version=version)
        return True

    def get_version(self, version: str) -> PipelineVersionRecord | None:
        return self._records.get(version)

    def get_history(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in sorted(self._records.values(), key=lambda r: r.created_at, reverse=True)]

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()
        self._active_version = None
