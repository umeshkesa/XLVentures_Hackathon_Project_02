"""EndpointHealth — tracks health of routers, middleware, adapters, and services.

Phase 3.5 endpoint-level health tracking.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

from adip.api.rest.enums import HealthStatus

logger = structlog.get_logger(__name__)


class EndpointHealthEntry:
    """Health status for a single endpoint or component."""

    def __init__(self, name: str, component_type: str, status: HealthStatus = HealthStatus.HEALTHY) -> None:
        self.entry_id: UUID = uuid4()
        self.name: str = name
        self.component_type: str = component_type
        self.status: HealthStatus = status
        self.last_checked: datetime = datetime.now(UTC)
        self.error_count: int = 0
        self.success_count: int = 0
        self.details: dict[str, Any] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": str(self.entry_id),
            "name": self.name,
            "component_type": self.component_type,
            "status": self.status.value,
            "last_checked": self.last_checked.isoformat(),
            "error_count": self.error_count,
            "success_count": self.success_count,
            "details": self.details,
        }


class EndpointHealth:
    """Tracks health of routers, middleware, adapters, and services."""

    TYPE_ROUTER = "router"
    TYPE_MIDDLEWARE = "middleware"
    TYPE_ADAPTER = "adapter"
    TYPE_SERVICE = "service"

    def __init__(self) -> None:
        self._entries: dict[str, EndpointHealthEntry] = {}

    def register(self, name: str, component_type: str, status: HealthStatus = HealthStatus.HEALTHY) -> EndpointHealthEntry:
        entry = EndpointHealthEntry(name, component_type, status)
        self._entries[f"{component_type}:{name}"] = entry
        logger.debug("endpoint_health.registered", name=name, type=component_type, status=status.value)
        return entry

    def report_success(self, name: str, component_type: str) -> None:
        key = f"{component_type}:{name}"
        if key not in self._entries:
            self.register(name, component_type)
        entry = self._entries[key]
        entry.success_count += 1
        entry.last_checked = datetime.now(UTC)
        entry.status = HealthStatus.HEALTHY

    def report_failure(self, name: str, component_type: str, details: dict[str, Any] | None = None) -> None:
        key = f"{component_type}:{name}"
        if key not in self._entries:
            self.register(name, component_type)
        entry = self._entries[key]
        entry.error_count += 1
        entry.last_checked = datetime.now(UTC)
        entry.details = details or {}
        if entry.error_count >= 5:
            entry.status = HealthStatus.UNHEALTHY
        elif entry.error_count >= 2:
            entry.status = HealthStatus.DEGRADED

    def get_health(self, component_type: str | None = None) -> list[dict[str, Any]]:
        if component_type:
            return [
                entry.to_dict()
                for key, entry in self._entries.items()
                if key.startswith(f"{component_type}:")
            ]
        return [entry.to_dict() for entry in self._entries.values()]

    def get_summary(self) -> dict[str, Any]:
        if not self._entries:
            return {"overall_status": HealthStatus.HEALTHY.value, "total": 0}
        statuses = [entry.status for entry in self._entries.values()]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        else:
            overall = HealthStatus.DEGRADED
        by_type: dict[str, int] = {}
        for entry in self._entries.values():
            by_type[entry.component_type] = by_type.get(entry.component_type, 0) + 1
        return {
            "overall_status": overall.value,
            "total": len(self._entries),
            "healthy_count": sum(1 for e in self._entries.values() if e.status == HealthStatus.HEALTHY),
            "degraded_count": sum(1 for e in self._entries.values() if e.status == HealthStatus.DEGRADED),
            "unhealthy_count": sum(1 for e in self._entries.values() if e.status == HealthStatus.UNHEALTHY),
            "by_type": by_type,
        }

    def clear(self) -> None:
        self._entries.clear()
