"""ReasoningSnapshot — captures immutable snapshots of reasoning state.

Creates and stores point-in-time snapshots of reasoning context,
graph, alternatives, confidence, risks, and impacts.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.reasoning.contracts.models import ReasoningConfidence, ReasoningContext
from adip.reasoning.execution.models import (
    ImpactAssessment,
    ReasoningAlternative,
    ReasoningGraph,
    ReasoningSnapshotModel,
    RiskAssessment,
)

log = structlog.get_logger(__name__)


class ReasoningSnapshot:
    """Captures immutable snapshots of reasoning state.

    Deterministic placeholder that creates point-in-time snapshots
    of reasoning context, graph, alternatives, confidence, risks,
    and impacts for audit and rollback purposes.
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, ReasoningSnapshotModel] = {}

    def create_snapshot(
        self,
        context: ReasoningContext | None = None,
        graph: ReasoningGraph | None = None,
        alternatives: list[ReasoningAlternative] | None = None,
        confidence: ReasoningConfidence | None = None,
        risks: dict[str, RiskAssessment] | None = None,
        impacts: dict[str, ImpactAssessment] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReasoningSnapshotModel:
        """Create an immutable snapshot of the current reasoning state.

        Args:
            context: Optional reasoning context.
            graph: Optional reasoning graph.
            alternatives: Optional list of alternatives.
            confidence: Optional confidence assessment.
            risks: Optional mapping of risk type to RiskAssessment.
            impacts: Optional mapping of impact type to ImpactAssessment.
            metadata: Optional additional metadata.

        Returns:
            A ReasoningSnapshotModel with the captured state.
        """
        ctx_data = context.model_dump() if context else None
        graph_data = graph.model_dump() if graph else None
        conf_data = confidence.model_dump() if confidence else None
        alt_data = [a.model_dump() for a in alternatives] if alternatives else []
        risk_data = {
            k: v.model_dump() for k, v in risks.items()
        } if risks else {}
        impact_data = {
            k: v.model_dump() for k, v in impacts.items()
        } if impacts else {}

        snapshot = ReasoningSnapshotModel(
            context=ctx_data,
            graph=graph_data,
            alternatives=alt_data,
            confidence=conf_data,
            risks=risk_data,
            impacts=impact_data,
            metadata=metadata or {},
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        log.info(
            "reasoning_snapshot.create",
            snapshot_id=snapshot.snapshot_id,
            has_context=context is not None,
            has_graph=graph is not None,
            alternatives_count=len(alt_data),
        )
        return snapshot

    def get_snapshot(
        self,
        snapshot_id: str,
    ) -> ReasoningSnapshotModel | None:
        """Retrieve a snapshot by its identifier.

        Args:
            snapshot_id: The snapshot identifier.

        Returns:
            The ReasoningSnapshotModel if found, else None.
        """
        return self._snapshots.get(snapshot_id)

    def get_all_snapshots(self) -> list[ReasoningSnapshotModel]:
        """Get all stored snapshots.

        Returns:
            List of all ReasoningSnapshotModel instances.
        """
        return list(self._snapshots.values())

    def clear(self) -> None:
        """Clear all stored snapshots."""
        self._snapshots.clear()

    def count(self) -> int:
        """Get the number of stored snapshots.

        Returns:
            Snapshot count.
        """
        return len(self._snapshots)
