"""ExecutionLineage — tracks decision lineage for execution operations.

Deterministic placeholder that maintains a provenance chain
from execution request through session, result, and decision.
Provides traceability for audit and governance.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ExecutionLineageRecord(BaseModel):
    """A lineage record in the execution chain."""

    lineage_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique lineage identifier",
    )
    request_id: str = Field(
        default="",
        description="The request ID this lineage tracks",
    )
    session_id: str | None = Field(
        default=None,
        description="The session ID in this lineage",
    )
    result_id: str | None = Field(
        default=None,
        description="The result ID in this lineage",
    )
    decision_id: str | None = Field(
        default=None,
        description="The decision ID in this lineage",
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


class ExecutionLineage:
    """Tracks decision lineage for execution operations.

    Maintains a sequence of lineage records tracing the
    provenance of execution operations from request through
    to decision.
    """

    def __init__(self) -> None:
        self._lineage: dict[str, ExecutionLineageRecord] = {}

    def record(
        self,
        request_id: str,
        session_id: str | None = None,
        result_id: str | None = None,
        decision_id: str | None = None,
        parent_lineage_id: str | None = None,
        stage: str = "",
        summary: str = "",
        correlation_id: str = "",
    ) -> ExecutionLineageRecord:
        """Record a lineage entry.

        Args:
            request_id: The request ID.
            session_id: Optional session ID.
            result_id: Optional result ID.
            decision_id: Optional decision ID.
            parent_lineage_id: Optional parent lineage ID.
            stage: The pipeline stage name.
            summary: Summary of what happened.
            correlation_id: Optional correlation ID.

        Returns:
            The created ExecutionLineageRecord.
        """
        record = ExecutionLineageRecord(
            request_id=request_id,
            session_id=session_id,
            result_id=result_id,
            decision_id=decision_id,
            parent_lineage_id=parent_lineage_id,
            stage=stage,
            summary=summary,
        )
        self._lineage[str(record.lineage_id)] = record
        log.info(
            "lineage.recorded",
            request_id=request_id,
            stage=stage,
            lineage_id=str(record.lineage_id),
            cid=correlation_id,
        )
        return record

    def get_lineage(self, lineage_id: str) -> ExecutionLineageRecord | None:
        """Retrieve a lineage record by ID.

        Args:
            lineage_id: The lineage identifier.

        Returns:
            ExecutionLineageRecord if found, None otherwise.
        """
        return self._lineage.get(lineage_id)

    def get_lineage_for_request(
        self,
        request_id: str,
    ) -> list[ExecutionLineageRecord]:
        """Get all lineage records for a request.

        Args:
            request_id: The request identifier.

        Returns:
            List of ExecutionLineageRecord in chronological order.
        """
        return sorted(
            [
                r for r in self._lineage.values()
                if r.request_id == request_id
            ],
            key=lambda r: r.timestamp,
        )

    def get_lineage_for_session(
        self,
        session_id: str,
    ) -> list[ExecutionLineageRecord]:
        """Get all lineage records for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of ExecutionLineageRecord in chronological order.
        """
        return sorted(
            [
                r for r in self._lineage.values()
                if r.session_id == session_id
            ],
            key=lambda r: r.timestamp,
        )
