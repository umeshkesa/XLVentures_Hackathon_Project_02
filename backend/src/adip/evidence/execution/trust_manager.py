"""Evidence trust calculation.

Calculates trust scores for evidence based on source reliability,
accuracy, validation success rate, and provenance quality.
"""

from __future__ import annotations

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.models import TrustScore
from adip.evidence.execution.source_reliability import EvidenceSourceReliability


class EvidenceTrustManager:
    """Calculates trust scores for evidence.

    Deterministic placeholder that computes trust scores based on
    source reliability, accuracy, validation success rate, and
    provenance completeness.
    """

    def __init__(self, source_reliability: EvidenceSourceReliability | None = None) -> None:
        self._source_reliability = source_reliability or EvidenceSourceReliability()

    def calculate_trust_score(self, evidence: Evidence) -> TrustScore:
        """Calculate a trust score for the given evidence.

        Args:
            evidence: The evidence to evaluate.

        Returns:
            A TrustScore with individual component scores.
        """
        source_id = evidence.source.source_id
        source_reliability = self._source_reliability.get_reliability(source_id)

        provenance = evidence.provenance
        provenance_fields = 0
        if provenance:
            if provenance.source:
                provenance_fields += 1
            if provenance.manager:
                provenance_fields += 1
            if provenance.source_type:
                provenance_fields += 1
            if provenance.owner:
                provenance_fields += 1
        provenance_quality = provenance_fields / 4.0

        metadata = evidence.metadata
        populated = 0
        if metadata.title:
            populated += 1
        if metadata.description:
            populated += 1
        if metadata.tags:
            populated += 1
        if metadata.category:
            populated += 1
        metadata_completeness = populated / 4.0

        validation_status = 1.0
        if evidence.status.value == "COLLECTED":
            validation_status = 0.5
        elif evidence.status.value == "VALIDATED":
            validation_status = 1.0
        elif evidence.status.value == "NORMALIZED":
            validation_status = 0.9

        combined_components = [source_reliability, metadata_completeness, validation_status, provenance_quality]
        trust_score_value = sum(combined_components) / len(combined_components)

        return TrustScore(
            score=trust_score_value,
            source_reliability=source_reliability,
            historical_accuracy=metadata_completeness,
            validation_status=validation_status,
            provenance=provenance_quality,
        )
