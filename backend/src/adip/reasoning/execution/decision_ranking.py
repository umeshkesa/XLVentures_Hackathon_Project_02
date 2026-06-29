"""DecisionRanking — ranks decision alternatives by composite scores.

Ranks alternatives by confidence, risk, impact, constraint satisfaction,
cost, and multi-criteria weighted composite scoring.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.execution.models import DecisionComparison

log = structlog.get_logger(__name__)


class DecisionRanking:
    """Ranks decision alternatives using composite scores.

    Deterministic placeholder that combines confidence, risk,
    impact, constraint satisfaction, and cost into a unified
    ranking order.
    """

    def __init__(self) -> None:
        self._rankings: list[DecisionComparison] = []

    def rank_by_composite(
        self,
        comparisons: list[DecisionComparison],
    ) -> list[DecisionComparison]:
        """Rank alternatives by composite score (highest first).

        Args:
            comparisons: List of DecisionComparison to rank.

        Returns:
            Ranked list of DecisionComparison (highest composite score first).
        """
        ranked = sorted(comparisons, key=lambda c: c.composite_score, reverse=True)
        self._rankings = ranked
        log.info(
            "decision_ranking.rank_by_composite",
            count=len(ranked),
            best_score=ranked[0].composite_score if ranked else None,
        )
        return ranked

    def rank_by_confidence(
        self,
        comparisons: list[DecisionComparison],
    ) -> list[DecisionComparison]:
        """Rank alternatives by confidence score (highest first).

        Args:
            comparisons: List of DecisionComparison to rank.

        Returns:
            Ranked list of DecisionComparison (highest confidence first).
        """
        ranked = sorted(comparisons, key=lambda c: c.confidence_score, reverse=True)
        log.info("decision_ranking.rank_by_confidence", count=len(ranked))
        return ranked

    def rank_by_risk(
        self,
        comparisons: list[DecisionComparison],
    ) -> list[DecisionComparison]:
        """Rank alternatives by risk score (lowest first).

        Args:
            comparisons: List of DecisionComparison to rank.

        Returns:
            Ranked list of DecisionComparison (lowest risk first).
        """
        ranked = sorted(comparisons, key=lambda c: c.risk_score)
        log.info("decision_ranking.rank_by_risk", count=len(ranked))
        return ranked

    def rank_by_impact(
        self,
        comparisons: list[DecisionComparison],
    ) -> list[DecisionComparison]:
        """Rank alternatives by impact score (highest first).

        Args:
            comparisons: List of DecisionComparison to rank.

        Returns:
            Ranked list of DecisionComparison (highest impact first).
        """
        ranked = sorted(comparisons, key=lambda c: c.impact_score, reverse=True)
        log.info("decision_ranking.rank_by_impact", count=len(ranked))
        return ranked

    def get_top_n(
        self,
        comparisons: list[DecisionComparison],
        n: int = 1,
    ) -> list[DecisionComparison]:
        """Get the top N ranked alternatives.

        Args:
            comparisons: List of DecisionComparison to rank.
            n: Number of top alternatives to return.

        Returns:
            Top N ranked DecisionComparison objects.
        """
        ranked = self.rank_by_composite(comparisons)
        result = ranked[:max(1, n)]
        log.info("decision_ranking.top_n", n=len(result))
        return result

    def get_top_comparison(
        self,
        comparisons: list[DecisionComparison],
    ) -> DecisionComparison | None:
        """Get the single highest-ranked comparison.

        Args:
            comparisons: List of DecisionComparison to rank.

        Returns:
            The top DecisionComparison, or None if empty.
        """
        if not comparisons:
            return None
        top = self.rank_by_composite(comparisons)
        return top[0] if top else None

    def count(self) -> int:
        """Get the number of ranked comparisons.

        Returns:
            Ranking count.
        """
        return len(self._rankings)

    def clear(self) -> None:
        """Clear all stored rankings."""
        self._rankings.clear()
