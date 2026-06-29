"""GovernanceMetrics — governance and compliance metrics collection.

Collects operational metrics for the review system including
approval, rejection, escalation, modification rates, review
times, and SLA compliance tracking.
"""

from __future__ import annotations

import structlog

from adip.review.execution.models import GovernanceMetricsSnapshot

log = structlog.get_logger(__name__)


class GovernanceMetrics:
    """Collects governance and compliance metrics for the review system.

    Phase 3 adds governance confidence tracking, audit, version,
    and delegation counters.
    """

    def __init__(self) -> None:
        self._reviews_total: int = 0
        self._approved_total: int = 0
        self._rejected_total: int = 0
        self._escalated_total: int = 0
        self._modified_total: int = 0
        self._info_requested_total: int = 0
        self._deferred_total: int = 0
        self._review_times: list[float] = []
        self._sla_compliant: int = 0
        self._sla_breaches: int = 0
        self._approvals_per_domain: dict[str, int] = {}
        self._reviews_per_role: dict[str, int] = {}
        # Phase 3 counters
        self._governance_confidences: list[float] = []
        self._audit_packages_total: int = 0
        self._versions_total: int = 0
        self._delegations_total: int = 0
        self._consensus_evaluations: int = 0

    def record_approval(self, domain: str = "", role: str = "") -> None:
        """Record an approval."""
        self._reviews_total += 1
        self._approved_total += 1
        if domain:
            self._approvals_per_domain[domain] = self._approvals_per_domain.get(domain, 0) + 1
        if role:
            self._reviews_per_role[role] = self._reviews_per_role.get(role, 0) + 1
        log.info("governance_metrics.approval", domain=domain, role=role)

    def record_rejection(self, domain: str = "", role: str = "") -> None:
        """Record a rejection."""
        self._reviews_total += 1
        self._rejected_total += 1
        if domain:
            self._approvals_per_domain[domain] = self._approvals_per_domain.get(domain, 0) + 1
        if role:
            self._reviews_per_role[role] = self._reviews_per_role.get(role, 0) + 1
        log.info("governance_metrics.rejection", domain=domain, role=role)

    def record_escalation(self, domain: str = "", role: str = "") -> None:
        """Record an escalation."""
        self._reviews_total += 1
        self._escalated_total += 1
        if domain:
            self._approvals_per_domain[domain] = self._approvals_per_domain.get(domain, 0) + 1
        if role:
            self._reviews_per_role[role] = self._reviews_per_role.get(role, 0) + 1
        log.info("governance_metrics.escalation", domain=domain, role=role)

    def record_modification(self, domain: str = "", role: str = "") -> None:
        """Record a modification."""
        self._reviews_total += 1
        self._modified_total += 1
        if domain:
            self._approvals_per_domain[domain] = self._approvals_per_domain.get(domain, 0) + 1
        if role:
            self._reviews_per_role[role] = self._reviews_per_role.get(role, 0) + 1
        log.info("governance_metrics.modification", domain=domain, role=role)

    def record_review_time(self, time_ms: float) -> None:
        """Record a review latency sample."""
        self._review_times.append(time_ms)
        log.info("governance_metrics.review_time", time_ms=time_ms)

    def record_sla_compliance(self, was_compliant: bool) -> None:
        """Record an SLA compliance result."""
        if was_compliant:
            self._sla_compliant += 1
        else:
            self._sla_breaches += 1
        log.info("governance_metrics.sla_compliance", was_compliant=was_compliant)

    # ── Phase 3 metric methods ───────────────────────────────────────────

    def record_governance_confidence(self, confidence: float) -> None:
        """Record a governance confidence score.

        Args:
            confidence: The governance confidence score (0-1).
        """
        self._governance_confidences.append(max(0.0, min(1.0, confidence)))
        log.info("governance_metrics.governance_confidence", confidence=confidence)

    def record_audit_package(self) -> None:
        """Record an audit package creation."""
        self._audit_packages_total += 1
        log.info("governance_metrics.audit_package", total=self._audit_packages_total)

    def record_version(self) -> None:
        """Record a version creation."""
        self._versions_total += 1
        log.info("governance_metrics.version", total=self._versions_total)

    def record_delegation(self) -> None:
        """Record a delegation operation."""
        self._delegations_total += 1
        log.info("governance_metrics.delegation", total=self._delegations_total)

    def record_consensus_evaluation(self) -> None:
        """Record a consensus evaluation."""
        self._consensus_evaluations += 1
        log.info("governance_metrics.consensus", total=self._consensus_evaluations)

    def get_average_governance_confidence(self) -> float:
        """Get the average governance confidence score.

        Returns:
            Average governance confidence (0-1), 0.0 if no data.
        """
        if not self._governance_confidences:
            return 0.0
        return round(sum(self._governance_confidences) / len(self._governance_confidences), 4)

    def get_audit_packages_total(self) -> int:
        """Get the total number of audit packages.

        Returns:
            The total count.
        """
        return self._audit_packages_total

    def get_versions_total(self) -> int:
        """Get the total number of versions.

        Returns:
            The total count.
        """
        return self._versions_total

    def get_delegations_total(self) -> int:
        """Get the total number of delegations.

        Returns:
            The total count.
        """
        return self._delegations_total

    def get_approval_rate(self) -> float:
        """Get the approval rate as a percentage (0-100)."""
        if self._reviews_total == 0:
            return 0.0
        return round((self._approved_total / self._reviews_total) * 100, 2)

    def get_rejection_rate(self) -> float:
        """Get the rejection rate as a percentage (0-100)."""
        if self._reviews_total == 0:
            return 0.0
        return round((self._rejected_total / self._reviews_total) * 100, 2)

    def get_escalation_rate(self) -> float:
        """Get the escalation rate as a percentage (0-100)."""
        if self._reviews_total == 0:
            return 0.0
        return round((self._escalated_total / self._reviews_total) * 100, 2)

    def get_average_review_time(self) -> float:
        """Get the average review time in milliseconds."""
        if not self._review_times:
            return 0.0
        return round(sum(self._review_times) / len(self._review_times), 2)

    def get_sla_compliance_rate(self) -> float:
        """Get the SLA compliance rate as a percentage (0-100)."""
        total = self._sla_compliant + self._sla_breaches
        if total == 0:
            return 0.0
        return round((self._sla_compliant / total) * 100, 2)

    def snapshot(self) -> GovernanceMetricsSnapshot:
        """Take a point-in-time snapshot of all governance metrics."""
        return GovernanceMetricsSnapshot(
            reviews_total=self._reviews_total,
            approved_total=self._approved_total,
            rejected_total=self._rejected_total,
            escalated_total=self._escalated_total,
            modified_total=self._modified_total,
            approval_rate=self.get_approval_rate(),
            rejection_rate=self.get_rejection_rate(),
            escalation_rate=self.get_escalation_rate(),
            average_review_time_ms=self.get_average_review_time(),
            sla_compliance_rate=self.get_sla_compliance_rate(),
            sla_breaches=self._sla_breaches,
            average_governance_confidence=self.get_average_governance_confidence(),
            audit_packages_total=self._audit_packages_total,
            versions_total=self._versions_total,
            delegations_total=self._delegations_total,
            consensus_evaluations=self._consensus_evaluations,
        )

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self._reviews_total = 0
        self._approved_total = 0
        self._rejected_total = 0
        self._escalated_total = 0
        self._modified_total = 0
        self._info_requested_total = 0
        self._deferred_total = 0
        self._review_times.clear()
        self._sla_compliant = 0
        self._sla_breaches = 0
        self._approvals_per_domain.clear()
        self._reviews_per_role.clear()
        self._governance_confidences.clear()
        self._audit_packages_total = 0
        self._versions_total = 0
        self._delegations_total = 0
        self._consensus_evaluations = 0
        log.info("governance_metrics.reset")
