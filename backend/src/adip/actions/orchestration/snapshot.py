"""ActionSnapshot — creates immutable snapshots of action plans.

Deterministic placeholder that captures point-in-time snapshots
of action plans for audit, comparison, and rollback purposes.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ActionSnapshotRecord(BaseModel):
    """An immutable snapshot of an action plan at a point in time."""

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this snapshot captures",
    )
    request_id: str = Field(
        default="",
        description="The request ID at snapshot time",
    )
    decision_id: str = Field(
        default="",
        description="The decision ID at snapshot time",
    )
    session_id: str = Field(
        default="",
        description="The session ID at snapshot time",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Plan version at snapshot time",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Number of steps at snapshot time",
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
        default="plan",
        description="Type of snapshot (plan, readiness, quality, confidence)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional snapshot metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )


class ActionSnapshot:
    """Creates immutable snapshots of action plans.

    Provides point-in-time captures for audit, comparison,
    and rollback scenarios.
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, ActionSnapshotRecord] = {}

    def create_snapshot(
        self,
        plan_id: str,
        request_id: str = "",
        decision_id: str = "",
        session_id: str = "",
        version: int = 1,
        step_count: int = 0,
        readiness_score: float = 0.0,
        quality_score: float = 0.0,
        confidence_score: float = 0.0,
        snapshot_type: str = "plan",
        correlation_id: str = "",
    ) -> ActionSnapshotRecord:
        """Create a snapshot of an action plan.

        Args:
            plan_id: The plan ID.
            request_id: The request ID.
            decision_id: The decision ID.
            session_id: The session ID.
            version: Plan version number.
            step_count: Number of steps.
            readiness_score: Readiness score.
            quality_score: Quality score.
            confidence_score: Confidence score.
            snapshot_type: Type of snapshot.
            correlation_id: Optional correlation ID.

        Returns:
            The created ActionSnapshotRecord.
        """
        snapshot = ActionSnapshotRecord(
            plan_id=plan_id,
            request_id=request_id,
            decision_id=decision_id,
            session_id=session_id,
            version=version,
            step_count=step_count,
            readiness_score=round(readiness_score, 4),
            quality_score=round(quality_score, 4),
            confidence_score=round(confidence_score, 4),
            snapshot_type=snapshot_type,
        )
        self._snapshots[str(snapshot.snapshot_id)] = snapshot
        log.info(
            "snapshot.created",
            plan_id=plan_id,
            snapshot_type=snapshot_type,
        )
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> ActionSnapshotRecord | None:
        """Retrieve a snapshot by ID.

        Args:
            snapshot_id: The snapshot identifier.

        Returns:
            ActionSnapshotRecord if found, None otherwise.
        """
        return self._snapshots.get(snapshot_id)

    def get_snapshots_for_plan(self, plan_id: str) -> list[ActionSnapshotRecord]:
        """Get all snapshots for a plan.

        Args:
            plan_id: The plan ID.

        Returns:
            List of ActionSnapshotRecords.
        """
        return [
            s for s in self._snapshots.values()
            if s.plan_id == plan_id
        ]

    def clear(self) -> None:
        """Clear all snapshots."""
        self._snapshots.clear()
