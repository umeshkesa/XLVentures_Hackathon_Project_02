"""DefaultPlatformVersionManager — tracks versions for all platform modules."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformVersionRecord
from adip.platform.enums import ModuleName
from adip.platform.interfaces import PlatformVersionManager

logger = structlog.get_logger(__name__)


class DefaultPlatformVersionManager(PlatformVersionManager):
    """Manages version tracking for all platform modules.

    Maintains an in-memory store of version records for each module.
    """

    def __init__(self) -> None:
        self._versions: dict[str, PlatformVersionRecord] = {}

        for module in ModuleName:
            record = PlatformVersionRecord(
                module=module.value,
                version="1.0.0",
                status="active",
            )
            self._versions[module.value] = record

        logger.debug("version_manager.initialized", modules=len(self._versions))

    def get_version(self, module: str) -> PlatformVersionRecord:
        if module not in self._versions:
            self._versions[module] = PlatformVersionRecord(
                module=module,
                version="0.0.0",
                status="unknown",
            )
        return self._versions[module]

    def list_versions(self) -> list[PlatformVersionRecord]:
        return list(self._versions.values())

    def update_version(self, module: str, version: str) -> PlatformVersionRecord:
        record = PlatformVersionRecord(
            module=module,
            version=version,
            status="active",
        )
        self._versions[module] = record
        logger.debug("version_manager.updated", module=module, version=version)
        return record
