"""DocumentationMetadata — prepares metadata for Swagger, Redoc, OpenAPI, route inventory, and service inventory.

Phase 3.5 documentation readiness.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class DocumentationMetadata:
    """Prepares and stores documentation metadata for API exports."""

    def __init__(self) -> None:
        self.metadata_id: UUID = uuid4()
        self.created_at: datetime = datetime.now(UTC)
        self.swagger_metadata: dict[str, Any] = {}
        self.redoc_metadata: dict[str, Any] = {}
        self.openapi_metadata: dict[str, Any] = {}
        self.route_inventory: list[dict[str, Any]] = []
        self.service_inventory: list[dict[str, Any]] = []

    def set_swagger_metadata(self, title: str = "ADIP REST API", version: str = "1.0.0", description: str = "") -> None:
        self.swagger_metadata = {
            "title": title,
            "version": version,
            "description": description,
            "ui_url": "/docs",
        }

    def set_redoc_metadata(self, title: str = "ADIP REST API", version: str = "1.0.0", description: str = "") -> None:
        self.redoc_metadata = {
            "title": title,
            "version": version,
            "description": description,
            "ui_url": "/redoc",
        }

    def set_openapi_metadata(self, spec_version: str = "3.1.0", info: dict[str, Any] | None = None) -> None:
        self.openapi_metadata = {
            "spec_version": spec_version,
            "info": info or {},
        }

    def add_route(self, method: str, path: str, summary: str = "", tags: list[str] | None = None) -> None:
        self.route_inventory.append({
            "method": method.upper(),
            "path": path,
            "summary": summary,
            "tags": tags or [],
        })

    def add_service(self, name: str, domain: str, operations: list[str] | None = None, description: str = "") -> None:
        self.service_inventory.append({
            "name": name,
            "domain": domain,
            "operations": operations or [],
            "description": description,
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata_id": str(self.metadata_id),
            "created_at": self.created_at.isoformat(),
            "swagger": self.swagger_metadata,
            "redoc": self.redoc_metadata,
            "openapi": self.openapi_metadata,
            "route_inventory": self.route_inventory,
            "service_inventory": self.service_inventory,
            "route_count": len(self.route_inventory),
            "service_count": len(self.service_inventory),
        }

    def reset(self) -> None:
        self.metadata_id = uuid4()
        self.created_at = datetime.now(UTC)
        self.swagger_metadata = {}
        self.redoc_metadata = {}
        self.openapi_metadata = {}
        self.route_inventory.clear()
        self.service_inventory.clear()
