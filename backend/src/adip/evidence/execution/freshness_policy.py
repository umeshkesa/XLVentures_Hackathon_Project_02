"""Evidence freshness policy.

Evaluates whether evidence is fresh or stale based on
configurable per-type thresholds.
"""

from __future__ import annotations

from datetime import UTC, datetime

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import EvidenceType


class EvidenceFreshnessPolicy:
    """Manages freshness thresholds for evidence types.

    Deterministic placeholder with configurable per-type thresholds.
    """

    DEFAULT_THRESHOLDS: dict[EvidenceType, float] = {
        EvidenceType.SENSOR: 60.0,
        EvidenceType.KNOWLEDGE: 3600.0,
        EvidenceType.REPORT: 43200.0,
        EvidenceType.MEMORY: 86400.0,
        EvidenceType.RULE: 86400.0,
        EvidenceType.WORKFLOW: 3600.0,
        EvidenceType.PLANNER: 3600.0,
        EvidenceType.INCIDENT: 43200.0,
        EvidenceType.MAINTENANCE: 86400.0,
        EvidenceType.CUSTOMER: 43200.0,
        EvidenceType.CRM: 43200.0,
        EvidenceType.EMAIL: 43200.0,
    }

    def __init__(self, thresholds: dict[EvidenceType, float] | None = None) -> None:
        self._thresholds = dict(self.DEFAULT_THRESHOLDS)
        if thresholds:
            self._thresholds.update(thresholds)

    def set_threshold(self, evidence_type: EvidenceType, max_age_seconds: float) -> None:
        """Set the freshness threshold for an evidence type.

        Args:
            evidence_type: The evidence type to set threshold for.
            max_age_seconds: Maximum age in seconds before stale.
        """
        self._thresholds[evidence_type] = max_age_seconds

    def get_threshold(self, evidence_type: EvidenceType) -> float:
        """Get the freshness threshold for an evidence type.

        Args:
            evidence_type: The evidence type to query.

        Returns:
            Max age in seconds for the given type.
        """
        return self._thresholds.get(evidence_type, 3600.0)

    def is_fresh(self, evidence: Evidence) -> bool:
        """Check if evidence is fresh.

        Args:
            evidence: The evidence to check.

        Returns:
            True if the evidence age is within its type's threshold.
        """
        now = datetime.now(UTC)
        age = (now - evidence.timestamp).total_seconds()
        threshold = self.get_threshold(evidence.evidence_type)
        if threshold <= 0:
            return False
        return age <= threshold

    def get_freshness(self, evidence: Evidence) -> float:
        """Get a freshness score (0.0–1.0) for evidence.

        Args:
            evidence: The evidence to evaluate.

        Returns:
            Freshness score where 1.0 is freshly collected.
        """
        now = datetime.now(UTC)
        age = (now - evidence.timestamp).total_seconds()
        threshold = self.get_threshold(evidence.evidence_type)
        if age <= 0:
            return 1.0
        if threshold <= 0:
            return 0.0
        if age >= threshold:
            return 0.0
        return 1.0 - (age / threshold)
