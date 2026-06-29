"""Evidence collection component.

Deterministic placeholder that creates Evidence objects with
generated provenance and type/domain-appropriate metadata.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceMetadata,
    EvidenceProvenance,
    EvidenceSource,
)
from adip.evidence.enums import EvidenceDomain, EvidenceStatus, EvidenceType


class EvidenceCollector:
    """Collects evidence from multiple source types.

    Deterministic placeholder that produces Evidence objects with
    COLLECTED status, generated provenance, and appropriate metadata.
    """

    def collect(
        self,
        evidence_type: EvidenceType,
        domain: EvidenceDomain,
        payload: dict[str, Any] | None = None,
        source_id: str | None = None,
        entity_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Evidence:
        """Collect a single piece of evidence from a source.

        Args:
            evidence_type: The type of source to collect from.
            domain: The domain the evidence belongs to.
            payload: Optional payload for the evidence.
            source_id: Optional source identifier.
            entity_id: Optional entity identifier.
            metadata: Optional additional metadata.

        Returns:
            An Evidence object with COLLECTED status.
        """
        now = datetime.now(UTC)
        extra_metadata = dict(metadata or {})
        if entity_id:
            extra_metadata["entity_id"] = entity_id

        source = EvidenceSource(
            source_id=source_id or f"source-{evidence_type.value.lower()}",
            source_type=evidence_type.value,
            manager=f"{evidence_type.value.lower()}_manager",
            version="1.0",
        )
        provenance = EvidenceProvenance(
            source=f"source-{evidence_type.value.lower()}",
            source_type=evidence_type.value,
            manager=f"{evidence_type.value.lower()}_manager",
            version="1.0",
            retrieved_at=now,
            owner="system",
            original_identifier=str(uuid.uuid4()),
        )
        return Evidence(
            evidence_id=uuid.uuid4(),
            evidence_type=evidence_type,
            domain=domain,
            status=EvidenceStatus.COLLECTED,
            source=source,
            metadata=EvidenceMetadata(
                title=f"Evidence from {evidence_type.value}",
                description=f"Collected from {evidence_type.value} source",
                additional=extra_metadata,
            ),
            provenance=provenance,
            payload=payload or {},
            timestamp=now,
        )

    def collect_batch(
        self,
        evidence_type: EvidenceType,
        domain: EvidenceDomain,
        items: list[dict[str, Any]],
        source_id: str | None = None,
    ) -> list[Evidence]:
        """Collect a batch of evidence items from a source.

        Args:
            evidence_type: The type of source to collect from.
            domain: The domain the evidence belongs to.
            items: List of payload dictionaries to create evidence for.
            source_id: Optional source identifier.

        Returns:
            List of Evidence objects with COLLECTED status.
        """
        return [
            self.collect(
                evidence_type=evidence_type,
                domain=domain,
                payload=item,
                source_id=source_id,
                entity_id=item.get("entity_id") if isinstance(item, dict) else None,
            )
            for item in items
        ]
