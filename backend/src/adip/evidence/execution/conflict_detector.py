"""Evidence conflict detection.

Detects conflicts, contradictions, duplicates, and staleness
between evidence items.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.models import ConflictReport


class EvidenceConflictDetector:
    """Detects conflicts between evidence items.

    Deterministic placeholder that detects contradictory statements,
    duplicates, missing entities, and stale timestamps.
    """

    def _get_entity_id(self, evidence: Evidence) -> str:
        return evidence.metadata.additional.get("entity_id", "") if evidence.metadata else ""

    def detect(self, evidence_list: list[Evidence]) -> ConflictReport:
        """Detect conflicts within a list of evidence.

        Args:
            evidence_list: List of evidence to analyse.

        Returns:
            A ConflictReport detailing all conflicts found.
        """
        contradictory_pairs: list[tuple[uuid.UUID, uuid.UUID]] = []
        duplicate_pairs: list[tuple[uuid.UUID, uuid.UUID]] = []
        missing_entity_ids: list[uuid.UUID] = []
        stale_evidence_ids: list[uuid.UUID] = []

        now = datetime.now(UTC)

        for i, a in enumerate(evidence_list):
            entity_a = self._get_entity_id(a)
            if not entity_a:
                missing_entity_ids.append(a.evidence_id)

            age = (now - a.timestamp).total_seconds()
            if age > 86400:
                stale_evidence_ids.append(a.evidence_id)

            for b in evidence_list[i + 1:]:
                if a.payload and b.payload and a.payload == b.payload:
                    duplicate_pairs.append((a.evidence_id, b.evidence_id))

                if a.source.source_id == b.source.source_id:
                    if a.payload and b.payload and a.payload != b.payload:
                        contradictory_pairs.append((a.evidence_id, b.evidence_id))

        report_id = str(uuid.uuid4())
        has_conflicts = bool(contradictory_pairs or duplicate_pairs or stale_evidence_ids)
        conflict_count = len(contradictory_pairs) + len(duplicate_pairs) + len(stale_evidence_ids)

        return ConflictReport(
            report_id=report_id,
            contradictory_pairs=contradictory_pairs,
            duplicate_pairs=duplicate_pairs,
            missing_evidence_ids=missing_entity_ids,
            stale_evidence_ids=stale_evidence_ids,
            has_conflicts=has_conflicts,
            conflict_count=conflict_count,
        )
