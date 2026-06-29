"""APIHealthManager — aggregates health status of routers, middleware, adapters, services."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ComponentHealth:
    """Health status of a single component."""

    def __init__(self, name: str, status: str = "healthy", details: dict[str, Any] | None = None) -> None:
        self.name = name
        self.status = status
        self.details = details or {}


class APIHealthManager:
    """Aggregates health status of all API layer components."""

    def __init__(self) -> None:
        self._components: dict[str, ComponentHealth] = {}

    def register_component(self, name: str, status: str = "healthy", details: dict[str, Any] | None = None) -> None:
        self._components[name] = ComponentHealth(name, status, details)
        logger.debug("health.component.registered", name=name, status=status)

    def update_status(self, name: str, status: str, details: dict[str, Any] | None = None) -> None:
        if name in self._components:
            self._components[name].status = status
            if details:
                self._components[name].details.update(details)
            logger.debug("health.component.updated", name=name, status=status)

    def get_health(self) -> dict[str, Any]:
        all_healthy = all(c.status == "healthy" for c in self._components.values())
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "components": {
                name: {"status": comp.status, "details": comp.details}
                for name, comp in self._components.items()
            },
            "component_count": len(self._components),
        }

    def get_component_health(self, name: str) -> dict[str, Any] | None:
        comp = self._components.get(name)
        if comp is None:
            return None
        return {"name": comp.name, "status": comp.status, "details": comp.details}

    def is_healthy(self) -> bool:
        return all(c.status == "healthy" for c in self._components.values())

    def count_unhealthy(self) -> int:
        return sum(1 for c in self._components.values() if c.status != "healthy")
