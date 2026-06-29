"""APIAuditPackage — creates immutable audit packages for API requests."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class AuditPackage:
    """An immutable audit package containing request/response data."""

    def __init__(self) -> None:
        self.audit_id: UUID = uuid4()
        self.created_at: datetime = datetime.now(UTC)
        self.request_data: dict[str, Any] = {}
        self.response_data: dict[str, Any] = {}
        self.headers: dict[str, str] = {}
        self.metadata: dict[str, Any] = {}
        self.trace_data: dict[str, Any] = {}
        self.hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": str(self.audit_id),
            "created_at": self.created_at.isoformat(),
            "request": self.request_data,
            "response": self.response_data,
            "headers": self.headers,
            "metadata": self.metadata,
            "trace": self.trace_data,
            "hash": self.hash,
        }


class APIAuditPackage:
    """Creates immutable audit packages for API requests."""

    def __init__(self) -> None:
        self._packages: dict[str, AuditPackage] = {}

    def create_package(
        self,
        request_data: dict[str, Any] | None = None,
        response_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
        trace_data: dict[str, Any] | None = None,
    ) -> AuditPackage:
        package = AuditPackage()
        package.request_data = request_data or {}
        package.response_data = response_data or {}
        package.headers = headers or {}
        package.metadata = metadata or {}
        package.trace_data = trace_data or {}
        package.hash = self._compute_hash(package)
        self._packages[str(package.audit_id)] = package
        logger.info("audit_package.created", audit_id=str(package.audit_id))
        return package

    def get_package(self, audit_id: str) -> AuditPackage | None:
        return self._packages.get(audit_id)

    def verify_package(self, audit_id: str) -> bool:
        package = self._packages.get(audit_id)
        if package is None:
            return False
        return package.hash == self._compute_hash(package)

    def list_packages(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._packages.values()]

    def _compute_hash(self, package: AuditPackage) -> str:
        content = {
            "audit_id": str(package.audit_id),
            "created_at": package.created_at.isoformat(),
            "request": package.request_data,
            "response": package.response_data,
            "headers": package.headers,
            "metadata": package.metadata,
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()

    def count(self) -> int:
        return len(self._packages)

    def clear(self) -> None:
        self._packages.clear()
