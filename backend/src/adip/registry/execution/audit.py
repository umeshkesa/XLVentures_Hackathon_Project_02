"""RegistryAudit — tracks registry operations for compliance.

Records registration, update, removal, activation, and deprecation
operations as placeholder audit records.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import RegistryEntry
from adip.registry.execution.models import AuditRecord

log = structlog.get_logger(__name__)


class RegistryAudit:
    """Tracks registry operations for compliance and observability.

    Each operation creates an immutable AuditRecord stored in memory.
    """

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def record_registration(self, entry: RegistryEntry, performed_by: str = "", details: dict | None = None) -> AuditRecord:
        """Record an entry registration."""
        log.info("registry_audit.registration", entry_id=str(entry.entry_id), name=entry.name)
        record = AuditRecord(
            entry_id=entry.entry_id,
            entry_name=entry.name,
            operation="register",
            previous_status="",
            new_status=entry.status.value,
            performed_by=performed_by,
            namespace=entry.namespace,
            details=details or {},
        )
        self._records.append(record)
        return record

    def record_update(self, entry: RegistryEntry, performed_by: str = "", details: dict | None = None) -> AuditRecord:
        """Record an entry update."""
        log.info("registry_audit.update", entry_id=str(entry.entry_id), name=entry.name)
        record = AuditRecord(
            entry_id=entry.entry_id,
            entry_name=entry.name,
            operation="update",
            previous_status="",
            new_status=entry.status.value,
            performed_by=performed_by,
            namespace=entry.namespace,
            details=details or {},
        )
        self._records.append(record)
        return record

    def record_removal(self, entry: RegistryEntry, performed_by: str = "", reason: str = "") -> AuditRecord:
        """Record an entry removal."""
        log.info("registry_audit.removal", entry_id=str(entry.entry_id), name=entry.name)
        record = AuditRecord(
            entry_id=entry.entry_id,
            entry_name=entry.name,
            operation="remove",
            previous_status=entry.status.value,
            new_status="REMOVED",
            performed_by=performed_by,
            namespace=entry.namespace,
            details={"reason": reason},
        )
        self._records.append(record)
        return record

    def record_activation(self, entry: RegistryEntry, performed_by: str = "") -> AuditRecord:
        """Record an entry activation."""
        log.info("registry_audit.activation", entry_id=str(entry.entry_id), name=entry.name)
        record = AuditRecord(
            entry_id=entry.entry_id,
            entry_name=entry.name,
            operation="activate",
            previous_status="VALIDATED",
            new_status=entry.status.value,
            performed_by=performed_by,
            namespace=entry.namespace,
        )
        self._records.append(record)
        return record

    def record_deprecation(self, entry: RegistryEntry, performed_by: str = "", reason: str = "") -> AuditRecord:
        """Record an entry deprecation."""
        log.info("registry_audit.deprecation", entry_id=str(entry.entry_id), name=entry.name)
        record = AuditRecord(
            entry_id=entry.entry_id,
            entry_name=entry.name,
            operation="deprecate",
            previous_status=entry.status.value,
            new_status="DEPRECATED",
            performed_by=performed_by,
            namespace=entry.namespace,
            details={"reason": reason},
        )
        self._records.append(record)
        return record

    def get_records(self, entry_id: str = "") -> list[AuditRecord]:
        """Get audit records, optionally filtered by entry ID."""
        if entry_id:
            return [r for r in self._records if str(r.entry_id) == entry_id]
        return list(self._records)

    def clear(self) -> int:
        """Clear all audit records. Returns count of records cleared."""
        count = len(self._records)
        self._records.clear()
        return count
