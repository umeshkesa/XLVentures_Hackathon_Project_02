"""DecisionComparator — compares decision alternatives across multiple criteria.

Compares alternatives by confidence, risk, impact, constraints, cost,
and multi-criteria weighted scoring.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.execution.models import (
    DecisionComparison,
    ImpactAssessment,
    ReasoningAlternative,
    RiskAssessment,
)

log = structlog.get_logger(__name__)


class DecisionComparator:
    """Compares decision alternatives across multiple criteria.

    Deterministic placeholder that evaluates and ranks alternatives
    by confidence, risk, impact, constraints, cost, and weighted
    multi-criteria analysis.
    """

    def __init__(self) -> None:
        self._comparisons: list[DecisionComparison] = []

    def compare_by_confidence(
        self,
        alternatives: list[ReasoningAlternative],
    ) -> ReasoningAlternative | None:
        """Return the alternative with the highest confidence.

        Args:
            alternatives: List of alternatives to compare.

        Returns:
            Highest-confidence alternative, or None if empty.
        """
        if not alternatives:
            return None
        best = max(alternatives, key=lambda a: a.confidence)
        log.info("decision_comparator.by_confidence", best_id=str(best.alternative_id), confidence=best.confidence)
        return best

    def compare_by_risk(
        self,
        alternatives: list[ReasoningAlternative],
        risks: dict[str, RiskAssessment],
    ) -> ReasoningAlternative | None:
        """Return the alternative with the lowest risk.

        Args:
            alternatives: List of alternatives to compare.
            risks: Mapping of alternative ID to RiskAssessment.

        Returns:
            Lowest-risk alternative, or None if empty.
        """
        if not alternatives:
            return None
        best = min(
            alternatives,
            key=lambda a: risks.get(str(a.alternative_id), RiskAssessment()).score,
        )
        log.info("decision_comparator.by_risk", best_id=str(best.alternative_id))
        return best

    def compare_by_impact(
        self,
        alternatives: list[ReasoningAlternative],
        impacts: dict[str, ImpactAssessment],
    ) -> ReasoningAlternative | None:
        """Return the alternative with the highest impact.

        Args:
            alternatives: List of alternatives to compare.
            impacts: Mapping of alternative ID to ImpactAssessment.

        Returns:
            Highest-impact alternative, or None if empty.
        """
        if not alternatives:
            return None
        best = max(
            alternatives,
            key=lambda a: impacts.get(str(a.alternative_id), ImpactAssessment()).score,
        )
        log.info("decision_comparator.by_impact", best_id=str(best.alternative_id))
        return best

    def compare_by_constraints(
        self,
        alternatives: list[ReasoningAlternative],
        constraint_satisfaction: dict[str, float],
    ) -> ReasoningAlternative | None:
        """Return the alternative with the highest constraint satisfaction.

        Args:
            alternatives: List of alternatives to compare.
            constraint_satisfaction: Mapping of alternative ID to satisfaction (0.0–1.0).

        Returns:
            Best-constrained alternative, or None if empty.
        """
        if not alternatives:
            return None
        best = max(
            alternatives,
            key=lambda a: constraint_satisfaction.get(str(a.alternative_id), 0.0),
        )
        log.info("decision_comparator.by_constraints", best_id=str(best.alternative_id))
        return best

    def compare_by_cost(
        self,
        alternatives: list[ReasoningAlternative],
        costs: dict[str, float],
    ) -> ReasoningAlternative | None:
        """Return the alternative with the lowest cost.

        Args:
            alternatives: List of alternatives to compare.
            costs: Mapping of alternative ID to cost value.

        Returns:
            Lowest-cost alternative, or None if empty.
        """
        if not alternatives:
            return None
        best = min(
            alternatives,
            key=lambda a: costs.get(str(a.alternative_id), 0.0),
        )
        log.info("decision_comparator.by_cost", best_id=str(best.alternative_id))
        return best

    def compare_all(
        self,
        alternatives: list[ReasoningAlternative],
        risks: dict[str, RiskAssessment] | None = None,
        impacts: dict[str, ImpactAssessment] | None = None,
        constraint_satisfaction: dict[str, float] | None = None,
        costs: dict[str, float] | None = None,
        weights: dict[str, float] | None = None,
    ) -> tuple[list[DecisionComparison], ReasoningAlternative | None]:
        """Multi-criteria comparison with weighted scoring.

        Each alternative receives a composite score based on
        confidence, risk (inverted), impact, constraint satisfaction,
        and cost (inverted) weighted by the provided weights.

        Args:
            alternatives: List of alternatives to compare.
            risks: Mapping of alternative ID to RiskAssessment.
            impacts: Mapping of alternative ID to ImpactAssessment.
            constraint_satisfaction: Mapping of alternative ID to satisfaction (0.0–1.0).
            costs: Mapping of alternative ID to cost value.
            weights: Criteria weights dict with keys: confidence, risk, impact,
                     constraint, cost (defaults to equal weights).

        Returns:
            Tuple of (ranked DecisionComparison list, best alternative or None).
        """
        if not alternatives:
            return [], None

        resolved_weights = weights or {}
        w_conf = resolved_weights.get("confidence", 0.25)
        w_risk = resolved_weights.get("risk", 0.20)
        w_impact = resolved_weights.get("impact", 0.20)
        w_constraint = resolved_weights.get("constraint", 0.20)
        w_cost = resolved_weights.get("cost", 0.15)

        total_w = w_conf + w_risk + w_impact + w_constraint + w_cost
        if total_w > 0:
            w_conf /= total_w
            w_risk /= total_w
            w_impact /= total_w
            w_constraint /= total_w
            w_cost /= total_w

        risks = risks or {}
        impacts = impacts or {}
        constraint_satisfaction = constraint_satisfaction or {}
        costs = costs or {}

        comparisons: list[DecisionComparison] = []
        for alt in alternatives:
            alt_id = str(alt.alternative_id)
            risk_score = risks.get(alt_id, RiskAssessment()).score
            impact_score = impacts.get(alt_id, ImpactAssessment()).score
            constraint_score = constraint_satisfaction.get(alt_id, 0.5)
            cost_score = costs.get(alt_id, 0.5)

            composite = (
                w_conf * alt.confidence
                + w_risk * (1.0 - risk_score)
                + w_impact * impact_score
                + w_constraint * constraint_score
                + w_cost * (1.0 - cost_score)
            )

            comparisons.append(DecisionComparison(
                alternative_id=str(alt.alternative_id),
                confidence_score=alt.confidence,
                risk_score=risk_score,
                impact_score=impact_score,
                constraint_score=constraint_score,
                cost_score=cost_score,
                composite_score=round(composite, 4),
            ))

        comparisons.sort(key=lambda c: c.composite_score, reverse=True)
        self._comparisons = comparisons

        best = next(
            (a for a in alternatives if str(a.alternative_id) == comparisons[0].alternative_id),
            None,
        )
        log.info(
            "decision_comparator.compare_all",
            count=len(comparisons),
            best_id=str(best.alternative_id) if best else None,
        )
        return comparisons, best

    def get_best_by_criteria(
        self,
        criteria: str,
        alternatives: list[ReasoningAlternative],
        scores: dict[str, float],
    ) -> ReasoningAlternative | None:
        """Return the best alternative by a given criteria.

        Args:
            criteria: The criteria name (for logging).
            alternatives: List of alternatives.
            scores: Mapping of alternative ID to score.

        Returns:
            Best alternative, or None if empty.
        """
        if not alternatives:
            return None
        best = max(
            alternatives,
            key=lambda a: scores.get(str(a.alternative_id), 0.0),
        )
        log.info("decision_comparator.best_by_criteria", criteria=criteria, best_id=str(best.alternative_id))
        return best

    def count(self) -> int:
        """Get the number of comparisons performed.

        Returns:
            Comparison count.
        """
        return len(self._comparisons)

    def clear(self) -> None:
        """Clear all stored comparisons."""
        self._comparisons.clear()
        log.info("decision_comparator.cleared")
