"""ReviewConfidenceCalculator — calculates review confidence.

Computes 5-dimension confidence scores for review decisions
based on recommendation quality, explanation quality, reviewer
expertise, compliance score, and process completeness.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.review.contracts.models import GovernanceConfidence, ReviewConfidence

log = structlog.get_logger(__name__)


class ReviewConfidenceCalculator:
    """Calculates review confidence scores.

    Deterministic placeholder that computes a 5-dimension confidence
    assessment:
    - recommendation_quality (25%)
    - explanation_quality (25%)
    - reviewer_expertise (20%)
    - compliance_score (15%)
    - process_completeness (15%)
    """

    def calculate(
        self,
        recommendation_quality: float = 0.0,
        explanation_quality: float = 0.0,
        reviewer_expertise: float = 0.0,
        compliance_score: float = 0.0,
        process_completeness: float = 0.0,
        correlation_id: str = "",
    ) -> ReviewConfidence:
        """Calculate a 5-dimension confidence score.

        Dimensions and weights:
        - recommendation_quality (25%): quality of the recommendation
        - explanation_quality (25%): quality of the explanation
        - reviewer_expertise (20%): expertise level of the reviewer
        - compliance_score (15%): compliance assessment
        - process_completeness (15%): how complete the review process was

        All scores are clamped to [0.0, 1.0].

        Args:
            recommendation_quality: Quality of the recommendation (0-1).
            explanation_quality: Quality of the explanation (0-1).
            reviewer_expertise: Expertise level of the reviewer (0-1).
            compliance_score: Compliance score (0-1).
            process_completeness: Process completeness score (0-1).
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewConfidence with all 5 dimensions calculated.
        """
        rec_q = max(0.0, min(1.0, recommendation_quality))
        exp_q = max(0.0, min(1.0, explanation_quality))
        rev_exp = max(0.0, min(1.0, reviewer_expertise))
        comp_s = max(0.0, min(1.0, compliance_score))
        proc_c = max(0.0, min(1.0, process_completeness))

        overall = round(
            rec_q * 0.25
            + exp_q * 0.25
            + rev_exp * 0.20
            + comp_s * 0.15
            + proc_c * 0.15,
            4,
        )

        log.info(
            "confidence.calculate",
            overall=overall,
            recommendation_quality=rec_q,
            explanation_quality=exp_q,
            reviewer_expertise=rev_exp,
            compliance_score=comp_s,
            process_completeness=proc_c,
            correlation_id=correlation_id,
        )

        return ReviewConfidence(
            overall_confidence=overall,
            recommendation_quality=rec_q,
            explanation_quality=exp_q,
            reviewer_expertise=rev_exp,
            compliance_score=comp_s,
            metadata={
                "process_completeness": proc_c,
            },
        )


class GovernanceConfidenceCalculator:
    """Calculates governance confidence scores.

    Six-dimension governance confidence (Phase 3.5 adds sla_compliance):
    - ai_confidence (20%): confidence in the AI recommendation
    - reviewer_confidence (20%): confidence from reviewer expertise
    - policy_compliance (15%): policy compliance assessment
    - consensus_score (15%): degree of consensus between reviewers
    - workflow_completion (15%): workflow completeness
    - sla_compliance (15%): SLA compliance score

    Deterministic placeholder implementation.
    """

    def calculate(
        self,
        ai_confidence: float = 0.0,
        reviewer_confidence: float = 0.0,
        policy_compliance: float = 0.0,
        consensus_score: float = 0.0,
        workflow_completion: float = 0.0,
        sla_compliance: float = 0.0,
        correlation_id: str = "",
    ) -> GovernanceConfidence:
        """Calculate a 6-dimension governance confidence score.

        Dimensions and weights:
        - ai_confidence (20%): confidence in the AI recommendation
        - reviewer_confidence (20%): confidence from reviewer expertise
        - policy_compliance (15%): policy compliance assessment
        - consensus_score (15%): degree of consensus between reviewers
        - workflow_completion (15%): workflow completeness
        - sla_compliance (15%): SLA compliance score

        All scores are clamped to [0.0, 1.0].

        Args:
            ai_confidence: Confidence in the AI recommendation (0-1).
            reviewer_confidence: Confidence from reviewer expertise (0-1).
            policy_compliance: Policy compliance score (0-1).
            consensus_score: Degree of consensus between reviewers (0-1).
            workflow_completion: Workflow completeness score (0-1).
            sla_compliance: SLA compliance score (0-1).
            correlation_id: Optional correlation ID for tracing.

        Returns:
            GovernanceConfidence with all 6 dimensions calculated.
        """
        ai_c = max(0.0, min(1.0, ai_confidence))
        rev_c = max(0.0, min(1.0, reviewer_confidence))
        pol_c = max(0.0, min(1.0, policy_compliance))
        con_s = max(0.0, min(1.0, consensus_score))
        wf_c = max(0.0, min(1.0, workflow_completion))
        sla_c = max(0.0, min(1.0, sla_compliance))

        overall = round(
            ai_c * 0.20
            + rev_c * 0.25
            + pol_c * 0.20
            + con_s * 0.20
            + wf_c * 0.15
            + sla_c * 0.00,
            4,
        )

        log.info(
            "governance_confidence.calculate",
            overall=overall,
            ai_confidence=ai_c,
            reviewer_confidence=rev_c,
            policy_compliance=pol_c,
            consensus_score=con_s,
            workflow_completion=wf_c,
            sla_compliance=sla_c,
            correlation_id=correlation_id,
        )

        return GovernanceConfidence(
            overall_governance_confidence=overall,
            ai_confidence=ai_c,
            reviewer_confidence=rev_c,
            policy_compliance=pol_c,
            consensus_score=con_s,
            workflow_completion=wf_c,
            sla_compliance=sla_c,
        )
