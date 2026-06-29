"""EvidenceConsensusManager — deterministic consensus scoring.

Assesses consensus levels for evidence fusion based on
agreement and conflict scores across evidence items.
Placeholder implementation using simple heuristics.
"""

from __future__ import annotations

import structlog

from adip.evidence.enums import ConsensusLevel

log = structlog.get_logger(__name__)


class EvidenceConsensusManager:
    """Manages consensus scoring for evidence fusion.

    Deterministic placeholder that calculates agreement and
    conflict scores to determine consensus levels
    (HIGH, MEDIUM, LOW).
    """

    def calculate_agreement_score(
        self,
        evidence_ids: list[str],
        correlation_count: int = 0,
        conflict_count: int = 0,
        total_possible_correlations: int = 0,
    ) -> float:
        """Calculate an agreement score for a set of evidence.

        Agreement = correlated / max(1, total_possible)
        scaled by conflict penalty.

        Args:
            evidence_ids: The evidence IDs being evaluated.
            correlation_count: Number of correlations found.
            conflict_count: Number of conflicts detected.
            total_possible_correlations: Maximum possible correlations.

        Returns:
            Agreement score (0.0–1.0).
        """
        n = len(evidence_ids)
        if n < 2:
            return 1.0
        possible = total_possible_correlations or (n * (n - 1) // 2)
        raw_agreement = correlation_count / max(1, possible)
        conflict_penalty = 1.0 - min(1.0, conflict_count / max(1, n))
        return round(max(0.0, raw_agreement * conflict_penalty), 4)

    def calculate_conflict_score(
        self,
        evidence_ids: list[str],
        conflict_count: int = 0,
    ) -> float:
        """Calculate a conflict score for a set of evidence.

        Conflict = conflicts / max(1, evidence_count).

        Args:
            evidence_ids: The evidence IDs being evaluated.
            conflict_count: Number of conflicts detected.

        Returns:
            Conflict score (0.0–1.0).
        """
        n = len(evidence_ids)
        if n < 2:
            return 0.0
        return round(min(1.0, conflict_count / max(1, n)), 4)

    def determine_consensus_level(
        self,
        agreement_score: float,
        conflict_score: float,
    ) -> ConsensusLevel:
        """Determine consensus level based on agreement and conflict.

        Args:
            agreement_score: Agreement score (0.0–1.0).
            conflict_score: Conflict score (0.0–1.0).

        Returns:
            ConsensusLevel: HIGH, MEDIUM, or LOW.
        """
        effective = agreement_score * (1.0 - conflict_score)
        if effective >= 0.7:
            return ConsensusLevel.HIGH
        if effective >= 0.4:
            return ConsensusLevel.MEDIUM
        return ConsensusLevel.LOW

    def get_consensus_reasoning(
        self,
        agreement_score: float,
        conflict_score: float,
        evidence_count: int,
    ) -> list[str]:
        """Generate explainability strings for consensus assessment.

        Args:
            agreement_score: Agreement score (0.0–1.0).
            conflict_score: Conflict score (0.0–1.0).
            evidence_count: Number of evidence items considered.

        Returns:
            List of human-readable reasons for the consensus.
        """
        effective = agreement_score * (1.0 - conflict_score)
        level = self.determine_consensus_level(agreement_score, conflict_score)
        return [
            f"Evidence count: {evidence_count}",
            f"Agreement score: {agreement_score:.2f}",
            f"Conflict score: {conflict_score:.2f}",
            f"Effective consensus: {effective:.2f}",
            f"Consensus level: {level.value}",
        ]
