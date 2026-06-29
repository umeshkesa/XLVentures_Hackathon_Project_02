"""Evidence validation component.

Validates evidence completeness and correctness against defined rules.
"""

from __future__ import annotations

from datetime import UTC, datetime

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import EvidenceDomain


class EvidenceValidator:
    """Validates evidence metadata, provenance, and status transitions.

    Deterministic placeholder that returns lists of violation strings.
    """

    def validate(self, evidence: Evidence) -> list[str]:
        """Validate evidence completeness and correctness.

        Args:
            evidence: The evidence to validate.

        Returns:
            List of violation strings (empty if fully valid).
        """
        violations: list[str] = []

        if evidence.domain not in list(EvidenceDomain):
            violations.append(f"invalid domain: {evidence.domain}")

        if evidence.evidence_type is None:
            violations.append("evidence type is missing")

        now = datetime.now(UTC)
        age = (now - evidence.timestamp).total_seconds()
        if age < 0:
            violations.append("timestamp is in the future")

        if not evidence.source.source_id:
            violations.append("source source_id is empty")

        if evidence.provenance is None:
            violations.append("provenance is missing")
        else:
            if not evidence.provenance.source:
                violations.append("provenance source is empty")
            if not evidence.provenance.manager:
                violations.append("provenance manager is empty")

        if not evidence.metadata.title and not evidence.metadata.description:
            violations.append("metadata title and description are both empty")

        return violations
