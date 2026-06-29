"""APIManifest — creates immutable manifests containing routes, middleware, adapters, contracts, and versions.

Phase 3.5 documentation readiness.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class APIManifest:
    """Creates immutable API manifests containing routes, middleware, adapters, contracts, and versions."""

    def __init__(self) -> None:
        self._manifest_id: UUID = uuid4()
        self._created_at: datetime = datetime.now(UTC)
        self._routes: list[dict[str, Any]] = []
        self._middleware: list[dict[str, Any]] = []
        self._adapters: list[dict[str, Any]] = []
        self._contracts: list[dict[str, Any]] = []
        self._versions: list[dict[str, Any]] = []

    def add_route(self, method: str, path: str, description: str = "", tags: list[str] | None = None) -> None:
        self._routes.append({
            "method": method.upper(),
            "path": path,
            "description": description,
            "tags": tags or [],
        })

    def add_middleware(self, name: str, enabled: bool = True, priority: int = 0) -> None:
        self._middleware.append({
            "name": name,
            "enabled": enabled,
            "priority": priority,
        })

    def add_adapter(self, domain: str, operations: list[str] | None = None) -> None:
        self._adapters.append({
            "domain": domain,
            "operations": operations or [],
        })

    def add_contract(self, name: str, version: str = "1.0.0", fields: list[str] | None = None) -> None:
        self._contracts.append({
            "name": name,
            "version": version,
            "fields": fields or [],
        })

    def add_version(self, version: str, status: str = "active", description: str = "") -> None:
        self._versions.append({
            "version": version,
            "status": status,
            "description": description,
        })

    def build(self) -> dict[str, Any]:
        return {
            "manifest_id": str(self._manifest_id),
            "created_at": self._created_at.isoformat(),
            "routes": list(self._routes),
            "middleware": list(self._middleware),
            "adapters": list(self._adapters),
            "contracts": list(self._contracts),
            "versions": list(self._versions),
            "route_count": len(self._routes),
            "middleware_count": len(self._middleware),
            "adapter_count": len(self._adapters),
            "contract_count": len(self._contracts),
            "version_count": len(self._versions),
        }

    def reset(self) -> None:
        self._manifest_id = uuid4()
        self._created_at = datetime.now(UTC)
        self._routes.clear()
        self._middleware.clear()
        self._adapters.clear()
        self._contracts.clear()
        self._versions.clear()
