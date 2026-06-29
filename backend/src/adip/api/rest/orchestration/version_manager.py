"""ApiVersionManager — manages API version compatibility and history."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.api.rest.enums import ApiVersion

logger = structlog.get_logger(__name__)


class VersionHistory:
    """A single version history entry."""

    def __init__(self, version: str, status: str = "active", description: str = "") -> None:
        self.version = version
        self.status = status
        self.description = description
        self.created_at = datetime.now(UTC)


class ApiVersionManager:
    """Manages API version lifecycle, compatibility checks, and history."""

    SUPPORTED_VERSIONS = {ApiVersion.V1}

    def __init__(self) -> None:
        self._active_version: str = ApiVersion.V1.value
        self._history: list[VersionHistory] = [
            VersionHistory(ApiVersion.V1.value, "active", "Initial API version"),
        ]

    def get_active_version(self) -> str:
        return self._active_version

    def set_active_version(self, version: str) -> None:
        old = self._active_version
        self._active_version = version
        self._history.append(VersionHistory(version, "active", f"Activated from {old}"))
        logger.info("api_version.activated", version=version, old=old)

    def is_supported(self, version: str) -> bool:
        return version in {v.value for v in self.SUPPORTED_VERSIONS}

    def check_compatibility(self, version: str) -> bool:
        try:
            api_version = ApiVersion(version)
        except ValueError:
            return False
        return api_version in self.SUPPORTED_VERSIONS

    def get_history(self) -> list[dict[str, Any]]:
        return [
            {
                "version": h.version,
                "status": h.status,
                "description": h.description,
                "created_at": h.created_at.isoformat(),
            }
            for h in self._history
        ]

    def register_version(self, version: str, description: str = "") -> None:
        self._history.append(VersionHistory(version, "registered", description))
        logger.info("api_version.registered", version=version)
