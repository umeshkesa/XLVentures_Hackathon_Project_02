"""ExecutionSnapshot — creates immutable snapshots of execution state.

Deterministic placeholder that captures point-in-time snapshots
of execution sessions for audit, comparison, and rollback purposes.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ExecutionSnapshotRecord(BaseModel):
    """An immutable snapshot of execution state at a point in time."""

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this snapshot captures",
    )
    request_id: str = Field(
        default="",
        description="The request ID at snapshot time",
    )
    decision_id: str = Field(
        default="",
        description="The decision ID at snapshot time",
    )
    package_id: str = Field(
        default="",
        description="The package ID at snapshot time",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Package version at snapshot time",
    )
    task_count: int = Field(
        default=0,
        ge=0,
        description="Number of tasks at snapshot time",
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Completed tasks at snapshot time",
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Failed tasks at snapshot time",
    )
    readiness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Readiness score at snapshot time",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score at snapshot time",
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score at snapshot time",
    )
    snapshot_type: str = Field(
        default="session",
        description="Type of snapshot (session, readiness, quality, confidence)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional snapshot metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )


class ExecutionSnapshot:
    """Creates immutable snapshots of execution state.

    Provides point-in-time captures for audit, comparison,
    and rollback scenarios.
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, ExecutionSnapshotRecord] = {}

    def create_snapshot(
        self,
        session_id: str,
        request_id: str = "",
        decision_id: str = "",
        package_id: str = "",
        task_count: int = 0,
        tasks_completed: int = 0,
        tasks_failed: int = 0,
        readiness_score: float = 0.0,
        quality_score: float = 0.0,
        confidence_score: float = 0.0,
        snapshot_type: str = "session",
        correlation_id: str = "",
    ) -> ExecutionSnapshotRecord:
        """Create an immutable snapshot.

        Args:
            session_id: The session ID to capture.
            request_id: The request ID.
            decision_id: The decision ID.
            package_id: The package ID.
            task_count: Number of tasks.
            tasks_completed: Completed tasks count.
            tasks_failed: Failed tasks count.
            readiness_score: Readiness score.
            quality_score: Quality score.
            confidence_score: Confidence score.
            snapshot_type: Type of snapshot.
            correlation_id: Optional correlation ID.

        Returns:
            The created ExecutionSnapshotRecord.
        """
        record = ExecutionSnapshotRecord(
            session_id=session_id,
            request_id=request_id,
            decision_id=decision_id,
            package_id=package_id,
            task_count=task_count,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            readiness_score=readiness_score,
            quality_score=quality_score,
            confidence_score=confidence_score,
            snapshot_type=snapshot_type,
        )
        self._snapshots[str(record.snapshot_id)] = record

        version_record = self._get_version(package_id or session_id)
        if version_record is not None:
            record.version = version_record

        log.info(
            "snapshot.created",
            session_id=session_id,
            snapshot_type=snapshot_type,
            snapshot_id=str(record.snapshot_id),
            cid=correlation_id,
        )
        return record

    def _get_version(self, entity_id: str) -> int:
        """Get version count for an entity.

        Args:
            entity_id: The entity identifier.

        Returns:
            Version count (snapshots count + 1).
        """
        count = sum(
            1 for s in self._snapshots.values()
            if s.session_id == entity_id or s.package_id == entity_id
        )
        return count + 1

    def get_snapshot(self, snapshot_id: str) -> ExecutionSnapshotRecord | None:
        """Retrieve a snapshot by ID.

        Args:
            snapshot_id: The snapshot identifier.

        Returns:
            ExecutionSnapshotRecord if found, None otherwise.
        """
        return self._snapshots.get(snapshot_id)

    def create_compliance_snapshot(
        self,
        session_id: str,
        request_id: str = "",
        compliance_status: str = "compliant",
        violations: int = 0,
        checks_passed: int = 0,
        checks_failed: int = 0,
        quality_score: float = 0.0,
        confidence_score: float = 0.0,
        correlation_id: str = "",
    ) -> ExecutionSnapshotRecord:
        """Create a compliance snapshot (Phase 3.5).

        Args:
            session_id: The session ID to capture.
            request_id: The request ID.
            compliance_status: Compliance status.
            violations: Number of violations.
            checks_passed: Number of checks passed.
            checks_failed: Number of checks failed.
            quality_score: Quality score.
            confidence_score: Confidence score.
            correlation_id: Optional correlation ID.

        Returns:
            The created ExecutionSnapshotRecord.
        """
        record = ExecutionSnapshotRecord(
            session_id=session_id,
            request_id=request_id,
            snapshot_type="compliance",
            quality_score=quality_score,
            confidence_score=confidence_score,
            metadata={
                "compliance_status": compliance_status,
                "violations": violations,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
            },
        )
        self._snapshots[str(record.snapshot_id)] = record
        log.info(
            "snapshot.compliance",
            session_id=session_id,
            compliance_status=compliance_status,
            cid=correlation_id,
        )
        return record

    def create_export_snapshot(
        self,
        session_id: str,
        request_id: str = "",
        export_type: str = "rest",
        task_count: int = 0,
        tasks_completed: int = 0,
        tasks_failed: int = 0,
        duration_ms: int = 0,
        quality_score: float = 0.0,
        confidence_score: float = 0.0,
        correlation_id: str = "",
    ) -> ExecutionSnapshotRecord:
        """Create an export snapshot (Phase 3.5).

        Args:
            session_id: The session ID to capture.
            request_id: The request ID.
            export_type: Type of export.
            task_count: Number of tasks.
            tasks_completed: Completed tasks count.
            tasks_failed: Failed tasks count.
            duration_ms: Duration in ms.
            quality_score: Quality score.
            confidence_score: Confidence score.
            correlation_id: Optional correlation ID.

        Returns:
            The created ExecutionSnapshotRecord.
        """
        record = ExecutionSnapshotRecord(
            session_id=session_id,
            request_id=request_id,
            snapshot_type=f"export.{export_type}",
            task_count=task_count,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            quality_score=quality_score,
            confidence_score=confidence_score,
            metadata={
                "export_type": export_type,
                "duration_ms": duration_ms,
            },
        )
        self._snapshots[str(record.snapshot_id)] = record
        log.info(
            "snapshot.export",
            session_id=session_id,
            export_type=export_type,
            cid=correlation_id,
        )
        return record

    def get_snapshots_for_session(
        self,
        session_id: str,
    ) -> list[ExecutionSnapshotRecord]:
        """Get all snapshots for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of ExecutionSnapshotRecord in chronological order.
        """
        return sorted(
            [
                s for s in self._snapshots.values()
                if s.session_id == session_id
            ],
            key=lambda s: s.timestamp,
        )
