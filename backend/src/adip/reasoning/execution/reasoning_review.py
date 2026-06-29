"""ReasoningReview — reviews reasoning quality across multiple dimensions.

Validates goals, constraints, assumptions, contradictions, risks,
alternatives, and confidence to produce a comprehensive review result.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.reasoning.contracts.models import Contradiction, ReasoningConfidence
from adip.reasoning.execution.models import (
    Assumption,
    Constraint,
    ReasoningAlternative,
    ReasoningGoal,
    ReviewResult,
    RiskAssessment,
)

log = structlog.get_logger(__name__)


class ReasoningReview:
    """Reviews reasoning quality across multiple dimensions.

    Deterministic placeholder that validates goals, constraints,
    assumptions, contradictions, risks, alternatives, and confidence
    to produce a comprehensive review result.
    """

    def review_goals(
        self,
        goals: list[ReasoningGoal],
    ) -> dict[str, Any]:
        """Validate goals — must have at least 1, primary must exist.

        Args:
            goals: List of reasoning goals to review.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if not goals:
            errors.append("No goals defined")
        else:
            if len(goals) < 1:
                errors.append("At least one goal is required")
            if not any(g.is_primary for g in goals):
                warnings.append("No primary goal defined")

        score = 0.0 if errors else (0.5 if warnings else 1.0)
        log.info(
            "reasoning_review.review_goals",
            goal_count=len(goals),
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def review_constraints(
        self,
        constraints: list[Constraint],
    ) -> dict[str, Any]:
        """Validate constraints — checks for hard/soft balance.

        Args:
            constraints: List of constraints to review.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if not constraints:
            warnings.append("No constraints defined")
        else:
            hard_count = sum(1 for c in constraints if c.is_hard)
            soft_count = sum(1 for c in constraints if not c.is_hard)
            if hard_count > 0 and soft_count == 0:
                warnings.append("No soft constraints defined — all constraints are hard")
            if soft_count > 0 and hard_count == 0:
                warnings.append("No hard constraints defined — all constraints are soft")

        score = 0.5 if warnings else 1.0
        log.info(
            "reasoning_review.review_constraints",
            constraint_count=len(constraints),
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def review_assumptions(
        self,
        assumptions: list[Assumption],
    ) -> dict[str, Any]:
        """Validate assumptions — checks for invalidated.

        Args:
            assumptions: List of assumptions to review.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if not assumptions:
            warnings.append("No assumptions defined")
        else:
            invalidated = [a for a in assumptions if a.status == "INVALIDATED"]
            if invalidated:
                warnings.append(
                    f"{len(invalidated)} assumption(s) have been invalidated"
                )

        score = 0.5 if warnings else 1.0
        log.info(
            "reasoning_review.review_assumptions",
            assumption_count=len(assumptions),
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def review_contradictions(
        self,
        contradictions: list[Contradiction],
    ) -> dict[str, Any]:
        """Validate contradictions — checks resolution status.

        Args:
            contradictions: List of contradictions to review.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if not contradictions:
            warnings.append("No contradictions detected")
        else:
            unresolved = [
                c for c in contradictions
                if c.resolution_status == "UNRESOLVED"
            ]
            if unresolved:
                warnings.append(
                    f"{len(unresolved)} contradiction(s) remain unresolved"
                )

        score = 0.5 if warnings else 1.0
        log.info(
            "reasoning_review.review_contradictions",
            contradiction_count=len(contradictions),
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def review_risks(
        self,
        risks: dict[str, RiskAssessment],
    ) -> dict[str, Any]:
        """Validate risks — flags HIGH/CRITICAL.

        Args:
            risks: Mapping of risk type to RiskAssessment.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if not risks:
            warnings.append("No risks assessed")
        else:
            high_risks = [
                (rtype, r) for rtype, r in risks.items()
                if r.level in ("HIGH", "CRITICAL")
            ]
            if high_risks:
                warnings.append(
                    f"{len(high_risks)} risk(s) flagged as HIGH or CRITICAL"
                )

        score = 0.5 if warnings else 1.0
        log.info(
            "reasoning_review.review_risks",
            risk_count=len(risks),
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def review_alternatives(
        self,
        alternatives: list[ReasoningAlternative],
    ) -> dict[str, Any]:
        """Validate alternatives — must have candidates.

        Args:
            alternatives: List of alternatives to review.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if not alternatives:
            errors.append("No alternatives generated")
        else:
            evaluated = [a for a in alternatives if a.status == "EVALUATED"]
            if not evaluated:
                warnings.append("No alternatives have been evaluated")

        score = 0.0 if errors else (0.5 if warnings else 1.0)
        log.info(
            "reasoning_review.review_alternatives",
            alternative_count=len(alternatives),
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def review_confidence(
        self,
        confidence: ReasoningConfidence | None,
    ) -> dict[str, Any]:
        """Validate confidence — flags if below 0.5.

        Args:
            confidence: The ReasoningConfidence to review, or None.

        Returns:
            Review dict with passed, score, warnings, errors.
        """
        warnings: list[str] = []
        errors: list[str] = []

        if confidence is None:
            errors.append("No confidence assessment available")
        else:
            if confidence.overall_confidence < 0.5:
                warnings.append(
                    f"Overall confidence is low ({confidence.overall_confidence:.2f})"
                )

        score = 0.0 if errors else (0.5 if warnings else 1.0)
        log.info(
            "reasoning_review.review_confidence",
            has_confidence=confidence is not None,
            passed=len(errors) == 0,
        )
        return {
            "passed": len(errors) == 0,
            "score": score,
            "warnings": warnings,
            "errors": errors,
        }

    def perform_full_review(
        self,
        goals: list[ReasoningGoal] | None = None,
        constraints: list[Constraint] | None = None,
        assumptions: list[Assumption] | None = None,
        contradictions: list[Contradiction] | None = None,
        risks: dict[str, RiskAssessment] | None = None,
        alternatives: list[ReasoningAlternative] | None = None,
        confidence: ReasoningConfidence | None = None,
    ) -> ReviewResult:
        """Run all reviews and aggregate into a ReviewResult.

        Args:
            goals: Optional goals to review.
            constraints: Optional constraints to review.
            assumptions: Optional assumptions to review.
            contradictions: Optional contradictions to review.
            risks: Optional risks to review.
            alternatives: Optional alternatives to review.
            confidence: Optional confidence to review.

        Returns:
            Aggregated ReviewResult containing all review outputs.
        """
        goal_review = self.review_goals(goals or [])
        constraint_review = self.review_constraints(constraints or [])
        assumption_review = self.review_assumptions(assumptions or [])
        contradiction_review = self.review_contradictions(contradictions or [])
        risk_review = self.review_risks(risks or {})
        alternative_review = self.review_alternatives(alternatives or [])
        confidence_review = self.review_confidence(confidence)

        reviews = [
            goal_review,
            constraint_review,
            assumption_review,
            contradiction_review,
            risk_review,
            alternative_review,
            confidence_review,
        ]
        scores = [r["score"] for r in reviews]
        overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0

        all_warnings: list[str] = []
        all_errors: list[str] = []
        for r in reviews:
            all_warnings.extend(r.get("warnings", []))
            all_errors.extend(r.get("errors", []))

        passed = overall_score >= 0.7 and len(all_errors) == 0

        result = ReviewResult(
            passed=passed,
            overall_score=overall_score,
            goal_review=goal_review,
            constraint_review=constraint_review,
            assumption_review=assumption_review,
            contradiction_review=contradiction_review,
            risk_review=risk_review,
            alternative_review=alternative_review,
            confidence_review=confidence_review,
            warnings=all_warnings,
            errors=all_errors,
        )
        log.info(
            "reasoning_review.perform_full_review",
            review_id=str(result.review_id),
            passed=passed,
            overall_score=overall_score,
        )
        return result
