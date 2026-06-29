"""ReviewReadiness — assesses readiness of a review operation.

Determines READY, PENDING, BLOCKED, ESCALATED, or
MORE_INFORMATION_REQUIRED status. Deterministic placeholder.
"""

from __future__ import annotations

import uuid

import structlog

from adip.review.contracts.models import ReviewReadiness as ReviewReadinessModel

log = structlog.get_logger(__name__)


class ReviewReadiness:
    """Assesses review readiness.

    Determines whether a review is ready to proceed based on
    checklist completion, SLA compliance, reviewer assignment,
    and policy compliance.

    Statuses:
    - READY: all conditions met
    - PENDING: awaiting completion of conditions
    - BLOCKED: conditions cannot be met
    - ESCALATED: requires escalation
    - MORE_INFORMATION_REQUIRED: additional information needed

    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._readiness_records: dict[str, ReviewReadinessModel] = {}

    def assess_readiness(
        self,
        decision_id: str,
        checklist_complete: bool = False,
        sla_compliant: bool = True,
        reviewers_assigned: bool = False,
        policy_compliant: bool = True,
        correlation_id: str = "",
    ) -> ReviewReadinessModel:
        """Assess the readiness of a review.

        Args:
            decision_id: The decision identifier.
            checklist_complete: Whether all checklist items are complete.
            sla_compliant: Whether the review is SLA-compliant.
            reviewers_assigned: Whether all required reviewers are assigned.
            policy_compliant: Whether the review is policy-compliant.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewReadinessModel with the readiness assessment.
        """
        status = self._determine_status(
            checklist_complete=checklist_complete,
            sla_compliant=sla_compliant,
            reviewers_assigned=reviewers_assigned,
            policy_compliant=policy_compliant,
        )
        reason = self._build_reason(
            status=status,
            checklist_complete=checklist_complete,
            sla_compliant=sla_compliant,
            reviewers_assigned=reviewers_assigned,
            policy_compliant=policy_compliant,
        )

        did = uuid.UUID(decision_id) if isinstance(decision_id, str) else decision_id
        readiness = ReviewReadinessModel(
            decision_id=did,
            status=status,
            reason=reason,
            checklist_complete=checklist_complete,
            sla_compliant=sla_compliant,
            reviewers_assigned=reviewers_assigned,
            policy_compliant=policy_compliant,
        )
        rid = str(readiness.readiness_id)
        self._readiness_records[rid] = readiness
        log.info(
            "readiness.assessed",
            readiness_id=rid,
            decision_id=decision_id,
            status=status,
            correlation_id=correlation_id,
        )
        return readiness

    def _determine_status(
        self,
        checklist_complete: bool,
        sla_compliant: bool,
        reviewers_assigned: bool,
        policy_compliant: bool,
    ) -> str:
        if not policy_compliant:
            return "BLOCKED"
        if not sla_compliant:
            return "ESCALATED"
        if not checklist_complete and not reviewers_assigned:
            return "MORE_INFORMATION_REQUIRED"
        if not reviewers_assigned:
            return "PENDING"
        if not checklist_complete:
            return "PENDING"
        return "READY"

    def _build_reason(
        self,
        status: str,
        checklist_complete: bool,
        sla_compliant: bool,
        reviewers_assigned: bool,
        policy_compliant: bool,
    ) -> str:
        reasons: list[str] = []
        if not policy_compliant:
            reasons.append("Policy compliance check failed")
        if not sla_compliant:
            reasons.append("SLA breach detected")
        if not reviewers_assigned:
            reasons.append("Reviewers not fully assigned")
        if not checklist_complete:
            reasons.append("Checklist items incomplete")
        if status == "READY":
            reasons.append("All readiness conditions met")
        return "; ".join(reasons) if reasons else "Ready to proceed"

    def get_readiness(self, readiness_id: str) -> ReviewReadinessModel | None:
        """Get a readiness record by ID.

        Args:
            readiness_id: The readiness identifier.

        Returns:
            ReviewReadinessModel if found, None otherwise.
        """
        return self._readiness_records.get(readiness_id)

    def get_readiness_for_decision(
        self,
        decision_id: str,
    ) -> ReviewReadinessModel | None:
        """Get the readiness record for a decision.

        Args:
            decision_id: The decision identifier.

        Returns:
            ReviewReadinessModel if found, None otherwise.
        """
        did = str(decision_id)
        for record in self._readiness_records.values():
            if str(record.decision_id) == did:
                return record
        return None

    def count(self) -> int:
        """Get the number of readiness records.

        Returns:
            The count of readiness records.
        """
        return len(self._readiness_records)

    def clear(self) -> None:
        """Clear all readiness records."""
        self._readiness_records.clear()
