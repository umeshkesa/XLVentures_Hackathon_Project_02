"""Evidence quality assessment.

Evaluates evidence quality based on freshness, completeness,
reliability, and consistency.
"""

from __future__ import annotations

from dataclasses import dataclass

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
from adip.evidence.execution.source_reliability import EvidenceSourceReliability


@dataclass
class QualityAssessment:
    """Detailed quality assessment for a piece of evidence."""

    evidence_id: str = ""
    freshness: float = 0.0
    completeness: float = 0.0
    reliability: float = 0.0
    consistency: float = 0.0
    overall: float = 0.0


class EvidenceQualityManager:
    """Assesses the quality of evidence.

    Deterministic placeholder that evaluates freshness, completeness,
    reliability, and consistency.
    """

    def __init__(
        self,
        freshness_policy: EvidenceFreshnessPolicy | None = None,
        source_reliability: EvidenceSourceReliability | None = None,
    ) -> None:
        self._freshness_policy = freshness_policy or EvidenceFreshnessPolicy()
        self._source_reliability = source_reliability or EvidenceSourceReliability()

    def assess_quality(self, evidence: Evidence) -> QualityAssessment:
        """Assess the quality of a single evidence item.

        Args:
            evidence: The evidence to assess.

        Returns:
            A QualityAssessment with component scores.
        """
        freshness = self._freshness_policy.get_freshness(evidence)

        metadata_fields = ["source", "evidence_type", "domain", "provenance"]
        populated = sum(1 for f in metadata_fields if getattr(evidence, f, None))
        completeness = populated / len(metadata_fields)

        reliability = self._source_reliability.get_reliability(evidence.source.source_id)

        consistency = 0.5
        if evidence.evidence_type and evidence.domain:
            consistency = 0.8

        overall = (freshness + completeness + reliability + consistency) / 4.0

        return QualityAssessment(
            evidence_id=str(evidence.evidence_id),
            freshness=freshness,
            completeness=completeness,
            reliability=reliability,
            consistency=consistency,
            overall=overall,
        )

    def assess_batch(
        self,
        evidence_list: list[Evidence],
    ) -> list[QualityAssessment]:
        """Assess quality for a batch of evidence.

        Args:
            evidence_list: List of evidence to assess.

        Returns:
            List of QualityAssessment results.
        """
        return [self.assess_quality(ev) for ev in evidence_list]
