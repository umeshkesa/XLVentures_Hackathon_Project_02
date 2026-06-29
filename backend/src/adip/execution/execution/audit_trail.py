"""AuditTrail — stores execution events, checkpoints, retries, and rollbacks.

Provides an immutable audit trail for all execution operations,
recording events, checkpoints, retries, rollbacks, and other
significant state changes.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.execution.execution.models import AuditRecord

log = structlog.get_logger(__name__)


class AuditTrail:
    """Stores an immutable audit trail of execution events."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def record_event(
        self,
        session_id: str = "",
        event_type: str = "",
        task_id: str = "",
        description: str = "",
        details: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> AuditRecord:
        """Record an audit event.

        Args:
            session_id: The session ID.
            event_type: Type of event (task_started, task_completed, checkpoint, retry, rollback, etc.).
            task_id: The task ID related to this event.
            description: Description of the event.
            details: Additional event details.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created AuditRecord.
        """
        record = AuditRecord(
            session_id=session_id,
            event_type=event_type,
            task_id=task_id,
            description=description,
            details=details or {},
        )
        self._records.append(record)
        log.info(
            "audit_trail.recorded",
            event_type=event_type,
            session_id=session_id,
            task_id=task_id,
            correlation_id=correlation_id,
        )
        return record

    def record_checkpoint(
        self,
        session_id: str = "",
        checkpoint_id: str = "",
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> AuditRecord:
        """Record a checkpoint event.

        Args:
            session_id: The session ID.
            checkpoint_id: The checkpoint ID.
            task_ids: Task IDs included in the checkpoint.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created AuditRecord.
        """
        return self.record_event(
            session_id=session_id,
            event_type="checkpoint",
            description=f"Checkpoint {checkpoint_id} created",
            details={"checkpoint_id": checkpoint_id, "task_ids": task_ids or []},
            correlation_id=correlation_id,
        )

    def record_retry(
        self,
        session_id: str = "",
        task_id: str = "",
        attempt: int = 0,
        delay_seconds: int = 0,
        error: str = "",
        correlation_id: str = "",
    ) -> AuditRecord:
        """Record a retry event.

        Args:
            session_id: The session ID.
            task_id: The task ID.
            attempt: Retry attempt number.
            delay_seconds: Delay before retry.
            error: Error that triggered the retry.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created AuditRecord.
        """
        return self.record_event(
            session_id=session_id,
            event_type="retry",
            task_id=task_id,
            description=f"Retry attempt {attempt} for task {task_id}",
            details={
                "attempt": attempt,
                "delay_seconds": delay_seconds,
                "error": error,
            },
            correlation_id=correlation_id,
        )

    def record_rollback(
        self,
        session_id: str = "",
        task_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> AuditRecord:
        """Record a rollback event.

        Args:
            session_id: The session ID.
            task_id: The task ID.
            reason: Reason for rollback.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created AuditRecord.
        """
        return self.record_event(
            session_id=session_id,
            event_type="rollback",
            task_id=task_id,
            description=f"Rollback for task {task_id}",
            details={"reason": reason},
            correlation_id=correlation_id,
        )

    def record_compensation(
        self,
        session_id: str = "",
        task_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> AuditRecord:
        """Record a compensation event.

        Args:
            session_id: The session ID.
            task_id: The task ID.
            reason: Reason for compensation.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created AuditRecord.
        """
        return self.record_event(
            session_id=session_id,
            event_type="compensation",
            task_id=task_id,
            description=f"Compensation for task {task_id}",
            details={"reason": reason},
            correlation_id=correlation_id,
        )

    def get_records(
        self,
        session_id: str | None = None,
        event_type: str | None = None,
        task_id: str | None = None,
    ) -> list[AuditRecord]:
        """Get audit records with optional filtering.

        Args:
            session_id: Optional session ID filter.
            event_type: Optional event type filter.
            task_id: Optional task ID filter.

        Returns:
            Filtered list of AuditRecord.
        """
        records = self._records
        if session_id:
            records = [r for r in records if r.session_id == session_id]
        if event_type:
            records = [r for r in records if r.event_type == event_type]
        if task_id:
            records = [r for r in records if r.task_id == task_id]
        return records

    def get_all_records(self) -> list[AuditRecord]:
        """Get all audit records."""
        return list(self._records)

    def clear(self) -> None:
        """Clear all audit records."""
        self._records.clear()
