"""AuditManager — records audit trail for memory operations.

Tracks Create, Read, Update, Delete, Archive, Restore, and lifecycle
transitions.  Each operation generates an AuditRecord.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.contracts.models import MemoryRecord
from adip.memory.enums import MemoryLifecycleStatus, MemoryOperation, MemoryTier, MemoryType
from adip.memory.execution.models import AuditRecord

log = structlog.get_logger(__name__)


class AuditManager:
    """Records and stores audit trail entries for memory operations."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def record(
        self,
        record: MemoryRecord,
        operation: MemoryOperation,
        tier: str = "",
        correlation_id: str = "",
        details: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Create an audit record from a MemoryRecord."""
        tier_enum: MemoryTier | None = None
        if tier:
            try:
                tier_enum = MemoryTier(tier)
            except ValueError:
                tier_enum = None
        audit = AuditRecord(
            memory_id=record.memory_id,
            memory_type=record.memory_type,
            operation=operation,
            tier=tier_enum,
            namespace=record.namespace,
            owner_id=record.owner_id,
            correlation_id=correlation_id,
            details=details or {},
        )
        self._records.append(audit)
        log.debug(
            "audit.record",
            memory_id=str(record.memory_id),
            operation=operation.value,
        )
        return audit

    def record_raw(
        self,
        memory_id: str,
        operation: MemoryOperation,
        memory_type: MemoryType | None = None,
        tier: str = "",
        correlation_id: str = "",
        details: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Create an audit record without a full MemoryRecord (e.g. for delete)."""
        import uuid
        tier_enum: MemoryTier | None = None
        if tier:
            try:
                tier_enum = MemoryTier(tier)
            except ValueError:
                tier_enum = None
        audit = AuditRecord(
            memory_id=uuid.UUID(memory_id) if isinstance(memory_id, str) else memory_id,
            memory_type=memory_type or MemoryType.CACHE,
            operation=operation,
            tier=tier_enum,
            correlation_id=correlation_id,
            details=details or {},
        )
        self._records.append(audit)
        return audit

    def record_lifecycle(
        self,
        record: MemoryRecord,
        old_status: MemoryLifecycleStatus,
        new_status: MemoryLifecycleStatus,
        reason: str = "",
        actor: str = "system",
    ) -> AuditRecord:
        """Record a lifecycle transition audit entry."""
        audit = AuditRecord(
            memory_id=record.memory_id,
            memory_type=record.memory_type,
            operation=MemoryOperation.UPDATE,
            namespace=record.namespace,
            owner_id=record.owner_id,
            details={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "reason": reason,
                "actor": actor,
            },
        )
        self._records.append(audit)
        return audit

    def get_records(
        self,
        memory_id: str | None = None,
        operation: MemoryOperation | None = None,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Retrieve audit records, optionally filtered."""
        results = list(self._records)
        if memory_id:
            target = str(memory_id)
            results = [r for r in results if str(r.memory_id) == target]
        if operation:
            results = [r for r in results if r.operation == operation]
        return results[-limit:]

    def clear(self) -> None:
        """Clear all audit records (for testing)."""
        self._records.clear()
