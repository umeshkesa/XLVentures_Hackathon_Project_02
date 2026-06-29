"""DefaultPlatformSnapshotManager — creates immutable platform snapshots."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.platform.contracts.models import PlatformSnapshot
from adip.platform.interfaces import PlatformSnapshotManager, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultPlatformSnapshotManager(PlatformSnapshotManager):
    """Creates immutable point-in-time snapshots of the platform state."""

    def __init__(self, version: str = "1.0.0") -> None:
        self._version = version
        logger.debug("snapshot_manager.initialized")

    def create_snapshot(self, registry: ServiceRegistry, versions: dict[str, str]) -> PlatformSnapshot:
        descriptors = registry.get_service_descriptors()
        all_services = registry.resolve_all()

        managers = [d.name for d in descriptors if "manager" in d.name.lower()]
        coordinators = [d.name for d in descriptors if "coordinator" in d.name.lower()]

        registry_overview = {
            "total_services": len(all_services),
            "total_descriptors": len(descriptors),
            "modules": [m["name"] for m in registry.get_modules()],
        }

        logger.info(
            "snapshot.created",
            services=len(descriptors),
            managers=len(managers),
            coordinators=len(coordinators),
            versions=len(versions),
        )

        return PlatformSnapshot(
            snapshot_id=str(uuid.uuid4()),
            version=self._version,
            services=descriptors,
            managers=managers,
            coordinators=coordinators,
            registry=registry_overview,
            versions=dict(versions),
            timestamp=datetime.now(UTC),
        )
