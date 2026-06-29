"""Evidence deduplication.

Detects and marks duplicate evidence across multiple dimensions.
"""

from __future__ import annotations

from enum import StrEnum

from adip.evidence.contracts.models import Evidence


class DuplicateMatchType(StrEnum):
    """Type of duplicate match detected."""

    EXACT_MATCH = "EXACT_MATCH"
    SOURCE_DUPLICATE = "SOURCE_DUPLICATE"
    TIMELINE_DUPLICATE = "TIMELINE_DUPLICATE"
    SEMANTIC_PLACEHOLDER = "SEMANTIC_PLACEHOLDER"


class EvidenceDeduplicator:
    """Detects and marks duplicate evidence.

    Deterministic placeholder that identifies duplicates based on
    exact payload, source, timeline, or semantic similarity.
    """

    def _get_entity_id(self, evidence: Evidence) -> str:
        return evidence.metadata.additional.get("entity_id", "") if evidence.metadata else ""

    def deduplicate(
        self,
        evidence_list: list[Evidence],
    ) -> list[Evidence]:
        """Deduplicate a list of evidence, returning only unique items.

        Args:
            evidence_list: List of evidence to deduplicate.

        Returns:
            List of evidence with duplicates removed.
        """
        unique: list[Evidence] = []
        for ev in evidence_list:
            is_dup = False
            for existing in unique:
                if self.is_duplicate(ev, existing):
                    is_dup = True
                    break
            if not is_dup:
                unique.append(ev)
        return unique

    def is_duplicate(
        self,
        a: Evidence,
        b: Evidence,
    ) -> bool:
        """Check if two evidence items are duplicates.

        Args:
            a: First evidence item.
            b: Second evidence item.

        Returns:
            True if the items are duplicates.
        """
        if a.payload and b.payload and a.payload == b.payload:
            return True
        entity_a = self._get_entity_id(a)
        entity_b = self._get_entity_id(b)
        if a.source.source_id == b.source.source_id and entity_a and entity_a == entity_b:
            return True
        time_diff = abs((a.timestamp - b.timestamp).total_seconds())
        if a.source.source_id == b.source.source_id and time_diff < 60:
            return True
        return False
