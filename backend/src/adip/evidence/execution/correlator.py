"""Evidence correlation component.

Correlates evidence by matching source, time, domain, and entity.
"""

from __future__ import annotations

import uuid

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.models import CorrelationResult


class EvidenceCorrelator:
    """Correlates evidence items based on shared characteristics.

    Deterministic placeholder that finds correlations based on
    shared source, time proximity, matching domain, and matching
    entity ID.
    """

    def _get_entity_id(self, evidence: Evidence) -> str:
        return evidence.metadata.additional.get("entity_id", "") if evidence.metadata else ""

    def correlate(
        self,
        evidence: Evidence,
        pool: list[Evidence],
    ) -> CorrelationResult:
        """Correlate evidence against a pool of other evidence.

        Args:
            evidence: The source evidence to correlate.
            pool: Pool of evidence to correlate against.

        Returns:
            A CorrelationResult with correlations and scores.
        """
        correlated_ids: list[uuid.UUID] = []
        source_matches = 0
        temporal_matches = 0
        domain_matches = 0
        entity_matches = 0
        evidence_entity = self._get_entity_id(evidence)

        for other in pool:
            if other.evidence_id == evidence.evidence_id:
                continue

            matched = False

            if evidence.source.source_id == other.source.source_id:
                source_matches += 1
                matched = True

            time_diff = abs((evidence.timestamp - other.timestamp).total_seconds())
            if time_diff < 3600:
                temporal_matches += 1
                matched = True

            if evidence.domain == other.domain:
                domain_matches += 1
                matched = True

            other_entity = self._get_entity_id(other)
            if evidence_entity and other_entity and evidence_entity == other_entity:
                entity_matches += 1
                matched = True

            if matched:
                correlated_ids.append(other.evidence_id)

        total = len(pool) - 1 if pool else 0
        n = max(total, 1)

        return CorrelationResult(
            correlation_id=str(uuid.uuid4()),
            source_evidence_id=evidence.evidence_id,
            correlated_evidence_ids=correlated_ids,
            source_score=min(source_matches / n, 1.0),
            temporal_score=min(temporal_matches / n, 1.0),
            domain_score=min(domain_matches / n, 1.0),
            entity_score=min(entity_matches / n, 1.0),
            overall_score=min((source_matches + temporal_matches + domain_matches + entity_matches) / (4 * n), 1.0),
        )

    def correlate_batch(
        self,
        evidence_list: list[Evidence],
    ) -> list[CorrelationResult]:
        """Correlate all evidence in a list against each other.

        Args:
            evidence_list: List of evidence to correlate.

        Returns:
            List of CorrelationResult for each evidence item.
        """
        return [
            self.correlate(ev, evidence_list) for ev in evidence_list
        ]
