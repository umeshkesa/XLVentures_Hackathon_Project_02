"""APIDiagnostics — collects and tracks failures across the API pipeline.

Tracks:
- Router Failures
- Middleware Failures
- Validation Errors
- Adapter Failures
- Contract Violations
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class DiagnosticEntry:
    """A single diagnostic event."""

    def __init__(self, category: str, source: str, message: str, details: dict[str, Any] | None = None) -> None:
        self.diagnostic_id: UUID = uuid4()
        self.timestamp: datetime = datetime.now(UTC)
        self.category: str = category
        self.source: str = source
        self.message: str = message
        self.details: dict[str, Any] = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagnostic_id": str(self.diagnostic_id),
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "source": self.source,
            "message": self.message,
            "details": self.details,
        }


class APIDiagnostics:
    """Collects diagnostic events across the API pipeline.

    Categories: router, middleware, validation, adapter, contract.
    """

    CATEGORY_ROUTER = "router"
    CATEGORY_MIDDLEWARE = "middleware"
    CATEGORY_VALIDATION = "validation"
    CATEGORY_ADAPTER = "adapter"
    CATEGORY_CONTRACT = "contract"

    def __init__(self) -> None:
        self._entries: dict[str, DiagnosticEntry] = {}

    def record_router_failure(self, route: str, method: str, message: str, details: dict[str, Any] | None = None) -> DiagnosticEntry:
        entry = DiagnosticEntry(self.CATEGORY_ROUTER, f"{method} {route}", message, details)
        self._entries[str(entry.diagnostic_id)] = entry
        logger.warning("diagnostics.router_failure", route=route, method=method, message=message)
        return entry

    def record_middleware_failure(self, middleware_name: str, message: str, details: dict[str, Any] | None = None) -> DiagnosticEntry:
        entry = DiagnosticEntry(self.CATEGORY_MIDDLEWARE, middleware_name, message, details)
        self._entries[str(entry.diagnostic_id)] = entry
        logger.warning("diagnostics.middleware_failure", middleware=middleware_name, message=message)
        return entry

    def record_validation_error(self, validator: str, message: str, details: dict[str, Any] | None = None) -> DiagnosticEntry:
        entry = DiagnosticEntry(self.CATEGORY_VALIDATION, validator, message, details)
        self._entries[str(entry.diagnostic_id)] = entry
        logger.warning("diagnostics.validation_error", validator=validator, message=message)
        return entry

    def record_adapter_failure(self, adapter_name: str, operation: str, message: str, details: dict[str, Any] | None = None) -> DiagnosticEntry:
        entry = DiagnosticEntry(self.CATEGORY_ADAPTER, f"{adapter_name}.{operation}", message, details)
        self._entries[str(entry.diagnostic_id)] = entry
        logger.warning("diagnostics.adapter_failure", adapter=adapter_name, operation=operation, message=message)
        return entry

    def record_contract_violation(self, source: str, message: str, details: dict[str, Any] | None = None) -> DiagnosticEntry:
        entry = DiagnosticEntry(self.CATEGORY_CONTRACT, source, message, details)
        self._entries[str(entry.diagnostic_id)] = entry
        logger.warning("diagnostics.contract_violation", source=source, message=message)
        return entry

    def get_diagnostics(self) -> dict[str, Any]:
        by_category: dict[str, list[dict[str, Any]]] = {}
        for entry in self._entries.values():
            by_category.setdefault(entry.category, []).append(entry.to_dict())
        return {
            "total_entries": len(self._entries),
            "by_category": by_category,
            "router_failures": sum(1 for e in self._entries.values() if e.category == self.CATEGORY_ROUTER),
            "middleware_failures": sum(1 for e in self._entries.values() if e.category == self.CATEGORY_MIDDLEWARE),
            "validation_errors": sum(1 for e in self._entries.values() if e.category == self.CATEGORY_VALIDATION),
            "adapter_failures": sum(1 for e in self._entries.values() if e.category == self.CATEGORY_ADAPTER),
            "contract_violations": sum(1 for e in self._entries.values() if e.category == self.CATEGORY_CONTRACT),
        }

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()
