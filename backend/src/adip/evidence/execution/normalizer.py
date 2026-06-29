"""Evidence normalization component.

Normalizes evidence to a standard format for downstream processing.
"""

from __future__ import annotations

from datetime import UTC

from adip.evidence.contracts.models import Evidence, EvidenceMetadata


class EvidenceNormalizer:
    """Normalizes evidence fields to standard formats.

    Deterministic placeholder that normalizes metadata, timestamps,
    source identifiers, and domain values.
    """

    def normalize(self, evidence: Evidence) -> Evidence:
        """Normalize evidence to a standard format.

        Applies:
        - Source identifiers → lowercase
        - Domain → uppercase
        - Timestamps → UTC

        Args:
            evidence: The evidence to normalize.

        Returns:
            A new Evidence object with normalized fields.
        """
        normalized_source_id = evidence.source.source_id.lower() if evidence.source.source_id else ""
        normalized_domain = evidence.domain.upper() if evidence.domain else evidence.domain

        source = evidence.source.model_copy()
        source.source_id = normalized_source_id

        provenance = evidence.provenance.model_copy() if evidence.provenance else None
        if provenance:
            provenance.source = provenance.source.lower() if provenance.source else ""
            provenance.manager = provenance.manager.lower() if provenance.manager else ""

        metadata = evidence.metadata.model_copy() if evidence.metadata else EvidenceMetadata()
        for key in list(metadata.additional.keys()):
            if metadata.additional[key] is None:
                metadata.additional[key] = ""

        timestamp = evidence.timestamp.replace(tzinfo=UTC) if evidence.timestamp.tzinfo is None else evidence.timestamp

        return Evidence(
            evidence_id=evidence.evidence_id,
            evidence_type=evidence.evidence_type,
            domain=normalized_domain,
            status=evidence.status,
            source=source,
            metadata=metadata,
            provenance=provenance,
            quality=evidence.quality,
            payload=evidence.payload,
            timestamp=timestamp,
        )

    def normalize_batch(self, evidence_list: list[Evidence]) -> list[Evidence]:
        """Normalize a batch of evidence.

        Args:
            evidence_list: List of evidence to normalize.

        Returns:
            List of normalized evidence.
        """
        return [self.normalize(ev) for ev in evidence_list]
