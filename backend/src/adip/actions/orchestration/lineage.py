"""ActionLineage — tracks decision lineage for action plans.

Deterministic placeholder that maintains a provenance chain
from review decision through planning, optimisation, and
execution packaging. Provides traceability for audit and
governance.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ActionLineageRecord(BaseModel):
    """A lineage record in the action planning chain."""

    lineage_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique lineage identifier",
    )
    request_id: str = Field(
        default="",
        description="The request ID this lineage tracks",
    )
    plan_id: str | None = Field(
        default=None,
        description="The plan ID in this lineage",
    )
    decision_id: str | None = Field(
        default=None,
        description="The decision ID in this lineage",
    )
    session_id: str | None = Field(
        default=None,
        description="The session ID in this lineage",
    )
    parent_lineage_id: str | None = Field(
        default=None,
        description="Parent lineage record ID",
    )
    stage: str = Field(
        default="",
        description="The pipeline stage that created this record",
    )
    summary: str = Field(
        default="",
        description="Summary of what happened at this stage",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional lineage metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the lineage record was created",
    )


class ActionLineage:
    """Tracks decision lineage for action planning.

    Maintains a sequence of lineage records tracing the
    provenance of action plans from review decision through
    to execution package.
    """

    def __init__(self) -> None:
        self._lineage: dict[str, ActionLineageRecord] = {}

    def record(
        self,
        request_id: str,
        plan_id: str | None = None,
        decision_id: str | None = None,
        session_id: str | None = None,
        parent_lineage_id: str | None = None,
        stage: str = "",
        summary: str = "",
        correlation_id: str = "",
    ) -> ActionLineageRecord:
        """Record a lineage entry.

        Args:
            request_id: The request ID.
            plan_id: Optional plan ID.
            decision_id: Optional decision ID.
            session_id: Optional session ID.
            parent_lineage_id: Optional parent lineage ID.
            stage: The pipeline stage name.
            summary: Summary of what happened.
            correlation_id: Optional correlation ID.

        Returns:
            The created ActionLineageRecord.
        """
        record = ActionLineageRecord(
            request_id=request_id,
            plan_id=plan_id,
            decision_id=decision_id,
            session_id=session_id,
            parent_lineage_id=parent_lineage_id,
            stage=stage,
            summary=summary or f"Stage: {stage}",
        )
        self._lineage[str(record.lineage_id)] = record
        log.info(
            "lineage.recorded",
            request_id=request_id,
            stage=stage,
        )
        return record

    def get_lineage(self, lineage_id: str) -> ActionLineageRecord | None:
        """Retrieve a lineage record by ID.

        Args:
            lineage_id: The lineage identifier.

        Returns:
            ActionLineageRecord if found, None otherwise.
        """
        return self._lineage.get(lineage_id)

    def get_lineage_for_request(self, request_id: str) -> list[ActionLineageRecord]:
        """Get all lineage records for a request.

        Args:
            request_id: The request ID.

        Returns:
            List of ActionLineageRecords in chronological order.
        """
        return [
            r for r in self._lineage.values()
            if r.request_id == request_id
        ]

    def get_lineage_for_plan(self, plan_id: str) -> list[ActionLineageRecord]:
        """Get all lineage records for a plan.

        Args:
            plan_id: The plan ID.

        Returns:
            List of ActionLineageRecords in chronological order.
        """
        return [
            r for r in self._lineage.values()
            if r.plan_id == plan_id
        ]

    def clear(self) -> None:
        """Clear all lineage records."""
        self._lineage.clear()
