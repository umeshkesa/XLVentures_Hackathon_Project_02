"""ExecutionRecoveryReport — generates recovery operation reports.

Deterministic placeholder that summarises recovery operations
including retries, compensation, rollback, recovery duration,
and final status. Phase 3.5.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class RecoveryReport(BaseModel):
    """Report of recovery operations for an execution session."""

    report_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique report identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this report describes",
    )
    retries_performed: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts performed",
    )
    compensations_performed: int = Field(
        default=0,
        ge=0,
        description="Number of compensation actions performed",
    )
    rollbacks_performed: int = Field(
        default=0,
        ge=0,
        description="Number of rollback operations performed",
    )
    recovery_duration_ms: int = Field(
        default=0,
        ge=0,
        description="Total recovery duration in milliseconds",
    )
    final_status: str = Field(
        default="",
        description="Final status after recovery",
    )
    details: list[str] = Field(
        default_factory=list,
        description="Recovery operation details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the report was generated",
    )


class ExecutionRecoveryReport:
    """Generates recovery reports for execution sessions.

    Summarises retries, compensation, rollback, duration,
    and final status after recovery operations.
    """

    def __init__(self) -> None:
        self._reports: dict[str, RecoveryReport] = {}

    def generate(
        self,
        session_id: str,
        retries_performed: int = 0,
        compensations_performed: int = 0,
        rollbacks_performed: int = 0,
        recovery_duration_ms: int = 0,
        final_status: str = "COMPLETED",
        details: list[str] | None = None,
        correlation_id: str = "",
    ) -> RecoveryReport:
        """Generate a recovery report.

        Args:
            session_id: The session ID.
            retries_performed: Number of retries.
            compensations_performed: Number of compensations.
            rollbacks_performed: Number of rollbacks.
            recovery_duration_ms: Recovery duration in ms.
            final_status: Final status after recovery.
            details: Recovery operation details.
            correlation_id: Optional correlation ID.

        Returns:
            The generated RecoveryReport.
        """
        report = RecoveryReport(
            session_id=session_id,
            retries_performed=retries_performed,
            compensations_performed=compensations_performed,
            rollbacks_performed=rollbacks_performed,
            recovery_duration_ms=recovery_duration_ms,
            final_status=final_status,
            details=details or [],
        )
        self._reports[str(report.report_id)] = report
        log.info(
            "recovery_report.generated",
            session_id=session_id,
            retries=retries_performed,
            compensations=compensations_performed,
            status=final_status,
            cid=correlation_id,
        )
        return report

    def get_report(self, report_id: str) -> RecoveryReport | None:
        """Retrieve a recovery report by ID.

        Args:
            report_id: The report identifier.

        Returns:
            RecoveryReport if found, None otherwise.
        """
        return self._reports.get(report_id)

    def get_reports_for_session(self, session_id: str) -> list[RecoveryReport]:
        """Get all reports for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of RecoveryReport objects.
        """
        return [r for r in self._reports.values() if r.session_id == session_id]
