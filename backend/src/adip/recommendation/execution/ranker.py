"""RecommendationRanker — ranks recommendation candidates.

Ranks recommendations using placeholder scoring based on
confidence, business value, impact, risk, and feasibility.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.contracts.models import (
    RecommendationCandidate,
    RecommendationConstraint,
    RecommendationGoal,
)

log = structlog.get_logger(__name__)


class RecommendationRanker:
    """Ranks recommendation candidates by priority and relevance.

    Deterministic placeholder that ranks candidates based on
    confidence, business value, impact, risk, and feasibility.
    """

    def __init__(self) -> None:
        self._rankings: dict[str, float] = {}

    def rank(
        self,
        candidates: list[RecommendationCandidate],
        goals: list[RecommendationGoal] | None = None,
        constraints: list[RecommendationConstraint] | None = None,
    ) -> list[RecommendationCandidate]:
        """Rank recommendation candidates by priority and relevance.

        Args:
            candidates: List of candidates to rank.
            goals: Optional goals to guide ranking.
            constraints: Optional constraints to guide ranking.

        Returns:
            Ranked list of candidates (highest score first).
        """
        log.info("ranker.rank", candidate_count=len(candidates))
        scored: list[tuple[float, RecommendationCandidate]] = []
        for candidate in candidates:
            score = self._calculate_score(candidate, goals or [], constraints or [])
            scored.append((score, candidate))
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [c for _, c in scored]
        self._rankings = {str(c.candidate_id): s for s, c in scored}
        return ranked

    def _calculate_score(
        self,
        candidate: RecommendationCandidate,
        goals: list[RecommendationGoal],
        constraints: list[RecommendationConstraint],
    ) -> float:
        confidence_weight = 0.3
        priority_map = {
            "CRITICAL": 1.0,
            "HIGH": 0.8,
            "MEDIUM": 0.6,
            "LOW": 0.4,
            "OPTIONAL": 0.2,
        }
        priority_score = priority_map.get(
            candidate.priority.value if hasattr(candidate.priority, "value") else candidate.priority,
            0.5,
        )
        goal_alignment = 0.8 if goals else 0.5
        constraint_satisfaction = 0.7 if constraints else 0.5
        return round(
            confidence_weight * candidate.confidence
            + 0.3 * priority_score
            + 0.2 * goal_alignment
            + 0.2 * constraint_satisfaction,
            4,
        )

    def get_best(self, candidates: list[RecommendationCandidate]) -> RecommendationCandidate | None:
        """Get the highest-ranked candidate.

        Args:
            candidates: The ranked candidates.

        Returns:
            The best candidate, or None if the list is empty.
        """
        if not candidates:
            return None
        return candidates[0]

    def get_ranking_score(self, candidate_id: str) -> float | None:
        """Get the ranking score for a specific candidate.

        Args:
            candidate_id: The candidate identifier.

        Returns:
            The ranking score if found, None otherwise.
        """
        return self._rankings.get(candidate_id)

    def get_all_rankings(self) -> dict[str, float]:
        """Get all ranking scores.

        Returns:
            Dictionary mapping candidate IDs to scores.
        """
        return dict(self._rankings)

    def clear(self) -> None:
        """Clear all rankings."""
        self._rankings.clear()

    def count(self) -> int:
        """Get the number of ranked candidates.

        Returns:
            Ranking count.
        """
        return len(self._rankings)
