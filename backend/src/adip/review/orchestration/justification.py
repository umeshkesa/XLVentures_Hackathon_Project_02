"""ReviewJustification — stores why-fields for review decisions.

Captures the structured justification for review outcomes
including why the review was approved, rejected, modified,
escalated, or delegated. Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

log = structlog.get_logger(__name__)


class ReviewJustificationRecord:
    """Record of a review justification."""

    def __init__(
        self,
        justification_id: str,
        decision_id: str,
        why_approved: str = "",
        why_rejected: str = "",
        why_modified: str = "",
        why_escalated: str = "",
        why_delegated: str = "",
    ) -> None:
        self.justification_id = justification_id
        self.decision_id = decision_id
        self.why_approved = why_approved
        self.why_rejected = why_rejected
        self.why_modified = why_modified
        self.why_escalated = why_escalated
        self.why_delegated = why_delegated
        self.created_at = datetime.now(UTC)


class ReviewJustification:
    """Stores structured justification for review decisions.

    Captures why-fields explaining the reasoning behind
    each possible review outcome for audit and explainability.

    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._records: dict[str, ReviewJustificationRecord] = {}

    def record_justification(
        self,
        decision_id: str,
        why_approved: str = "",
        why_rejected: str = "",
        why_modified: str = "",
        why_escalated: str = "",
        why_delegated: str = "",
        correlation_id: str = "",
    ) -> ReviewJustificationRecord:
        """Record a justification for a review decision.

        Args:
            decision_id: The decision identifier.
            why_approved: Why the review was approved.
            why_rejected: Why the review was rejected.
            why_modified: Why the review was modified.
            why_escalated: Why the review was escalated.
            why_delegated: Why the review was delegated.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewJustificationRecord with the stored justification.
        """
        record = ReviewJustificationRecord(
            justification_id=str(uuid.uuid4()),
            decision_id=decision_id,
            why_approved=why_approved,
            why_rejected=why_rejected,
            why_modified=why_modified,
            why_escalated=why_escalated,
            why_delegated=why_delegated,
        )
        self._records[record.justification_id] = record
        log.info(
            "justification.recorded",
            justification_id=record.justification_id,
            decision_id=decision_id,
            correlation_id=correlation_id,
        )
        return record

    def get_justification(
        self,
        justification_id: str,
    ) -> ReviewJustificationRecord | None:
        """Get a justification by ID.

        Args:
            justification_id: The justification identifier.

        Returns:
            ReviewJustificationRecord if found, None otherwise.
        """
        return self._records.get(justification_id)

    def get_justification_for_decision(
        self,
        decision_id: str,
    ) -> ReviewJustificationRecord | None:
        """Get the justification for a specific decision.

        Args:
            decision_id: The decision identifier.

        Returns:
            ReviewJustificationRecord if found, None otherwise.
        """
        for record in self._records.values():
            if record.decision_id == decision_id:
                return record
        return None

    def count(self) -> int:
        """Get the number of justification records.

        Returns:
            The count of justification records.
        """
        return len(self._records)

    def clear(self) -> None:
        """Clear all justification records."""
        self._records.clear()
