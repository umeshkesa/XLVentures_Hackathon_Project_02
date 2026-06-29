"""RecommendationSnapshot — creates immutable recommendation snapshots.

Captures point-in-time snapshots of portfolios, confidence,
business scores, costs, and timelines.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

log = structlog.get_logger(__name__)


class SnapshotRecord(BaseModel):
    """A snapshot record of recommendation state.

    Attributes:
        snapshot_id: Unique snapshot identifier.
        recommendation_id: The recommendation this snapshot belongs to.
        snapshot_type: The type of snapshot (portfolio, confidence, score, cost, timeline).
        data: The snapshot data.
        description: Description of this snapshot.
        created_at: When the snapshot was taken.
    """
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_id: str = Field(default="")
    snapshot_type: str = Field(default="")
    data: dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RecommendationSnapshot:
    """Creates immutable snapshots of recommendation state.

    Deterministic placeholder that captures point-in-time state
    of portfolios, confidence, business scores, costs, and timelines.
    """

    def __init__(self) -> None:
        self._snapshots: list[SnapshotRecord] = []

    def create_snapshot(
        self,
        recommendation_id: str = "",
        snapshot_type: str = "",
        data: dict[str, Any] | None = None,
        description: str = "",
    ) -> SnapshotRecord:
        """Create an immutable snapshot.

        Args:
            recommendation_id: The recommendation identifier.
            snapshot_type: The snapshot type (portfolio, confidence, score, cost, timeline).
            data: The data to capture.
            description: Description of this snapshot.

        Returns:
            The created SnapshotRecord.
        """
        record = SnapshotRecord(
            recommendation_id=recommendation_id,
            snapshot_type=snapshot_type,
            data=data or {},
            description=description,
        )
        self._snapshots.append(record)
        log.info("snapshot.created", type=snapshot_type, recommendation_id=recommendation_id)
        return record

    def create_quality_snapshot(
        self,
        recommendation_id: str = "",
        quality_result=None,
    ) -> SnapshotRecord:
        """Create a snapshot of a quality assessment.

        Args:
            recommendation_id: The recommendation identifier.
            quality_result: The quality result to snapshot.

        Returns:
            SnapshotRecord.
        """
        data = {}
        if quality_result:
            data = {
                "portfolio_completeness": getattr(quality_result, 'portfolio_completeness', 0.0),
                "business_coverage": getattr(quality_result, 'business_coverage', 0.0),
                "feasibility_coverage": getattr(quality_result, 'feasibility_coverage', 0.0),
                "policy_compliance": getattr(quality_result, 'policy_compliance', 0.0),
                "outcome_coverage": getattr(quality_result, 'outcome_coverage', 0.0),
                "overall_quality": getattr(quality_result, 'overall_quality', 0.0),
            }
        return self.create_snapshot(
            recommendation_id=recommendation_id,
            snapshot_type="quality",
            data=data,
            description="Quality assessment snapshot",
        )

    def create_approval_snapshot(
        self,
        recommendation_id: str = "",
        approval_result=None,
    ) -> SnapshotRecord:
        """Create a snapshot of an approval readiness assessment.

        Args:
            recommendation_id: The recommendation identifier.
            approval_result: The approval readiness result to snapshot.

        Returns:
            SnapshotRecord.
        """
        data = {}
        if approval_result:
            data = {
                "status": getattr(approval_result, 'status', ''),
                "confidence_adequate": getattr(approval_result, 'confidence_adequate', False),
                "feasibility_adequate": getattr(approval_result, 'feasibility_adequate', False),
                "policy_passed": getattr(approval_result, 'policy_passed', True),
                "review_passed": getattr(approval_result, 'review_passed', True),
                "quality_adequate": getattr(approval_result, 'quality_adequate', False),
                "reasons": getattr(approval_result, 'reasons', []),
            }
        return self.create_snapshot(
            recommendation_id=recommendation_id,
            snapshot_type="approval",
            data=data,
            description="Approval readiness snapshot",
        )

    def create_portfolio_snapshot(
        self,
        recommendation_id: str = "",
        portfolio=None,
    ) -> SnapshotRecord:
        """Create a snapshot of a portfolio.

        Args:
            recommendation_id: The recommendation identifier.
            portfolio: The portfolio to snapshot.

        Returns:
            SnapshotRecord.
        """
        data = {}
        if portfolio:
            data = {
                "portfolio_id": getattr(portfolio, 'portfolio_id', ''),
                "primary_recommendation_id": getattr(portfolio, 'primary_recommendation_id', ''),
                "alternative_ids": getattr(portfolio, 'alternative_ids', []),
                "overall_confidence": getattr(portfolio, 'overall_confidence', 0.0),
            }
        return self.create_snapshot(
            recommendation_id=recommendation_id,
            snapshot_type="portfolio",
            data=data,
            description="Portfolio state snapshot",
        )

    def get_by_recommendation(self, recommendation_id: str) -> list[SnapshotRecord]:
        """Get all snapshots for a recommendation.

        Args:
            recommendation_id: The recommendation identifier.

        Returns:
            List of SnapshotRecord.
        """
        return [s for s in self._snapshots if s.recommendation_id == recommendation_id]

    def get_by_type(self, snapshot_type: str) -> list[SnapshotRecord]:
        """Get all snapshots of a type.

        Args:
            snapshot_type: The snapshot type.

        Returns:
            List of SnapshotRecord.
        """
        return [s for s in self._snapshots if s.snapshot_type == snapshot_type]

    def get_all(self) -> list[SnapshotRecord]:
        """Get all snapshots."""
        return list(self._snapshots)

    def clear(self) -> None:
        """Clear all snapshots."""
        self._snapshots.clear()

    def count(self) -> int:
        """Get the number of snapshots."""
        return len(self._snapshots)
