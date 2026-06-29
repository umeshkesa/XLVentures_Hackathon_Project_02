"""ReasoningConfidenceCalculator — computes confidence for reasoning results.

Produces ReasoningConfidence from evidence quality, hypothesis
strength, inference validity, contradiction resolution, path
consistency, risk level, impact score, uncertainty level,
ranking quality, goal alignment, and policy compliance.
Placeholder implementation using deterministic heuristics.
"""

from __future__ import annotations

import structlog

from adip.reasoning.contracts.models import ReasoningConfidence, ReasoningResult
from adip.reasoning.execution.models import (
    ImpactAssessment,
    RiskAssessment,
    UncertaintyAnalysis,
)

log = structlog.get_logger(__name__)


class ReasoningConfidenceCalculator:
    """Computes reasoning confidence across multiple dimensions."""

    def calculate(
        self,
        result: ReasoningResult,
        risks: dict[str, RiskAssessment] | None = None,
        impacts: dict[str, ImpactAssessment] | None = None,
        uncertainties: list[UncertaintyAnalysis] | None = None,
        ranking_scores: dict[str, float] | None = None,
    ) -> ReasoningConfidence:
        """Calculate confidence metrics for a reasoning result.

        Uses deterministic placeholder heuristics across 12 dimensions:
        - evidence_quality: based on number of hypotheses with supporting evidence
        - hypothesis_strength: average confidence of generated hypotheses
        - inference_validity: average confidence of drawn inferences
        - contradiction_resolution: inversely proportional to contradiction count
        - path_consistency: based on reasoning path count diversity
        - risk_level: 1.0 - average risk score (lower risk = higher confidence)
        - impact_score: average impact score (higher positive impact = higher confidence)
        - uncertainty_level: 1.0 - average criticality (lower uncertainty = higher confidence)
        - ranking_quality: average ranking score if provided
        - goal_alignment: placeholder — assumed aligned
        - policy_compliance: placeholder — assumed compliant
        - overall: weighted average of all dimensions
        """
        log.info("confidence.calculate", result_id=str(result.result_id))

        # Evidence quality: based on number of hypotheses with supporting evidence
        hypotheses_with_evidence = sum(
            1 for h in result.hypotheses if h.supporting_evidence
        )
        evidence_quality = min(
            1.0, hypotheses_with_evidence / max(1, len(result.hypotheses))
        )

        # Hypothesis strength: average confidence of all hypotheses
        hypothesis_strength = (
            sum(h.confidence for h in result.hypotheses) / max(1, len(result.hypotheses))
        )

        # Inference validity: average confidence of all inferences
        inference_validity = (
            sum(i.confidence for i in result.inferences) / max(1, len(result.inferences))
        )

        # Contradiction resolution: inversely proportional to count
        contradiction_count = len(result.contradictions)
        contradiction_resolution = max(0.0, 1.0 - contradiction_count * 0.25)

        # Path consistency: based on path count diversity
        path_count = len(result.paths)
        path_consistency = min(1.0, path_count / 5.0) if path_count > 0 else 0.5

        # Risk level: 1.0 - average risk score
        risks = risks or {}
        risk_scores = [r.score for r in risks.values()]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        risk_level = 1.0 - avg_risk

        # Impact score: average impact score
        impacts = impacts or {}
        impact_scores_list = [i.score for i in impacts.values()]
        impact_score = (
            sum(impact_scores_list) / len(impact_scores_list) if impact_scores_list else 0.0
        )

        # Uncertainty level: 1.0 - average criticality
        uncertainties = uncertainties or []
        unc_criticalities = [u.criticality for u in uncertainties]
        avg_criticality = (
            sum(unc_criticalities) / len(unc_criticalities) if unc_criticalities else 0.0
        )
        uncertainty_level = 1.0 - avg_criticality

        # Ranking quality: average ranking score
        ranking_scores = ranking_scores or {}
        ranking_values = list(ranking_scores.values())
        ranking_quality = (
            sum(ranking_values) / len(ranking_values) if ranking_values else 0.0
        )

        # Goal alignment: placeholder — assume aligned
        goal_alignment = 1.0

        # Policy compliance: placeholder — assume compliant
        policy_compliance = 1.0

        overall = (
            evidence_quality * 0.10
            + hypothesis_strength * 0.12
            + inference_validity * 0.10
            + contradiction_resolution * 0.10
            + path_consistency * 0.08
            + risk_level * 0.10
            + impact_score * 0.08
            + uncertainty_level * 0.08
            + ranking_quality * 0.08
            + goal_alignment * 0.08
            + policy_compliance * 0.08
        )

        confidence = ReasoningConfidence(
            overall_confidence=round(overall, 4),
            evidence_quality=round(evidence_quality, 4),
            hypothesis_strength=round(hypothesis_strength, 4),
            inference_validity=round(inference_validity, 4),
            contradiction_resolution=round(contradiction_resolution, 4),
            path_consistency=round(path_consistency, 4),
            goal_alignment=round(goal_alignment, 4),
            policy_compliance=round(policy_compliance, 4),
        )

        log.info(
            "confidence.calculate.complete",
            overall=confidence.overall_confidence,
        )
        return confidence
