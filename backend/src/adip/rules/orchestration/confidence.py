"""RuleConfidenceCalculator — computes confidence and quality scores.

Produces RuleConfidence from rule completeness, version freshness,
conflict resolution quality, policy compliance, and evaluation
coverage. Placeholder implementation using deterministic heuristics.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import RuleConfidence, RuleEvaluation

log = structlog.get_logger(__name__)


class RuleConfidenceCalculator:
    """Computes confidence, completeness, freshness, lifecycle validity,
    conflict quality, policy compliance, and evaluation coverage scores."""

    def calculate(self, evaluation: RuleEvaluation) -> RuleConfidence:
        """Calculate confidence metrics for a rule evaluation.

        Uses deterministic placeholder heuristics:
        - rule_completeness: proportion of rules with conditions
        - version_freshness: decays with distance from version 1
        - lifecycle_validity: based on lifecycle status of evaluated rules
        - conflict_quality: inversely proportional to conflict count
        - policy_compliance: based on evaluation status
        - evaluation_coverage: proportion of rules that produced decisions
        - overall: weighted average of all sub-scores
        """
        log.info("rule_confidence.calculate", rules_evaluated=len(evaluation.rules_evaluated))

        if not evaluation.rules_evaluated:
            return RuleConfidence()

        # Rule completeness: proportion of rules with decisions
        completeness = min(1.0, len(evaluation.decisions) / max(1, len(evaluation.rules_evaluated)))

        # Version freshness: placeholder — assume version 1
        freshness = 1.0

        # Lifecycle validity: placeholder — assume valid
        lifecycle_validity = 1.0

        # Conflict quality: inversely proportional to conflict count
        conflict_count = len(evaluation.conflicts_detected)
        conflict_quality = max(0.0, 1.0 - conflict_count * 0.2)

        # Policy compliance: based on evaluation status
        compliance = 1.0 if evaluation.status == "COMPLETED" else 0.5

        # Evaluation coverage: proportion of rules that produced decisions
        coverage = completeness

        overall = (
            completeness * 0.20
            + freshness * 0.10
            + lifecycle_validity * 0.15
            + conflict_quality * 0.20
            + compliance * 0.20
            + coverage * 0.15
        )

        confidence = RuleConfidence(
            overall_confidence=round(overall, 4),
            rule_completeness=round(completeness, 4),
            version_freshness=round(freshness, 4),
            lifecycle_validity=round(lifecycle_validity, 4),
            conflict_quality=round(conflict_quality, 4),
            policy_compliance=round(compliance, 4),
            evaluation_coverage=round(coverage, 4),
        )

        log.info("rule_confidence.calculate.complete", overall_confidence=confidence.overall_confidence)
        return confidence
