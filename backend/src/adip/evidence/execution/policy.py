"""Evidence policy engine.

Enforces domain, classification, priority, trust, provenance,
and retention policies on evidence.
"""

from __future__ import annotations

from datetime import UTC, datetime

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import EvidenceDomain


class EvidencePolicyEngine:
    """Enforces policies on evidence items.

    Deterministic placeholder that validates domain, classification,
    priority, trust, provenance, and retention policies.
    """

    def __init__(
        self,
        allowed_domains: list[EvidenceDomain] | None = None,
        max_retention_days: int = 365,
    ) -> None:
        self._allowed_domains = allowed_domains or list(EvidenceDomain)
        self._max_retention_days = max_retention_days

    def check_domain(self, evidence: Evidence) -> list[str]:
        """Check domain policy violations.

        Args:
            evidence: The evidence to check.

        Returns:
            List of domain policy violations.
        """
        violations: list[str] = []
        if evidence.domain not in self._allowed_domains:
            violations.append(f"domain '{evidence.domain}' is not in allowed domains")
        return violations

    def check_classification(self, evidence: Evidence) -> list[str]:
        """Check classification policy violations.

        Args:
            evidence: The evidence to check.

        Returns:
            List of classification policy violations.
        """
        violations: list[str] = []
        if not evidence.evidence_type:
            violations.append("evidence type is required for classification")
        return violations

    def check_priority(self, evidence: Evidence) -> list[str]:
        """Check priority policy violations.

        Args:
            evidence: The evidence to check.

        Returns:
            List of priority policy violations.
        """
        return []

    def check_trust(self, evidence: Evidence, trust_score: float = 0.5) -> list[str]:
        """Check trust policy violations.

        Args:
            evidence: The evidence to check.
            trust_score: The calculated trust score.

        Returns:
            List of trust policy violations.
        """
        violations: list[str] = []
        if trust_score < 0.0:
            violations.append("trust score cannot be negative")
        return violations

    def check_provenance(self, evidence: Evidence) -> list[str]:
        """Check provenance policy violations.

        Args:
            evidence: The evidence to check.

        Returns:
            List of provenance policy violations.
        """
        violations: list[str] = []
        if not evidence.source.source_id:
            violations.append("source source_id is required")
        if not evidence.provenance:
            violations.append("provenance is required")
        elif not evidence.provenance.source:
            violations.append("provenance source is required")
        return violations

    def check_retention(self, evidence: Evidence) -> list[str]:
        """Check retention policy violations.

        Args:
            evidence: The evidence to check.

        Returns:
            List of retention policy violations.
        """
        violations: list[str] = []
        now = datetime.now(UTC)
        age_days = (now - evidence.timestamp).total_seconds() / 86400.0
        if age_days > self._max_retention_days:
            violations.append(f"evidence exceeds max retention of {self._max_retention_days} days")
        return violations

    def check_all(self, evidence: Evidence, trust_score: float = 0.5) -> list[str]:
        """Check all policies against evidence.

        Args:
            evidence: The evidence to check.
            trust_score: The calculated trust score.

        Returns:
            List of all policy violations.
        """
        violations: list[str] = []
        violations.extend(self.check_domain(evidence))
        violations.extend(self.check_classification(evidence))
        violations.extend(self.check_priority(evidence))
        violations.extend(self.check_trust(evidence, trust_score))
        violations.extend(self.check_provenance(evidence))
        violations.extend(self.check_retention(evidence))
        return violations
