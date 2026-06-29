"""Evidence correlation scoring.

Calculates detailed correlation scores between evidence pairs.
"""

from __future__ import annotations

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.models import CorrelationScore


class EvidenceCorrelationScorer:
    """Calculates correlation scores between evidence pairs.

    Deterministic placeholder that computes source agreement,
    temporal consistency, domain consistency, and entity match.
    """

    def _get_entity_id(self, evidence: Evidence) -> str:
        return evidence.metadata.additional.get("entity_id", "") if evidence.metadata else ""

    def calculate(
        self,
        evidence: Evidence,
        pool: list[Evidence],
    ) -> list[CorrelationScore]:
        """Calculate correlation scores against a pool of evidence.

        Args:
            evidence: The source evidence.
            pool: Pool of evidence to compare against.

        Returns:
            List of CorrelationScore for each pool item.
        """
        scores: list[CorrelationScore] = []
        evidence_entity = self._get_entity_id(evidence)
        for other in pool:
            if other.evidence_id == evidence.evidence_id:
                continue

            source_agreement = 1.0 if evidence.source.source_id == other.source.source_id else 0.0

            time_diff = abs((evidence.timestamp - other.timestamp).total_seconds())
            temporal_consistency = max(0.0, 1.0 - (time_diff / 86400.0))

            domain_consistency = 1.0 if evidence.domain == other.domain else 0.0

            other_entity = self._get_entity_id(other)
            entity_match = 1.0 if (evidence_entity and other_entity and evidence_entity == other_entity) else 0.0

            overall = (source_agreement + temporal_consistency + domain_consistency + entity_match) / 4.0

            scores.append(CorrelationScore(
                source_agreement=source_agreement,
                temporal_consistency=temporal_consistency,
                domain_consistency=domain_consistency,
                entity_match=entity_match,
                overall=overall,
            ))
        return scores
