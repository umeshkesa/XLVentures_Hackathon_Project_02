"""APIExportPackage — supports export of OpenAPI metadata, route manifest, version manifest, middleware manifest, contract manifest.

Phase 3.5 documentation readiness.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

from adip.api.rest.enums import ExportFormat

logger = structlog.get_logger(__name__)


class ExportPackage:
    """An immutable export package containing API metadata manifests."""

    def __init__(self) -> None:
        self.package_id: UUID = uuid4()
        self.created_at: datetime = datetime.now(UTC)
        self.openapi_metadata: dict[str, Any] = {}
        self.route_manifest: list[dict[str, Any]] = []
        self.version_manifest: list[dict[str, Any]] = []
        self.middleware_manifest: list[dict[str, Any]] = []
        self.contract_manifest: list[dict[str, Any]] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": str(self.package_id),
            "created_at": self.created_at.isoformat(),
            "openapi_metadata": self.openapi_metadata,
            "route_manifest": self.route_manifest,
            "version_manifest": self.version_manifest,
            "middleware_manifest": self.middleware_manifest,
            "contract_manifest": self.contract_manifest,
        }


class APIExportPackage:
    """Creates and manages export packages for API documentation and metadata."""

    def __init__(self) -> None:
        self._packages: dict[str, ExportPackage] = {}

    def create_package(
        self,
        openapi_metadata: dict[str, Any] | None = None,
        route_manifest: list[dict[str, Any]] | None = None,
        version_manifest: list[dict[str, Any]] | None = None,
        middleware_manifest: list[dict[str, Any]] | None = None,
        contract_manifest: dict[str, Any] | None = None,
    ) -> ExportPackage:
        package = ExportPackage()
        package.openapi_metadata = openapi_metadata or {}
        package.route_manifest = route_manifest or []
        package.version_manifest = version_manifest or []
        package.middleware_manifest = middleware_manifest or []
        package.contract_manifest = contract_manifest or {}
        self._packages[str(package.package_id)] = package
        logger.info("export_package.created", package_id=str(package.package_id))
        return package

    def get_package(self, package_id: str) -> ExportPackage | None:
        return self._packages.get(package_id)

    def list_packages(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._packages.values()]

    def export_as(self, package_id: str, fmt: ExportFormat = ExportFormat.JSON) -> str:
        package = self._packages.get(package_id)
        if package is None:
            return ""
        if fmt == ExportFormat.MARKDOWN:
            return self._to_markdown(package)
        return self._to_json(package)

    def _to_json(self, package: ExportPackage) -> str:
        import json
        return json.dumps(package.to_dict(), indent=2, default=str)

    def _to_markdown(self, package: ExportPackage) -> str:
        lines = ["# API Export Package", "", f"**Package ID:** {package.package_id}", f"**Created:** {package.created_at.isoformat()}", ""]
        if package.route_manifest:
            lines.append("## Routes")
            for route in package.route_manifest:
                method = route.get("method", "GET")
                path = route.get("path", "/")
                desc = route.get("description", "")
                lines.append(f"- `{method} {path}` — {desc}")
            lines.append("")
        if package.version_manifest:
            lines.append("## Versions")
            for ver in package.version_manifest:
                lines.append(f"- {ver.get('version', '?')}: {ver.get('status', 'unknown')}")
            lines.append("")
        if package.middleware_manifest:
            lines.append("## Middleware")
            for mw in package.middleware_manifest:
                lines.append(f"- {mw.get('name', '?')} ({mw.get('status', 'unknown')})")
            lines.append("")
        return "\n".join(lines)

    def count(self) -> int:
        return len(self._packages)

    def clear(self) -> None:
        self._packages.clear()
