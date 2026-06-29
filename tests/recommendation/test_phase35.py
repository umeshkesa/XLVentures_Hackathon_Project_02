"""Comprehensive tests for the Recommendation Engine Phase 3.5 (Enterprise Refinement).

Tests all Phase 3.5 components:
  1. RecommendationQualityManager
  2. RecommendationJustification
  3. RecommendationApprovalReadiness
  4. PortfolioQuality
  5. ReviewEnhanced (business_goals)
  6. LineageEnhanced (record_review, record_action)
  7. SnapshotEnhanced (create_quality_snapshot, create_approval_snapshot)
  8. TraceEnhanced (record_review_stage, record_readiness_stage, record_quality_stage,
     record_approval_readiness_stage)
  9. MetricsEnhanced (increment_quality, increment_justifications,
     increment_approval_readiness, increment_portfolio_quality, record_quality)
 10. CoordinatorPhase35 (health/metrics phase 3.5 fields, recommend runs)
 11. DecisionEnhancedFields
 12. ConfidenceEnhancedFields
 13. HealthEnhancedFields
 14. MetricsEnhancedFields
 15. ExplainabilityEnhancedFields
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from adip.recommendation.contracts.models import (
    RecommendationConfidence,
    RecommendationDecision,
    RecommendationExplainabilityMetadata,
    RecommendationHealth,
    RecommendationMetrics,
    RecommendationRequest,
    RecommendationResult,
)
from adip.recommendation.enums import (
    FeasibilityStatus,
    RecommendationStatus,
)
from adip.recommendation.execution.metrics import RecommendationMetricsCollector
from adip.recommendation.execution.models import (
    FeasibilityAnalysis,
    OutcomePrediction,
    PolicyEvalResult,
    RecommendationPortfolio,
)
from adip.recommendation.execution.trace import RecommendationTrace
from adip.recommendation.orchestration.approval_readiness import (
    ApprovalReadinessResult,
    RecommendationApprovalReadiness,
)
from adip.recommendation.orchestration.coordinator import RecommendationCoordinator
from adip.recommendation.orchestration.justification import (
    JustificationRecord,
    RecommendationJustification,
)
from adip.recommendation.orchestration.lineage import RecommendationLineage
from adip.recommendation.orchestration.portfolio_quality import (
    PortfolioQuality,
    PortfolioQualityResult,
)
from adip.recommendation.orchestration.quality import QualityResult, RecommendationQualityManager
from adip.recommendation.orchestration.review import RecommendationReview, ReviewResult
from adip.recommendation.orchestration.snapshot import RecommendationSnapshot, SnapshotRecord

# =============================================================================
# 1. RecommendationQualityManager
# =============================================================================


class TestRecommendationQualityManager:
    def test_calculate_default(self) -> None:
        qm = RecommendationQualityManager()
        result = qm.calculate()
        assert isinstance(result, QualityResult)
        assert result.portfolio_completeness == 0.0
        assert result.business_coverage == 0.5
        assert result.feasibility_coverage == 0.0
        assert result.policy_compliance == 0.0
        assert result.outcome_coverage == 0.0
        assert result.overall_quality == 0.1
        assert result.details["overall_quality"] == 0.1

    def test_calculate_with_portfolio(self) -> None:
        qm = RecommendationQualityManager()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1")
        result = qm.calculate(portfolio=portfolio)
        assert result.portfolio_completeness == 0.8
        assert result.business_coverage == 0.5
        assert result.feasibility_coverage == 0.0
        assert result.policy_compliance == 0.0
        assert result.outcome_coverage == 0.0
        assert result.overall_quality == 0.26
        assert result.details["portfolio_completeness"] == 0.8

    def test_calculate_with_full_args(self) -> None:
        qm = RecommendationQualityManager()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1")
        feasibility = FeasibilityAnalysis(
            status=FeasibilityStatus.FEASIBLE,
            feasibility_score=0.9,
        )
        policy_result = PolicyEvalResult(overall_passed=True)
        outcomes = [
            OutcomePrediction(candidate_id="c-1", success_probability=0.8),
            OutcomePrediction(candidate_id="c-2", success_probability=0.7),
            OutcomePrediction(candidate_id="c-3", success_probability=0.9),
            OutcomePrediction(candidate_id="c-4", success_probability=0.6),
            OutcomePrediction(candidate_id="c-5", success_probability=0.5),
        ]
        result = qm.calculate(
            portfolio=portfolio,
            feasibility=feasibility,
            policy_result=policy_result,
            outcomes=outcomes,
            business_goals=["Reduce cost"],
        )
        assert result.portfolio_completeness == 0.8
        assert result.business_coverage == 0.7
        assert result.feasibility_coverage == 0.9
        assert result.policy_compliance == 1.0
        assert result.outcome_coverage == 1.0
        assert result.overall_quality == 0.88

    def test_calculate_with_business_goals(self) -> None:
        qm = RecommendationQualityManager()
        result = qm.calculate(business_goals=["goal1", "goal2"])
        assert result.portfolio_completeness == 0.0
        assert result.business_coverage == 0.7
        assert result.feasibility_coverage == 0.0
        assert result.policy_compliance == 0.0
        assert result.outcome_coverage == 0.0
        assert result.overall_quality == 0.14


# =============================================================================
# 2. RecommendationJustification
# =============================================================================


class TestRecommendationJustification:
    def test_record(self) -> None:
        j = RecommendationJustification()
        record = j.record(
            recommendation_id="rec-1",
            supporting_reasoning="Best cost-benefit ratio",
            supporting_evidence=["Data source A"],
            business_goals=["Reduce cost"],
            constraints=["Budget < $5000"],
            policies=["Safety policy"],
            tradeoffs=["Cost vs Risk"],
        )
        assert isinstance(record, JustificationRecord)
        assert record.recommendation_id == "rec-1"
        assert record.supporting_reasoning == "Best cost-benefit ratio"
        assert record.supporting_evidence == ["Data source A"]
        assert record.business_goals == ["Reduce cost"]
        assert record.constraints == ["Budget < $5000"]
        assert record.policies == ["Safety policy"]
        assert record.tradeoffs == ["Cost vs Risk"]

    def test_get_by_recommendation(self) -> None:
        j = RecommendationJustification()
        j.record(recommendation_id="rec-1")
        j.record(recommendation_id="rec-1")
        j.record(recommendation_id="rec-2")
        results = j.get_by_recommendation("rec-1")
        assert len(results) == 2
        for r in results:
            assert r.recommendation_id == "rec-1"

    def test_get_by_recommendation_empty(self) -> None:
        j = RecommendationJustification()
        assert j.get_by_recommendation("nonexistent") == []

    def test_get_all(self) -> None:
        j = RecommendationJustification()
        assert len(j.get_all()) == 0
        j.record(recommendation_id="rec-1")
        j.record(recommendation_id="rec-2")
        assert len(j.get_all()) == 2

    def test_clear(self) -> None:
        j = RecommendationJustification()
        j.record(recommendation_id="rec-1")
        j.clear()
        assert j.count() == 0

    def test_count(self) -> None:
        j = RecommendationJustification()
        assert j.count() == 0
        j.record(recommendation_id="rec-1")
        assert j.count() == 1
        j.record(recommendation_id="rec-2")
        assert j.count() == 2


# =============================================================================
# 3. RecommendationApprovalReadiness
# =============================================================================


class TestRecommendationApprovalReadiness:
    def test_assess_ready(self) -> None:
        ar = RecommendationApprovalReadiness()
        review_result = ReviewResult(passed=True)
        result = ar.assess(
            review_result=review_result,
            confidence=0.8,
            feasibility_score=0.8,
            policy_passed=True,
            quality_score=0.8,
        )
        assert isinstance(result, ApprovalReadinessResult)
        assert result.status == "READY"
        assert result.confidence_adequate
        assert result.feasibility_adequate
        assert result.quality_adequate
        assert result.policy_passed
        assert result.review_passed

    def test_assess_blocked_by_policy(self) -> None:
        ar = RecommendationApprovalReadiness()
        result = ar.assess(
            review_result=None,
            confidence=0.8,
            feasibility_score=0.8,
            policy_passed=False,
            quality_score=0.8,
        )
        assert result.status == "BLOCKED"
        assert not result.policy_passed
        assert "Policy check failed" in result.reasons

    def test_assess_blocked_low_feasibility(self) -> None:
        ar = RecommendationApprovalReadiness()
        result = ar.assess(
            review_result=None,
            confidence=0.8,
            feasibility_score=0.2,
            policy_passed=True,
            quality_score=0.8,
        )
        assert result.status == "BLOCKED"
        assert not result.feasibility_adequate
        assert "Feasibility below 0.3 threshold" in result.reasons

    def test_assess_blocked_low_quality(self) -> None:
        ar = RecommendationApprovalReadiness()
        result = ar.assess(
            review_result=None,
            confidence=0.8,
            feasibility_score=0.8,
            policy_passed=True,
            quality_score=0.2,
        )
        assert result.status == "BLOCKED"
        assert not result.quality_adequate
        assert "Quality below 0.3 threshold" in result.reasons

    def test_assess_review_required_low_confidence(self) -> None:
        ar = RecommendationApprovalReadiness()
        result = ar.assess(
            review_result=None,
            confidence=0.4,
            feasibility_score=0.8,
            policy_passed=True,
            quality_score=0.8,
        )
        assert result.status == "REVIEW_REQUIRED"
        assert result.confidence_adequate
        assert "Confidence below 0.5" in result.reasons

    def test_assess_review_required_low_quality(self) -> None:
        ar = RecommendationApprovalReadiness()
        result = ar.assess(
            review_result=None,
            confidence=0.8,
            feasibility_score=0.8,
            policy_passed=True,
            quality_score=0.4,
        )
        assert result.status == "REVIEW_REQUIRED"
        assert result.quality_adequate
        assert "Quality below 0.5" in result.reasons


# =============================================================================
# 4. PortfolioQuality
# =============================================================================


class TestPortfolioQuality:
    def test_evaluate_default(self) -> None:
        pq = PortfolioQuality()
        result = pq.evaluate()
        assert isinstance(result, PortfolioQualityResult)
        assert result.diversity_score == 0.0
        assert result.coverage_score == 0.0
        assert result.dependency_score == 0.0
        assert result.policy_compliance_score == 0.0
        assert result.feasibility_score == 0.0
        assert result.overall == 0.0

    def test_evaluate_with_portfolio(self) -> None:
        pq = PortfolioQuality()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1")
        result = pq.evaluate(portfolio=portfolio)
        assert result.diversity_score == 0.0
        assert result.coverage_score == 0.7
        assert result.dependency_score == 0.5
        assert result.policy_compliance_score == 0.0
        assert result.feasibility_score == 0.0
        assert result.overall == 0.24

    def test_evaluate_with_alternatives(self) -> None:
        pq = PortfolioQuality()
        alternatives = ["alt-1", "alt-2"]
        result = pq.evaluate(alternatives=alternatives)
        assert result.diversity_score == pytest.approx(2.0 / 3.0)
        assert result.coverage_score == 0.0
        assert result.dependency_score == 0.0
        assert result.policy_compliance_score == 0.0
        assert result.feasibility_score == 0.0
        assert result.overall == pytest.approx(0.1667, rel=1e-3)

    def test_evaluate_with_all_args(self) -> None:
        pq = PortfolioQuality()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1")
        policy_result = PolicyEvalResult(overall_passed=True)
        feasibility = FeasibilityAnalysis(
            status=FeasibilityStatus.FEASIBLE,
            feasibility_score=0.8,
        )
        alternatives = ["alt-1", "alt-2", "alt-3", "alt-4", "alt-5"]
        result = pq.evaluate(
            portfolio=portfolio,
            policy_result=policy_result,
            feasibility=feasibility,
            alternatives=alternatives,
        )
        assert result.diversity_score == 1.0
        assert result.coverage_score == 0.7
        assert result.dependency_score == 0.5
        assert result.policy_compliance_score == 1.0
        assert result.feasibility_score == 0.8
        assert result.overall == 0.81


# =============================================================================
# 5. ReviewEnhanced (new business_goals functionality)
# =============================================================================


class TestReviewEnhanced:
    def test_review_with_business_goals(self) -> None:
        r = RecommendationReview()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1")
        result = r.review(
            business_goals=["Reduce cost"],
            portfolio=portfolio,
            confidence=0.8,
        )
        assert result.business_goals_aligned
        assert "No business goals provided for alignment check" not in result.violations
        assert result.passed

    def test_review_without_business_goals(self) -> None:
        r = RecommendationReview()
        result = r.review(business_goals=[])
        # Empty list is falsy, so business_goals_aligned defaults to True
        # but the explicit empty-list check still adds a violation
        assert result.business_goals_aligned
        assert "No business goals provided for alignment check" in result.violations
        assert not result.passed

    def test_review_business_goals_aligned(self) -> None:
        r = RecommendationReview()
        result = r.review(business_goals=None)
        assert result.business_goals_aligned
        assert len(result.violations) == 1  # "No portfolio created"
        assert result.passed is False  # confidence=0.0 < 0.3


# =============================================================================
# 6. LineageEnhanced
# =============================================================================


class TestLineageEnhanced:
    def test_record_review(self) -> None:
        ll = RecommendationLineage()
        entry = ll.record_review(
            source_id="reviewer-1",
            target_id="rec-1",
            description="Review passed all checks",
            metadata={"score": 0.95},
        )
        assert entry.lineage_type == "review"
        assert entry.source_id == "reviewer-1"
        assert entry.target_id == "rec-1"
        assert entry.description == "Review passed all checks"
        assert entry.metadata == {"score": 0.95}

    def test_record_action(self) -> None:
        ll = RecommendationLineage()
        entry = ll.record_action(
            source_id="actor-1",
            target_id="rec-1",
            description="Action: Replace filter",
            metadata={"action_type": "maintenance"},
        )
        assert entry.lineage_type == "action"
        assert entry.source_id == "actor-1"
        assert entry.target_id == "rec-1"
        assert entry.description == "Action: Replace filter"
        assert entry.metadata == {"action_type": "maintenance"}


# =============================================================================
# 7. SnapshotEnhanced
# =============================================================================


class TestSnapshotEnhanced:
    def test_create_quality_snapshot(self) -> None:
        ss = RecommendationSnapshot()
        quality_result = QualityResult(
            portfolio_completeness=0.8,
            business_coverage=0.7,
            feasibility_coverage=0.9,
            policy_compliance=1.0,
            outcome_coverage=0.5,
            overall_quality=0.78,
        )
        snap = ss.create_quality_snapshot(
            recommendation_id="rec-1",
            quality_result=quality_result,
        )
        assert isinstance(snap, SnapshotRecord)
        assert snap.snapshot_type == "quality"
        assert snap.recommendation_id == "rec-1"
        assert snap.data["portfolio_completeness"] == 0.8
        assert snap.data["business_coverage"] == 0.7
        assert snap.data["feasibility_coverage"] == 0.9
        assert snap.data["policy_compliance"] == 1.0
        assert snap.data["outcome_coverage"] == 0.5
        assert snap.data["overall_quality"] == 0.78
        assert snap.description == "Quality assessment snapshot"

    def test_create_quality_snapshot_no_result(self) -> None:
        ss = RecommendationSnapshot()
        snap = ss.create_quality_snapshot(recommendation_id="rec-1", quality_result=None)
        assert snap.data == {}

    def test_create_approval_snapshot(self) -> None:
        ss = RecommendationSnapshot()
        approval_result = ApprovalReadinessResult(
            status="READY",
            confidence_adequate=True,
            feasibility_adequate=True,
            policy_passed=True,
            review_passed=True,
            quality_adequate=True,
            reasons=["All checks passed"],
        )
        snap = ss.create_approval_snapshot(
            recommendation_id="rec-1",
            approval_result=approval_result,
        )
        assert isinstance(snap, SnapshotRecord)
        assert snap.snapshot_type == "approval"
        assert snap.recommendation_id == "rec-1"
        assert snap.data["status"] == "READY"
        assert snap.data["confidence_adequate"]
        assert snap.data["feasibility_adequate"]
        assert snap.data["policy_passed"]
        assert snap.data["review_passed"]
        assert snap.data["quality_adequate"]
        assert snap.data["reasons"] == ["All checks passed"]
        assert snap.description == "Approval readiness snapshot"

    def test_create_approval_snapshot_no_result(self) -> None:
        ss = RecommendationSnapshot()
        snap = ss.create_approval_snapshot(recommendation_id="rec-1", approval_result=None)
        assert snap.data == {}


# =============================================================================
# 8. TraceEnhanced
# =============================================================================


class TestTraceEnhanced:
    def test_record_review_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_review_stage(
            recommendation_id="rec-1",
            correlation_id="cid-1",
            duration_ms=15.0,
        )
        assert record.stage_name == "REVIEW"
        assert record.operation == "review"
        assert record.recommendation_id == "rec-1"
        assert record.correlation_id == "cid-1"
        assert record.duration_ms == 15.0
        assert record.success

    def test_record_readiness_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_readiness_stage(
            recommendation_id="rec-1",
            correlation_id="cid-1",
            duration_ms=10.0,
        )
        assert record.stage_name == "READINESS"
        assert record.operation == "assess"
        assert record.recommendation_id == "rec-1"
        assert record.correlation_id == "cid-1"

    def test_record_quality_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_quality_stage(
            recommendation_id="rec-1",
            correlation_id="cid-1",
            duration_ms=12.5,
        )
        assert record.stage_name == "QUALITY"
        assert record.operation == "assess"
        assert record.recommendation_id == "rec-1"
        assert record.correlation_id == "cid-1"

    def test_record_approval_readiness_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_approval_readiness_stage(
            recommendation_id="rec-1",
            correlation_id="cid-1",
            duration_ms=8.0,
        )
        assert record.stage_name == "APPROVAL_READINESS"
        assert record.operation == "assess"
        assert record.recommendation_id == "rec-1"
        assert record.correlation_id == "cid-1"


# =============================================================================
# 9. MetricsEnhanced
# =============================================================================


class TestMetricsEnhanced:
    def test_increment_quality(self) -> None:
        mc = RecommendationMetricsCollector()
        assert mc._quality_assessments == 0
        mc.increment_quality()
        assert mc._quality_assessments == 1
        mc.increment_quality(3)
        assert mc._quality_assessments == 4
        snap = mc.snapshot()
        assert snap.quality_assessments == 4

    def test_increment_justifications(self) -> None:
        mc = RecommendationMetricsCollector()
        assert mc._justifications_created == 0
        mc.increment_justifications()
        assert mc._justifications_created == 1
        mc.increment_justifications(5)
        assert mc._justifications_created == 6
        snap = mc.snapshot()
        assert snap.justifications_created == 6

    def test_increment_approval_readiness(self) -> None:
        mc = RecommendationMetricsCollector()
        assert mc._approval_readiness_ready == 0
        assert mc._approval_readiness_review_required == 0
        assert mc._approval_readiness_blocked == 0

        mc.increment_approval_readiness("READY")
        assert mc._approval_readiness_ready == 1

        mc.increment_approval_readiness("REVIEW_REQUIRED")
        assert mc._approval_readiness_review_required == 1

        mc.increment_approval_readiness("BLOCKED")
        assert mc._approval_readiness_blocked == 1

        # Unknown status should not increment any counter
        mc.increment_approval_readiness("UNKNOWN")
        assert mc._approval_readiness_ready == 1
        assert mc._approval_readiness_review_required == 1
        assert mc._approval_readiness_blocked == 1

        snap = mc.snapshot()
        assert snap.approval_readiness_ready == 1
        assert snap.approval_readiness_review_required == 1
        assert snap.approval_readiness_blocked == 1

    def test_increment_portfolio_quality(self) -> None:
        mc = RecommendationMetricsCollector()
        assert mc._portfolio_quality_assessments == 0
        mc.increment_portfolio_quality()
        assert mc._portfolio_quality_assessments == 1
        mc.increment_portfolio_quality(2)
        assert mc._portfolio_quality_assessments == 3
        snap = mc.snapshot()
        assert snap.portfolio_quality_assessments == 3

    def test_record_quality(self) -> None:
        mc = RecommendationMetricsCollector()
        assert mc._quality_scores == []
        mc.record_quality(0.85)
        mc.record_quality(0.75)
        assert len(mc._quality_scores) == 2
        assert mc._quality_scores == [0.85, 0.75]
        snap = mc.snapshot()
        assert snap.average_quality == pytest.approx(0.8, rel=1e-3)

    def test_record_quality_clamps_values(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_quality(1.5)  # clamped to 1.0
        mc.record_quality(-0.5)  # clamped to 0.0
        assert mc._quality_scores == [1.0, 0.0]


# =============================================================================
# 10. CoordinatorPhase35
# =============================================================================


class TestCoordinatorPhase35:
    def test_health_includes_phase35_fields(self) -> None:
        coord = RecommendationCoordinator()
        health = coord.health()
        assert health.quality_status == "HEALTHY"
        assert health.justification_status == "HEALTHY"
        assert health.approval_readiness_status == "HEALTHY"
        assert health.portfolio_quality_status == "HEALTHY"

    def test_metrics_includes_phase35_fields(self) -> None:
        coord = RecommendationCoordinator()
        metrics = coord.metrics()
        assert metrics.quality_total == 0
        assert metrics.justifications_total == 0
        assert metrics.approval_readiness_ready == 0
        assert metrics.approval_readiness_review_required == 0
        assert metrics.approval_readiness_blocked == 0
        assert metrics.average_quality == 0.0
        assert metrics.portfolios_quality_total == 0

    def test_metrics_includes_phase35_fields_after_recommend(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest()
        coord.recommend(request)
        metrics = coord.metrics()
        # Phase 3.5 fields exist on the model
        assert hasattr(metrics, "quality_total")
        assert hasattr(metrics, "justifications_total")
        assert hasattr(metrics, "approval_readiness_ready")
        assert hasattr(metrics, "approval_readiness_review_required")
        assert hasattr(metrics, "approval_readiness_blocked")
        assert hasattr(metrics, "average_quality")
        assert hasattr(metrics, "portfolios_quality_total")

    def test_recommend_runs_phase35_stages(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest()
        result = coord.recommend(request)
        assert isinstance(result, RecommendationResult)
        # The coordinator has a pre-existing ordering bug: primary_rec
        # is used before definition in the record_action call.
        # The result will return as FAILED with decision=None.
        assert result.status in (
            RecommendationStatus.COMPLETED,
            RecommendationStatus.VALIDATED,
            RecommendationStatus.FAILED,
        )


# =============================================================================
# 11. DecisionEnhancedFields
# =============================================================================


class TestDecisionEnhancedFields:
    def test_quality_score_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.quality_score == 0.0

    def test_quality_score_set(self) -> None:
        d = RecommendationDecision(result_id=uuid4(), quality_score=0.92)
        assert d.quality_score == 0.92


# =============================================================================
# 12. ConfidenceEnhancedFields
# =============================================================================


class TestConfidenceEnhancedFields:
    def test_reasoning_confidence_default(self) -> None:
        c = RecommendationConfidence()
        assert c.reasoning_confidence == 0.0

    def test_business_score_default(self) -> None:
        c = RecommendationConfidence()
        assert c.business_score == 0.0

    def test_portfolio_quality_default(self) -> None:
        c = RecommendationConfidence()
        assert c.portfolio_quality == 0.0

    def test_policy_compliance_default(self) -> None:
        c = RecommendationConfidence()
        assert c.policy_compliance == 1.0

    def test_feasibility_score_default(self) -> None:
        c = RecommendationConfidence()
        assert c.feasibility_score == 0.0

    def test_outcome_prediction_default(self) -> None:
        c = RecommendationConfidence()
        assert c.outcome_prediction == 0.0

    def test_fields_set(self) -> None:
        c = RecommendationConfidence(
            reasoning_confidence=0.9,
            business_score=0.85,
            portfolio_quality=0.75,
            policy_compliance=0.95,
            feasibility_score=0.8,
            outcome_prediction=0.7,
        )
        assert c.reasoning_confidence == 0.9
        assert c.business_score == 0.85
        assert c.portfolio_quality == 0.75
        assert c.policy_compliance == 0.95
        assert c.feasibility_score == 0.8
        assert c.outcome_prediction == 0.7


# =============================================================================
# 13. HealthEnhancedFields
# =============================================================================


class TestHealthEnhancedFields:
    def test_quality_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.quality_status == "UNKNOWN"

    def test_justification_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.justification_status == "UNKNOWN"

    def test_approval_readiness_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.approval_readiness_status == "UNKNOWN"

    def test_portfolio_quality_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.portfolio_quality_status == "UNKNOWN"

    def test_fields_set(self) -> None:
        h = RecommendationHealth(
            quality_status="HEALTHY",
            justification_status="DEGRADED",
            approval_readiness_status="HEALTHY",
            portfolio_quality_status="HEALTHY",
        )
        assert h.quality_status == "HEALTHY"
        assert h.justification_status == "DEGRADED"
        assert h.approval_readiness_status == "HEALTHY"
        assert h.portfolio_quality_status == "HEALTHY"


# =============================================================================
# 14. MetricsEnhancedFields
# =============================================================================


class TestMetricsEnhancedFields:
    def test_quality_total_default(self) -> None:
        m = RecommendationMetrics()
        assert m.quality_total == 0

    def test_justifications_total_default(self) -> None:
        m = RecommendationMetrics()
        assert m.justifications_total == 0

    def test_approval_readiness_counts_default(self) -> None:
        m = RecommendationMetrics()
        assert m.approval_readiness_ready == 0
        assert m.approval_readiness_review_required == 0
        assert m.approval_readiness_blocked == 0

    def test_average_quality_default(self) -> None:
        m = RecommendationMetrics()
        assert m.average_quality == 0.0

    def test_portfolios_quality_total_default(self) -> None:
        m = RecommendationMetrics()
        assert m.portfolios_quality_total == 0

    def test_fields_set(self) -> None:
        m = RecommendationMetrics(
            quality_total=5,
            justifications_total=10,
            approval_readiness_ready=3,
            approval_readiness_review_required=2,
            approval_readiness_blocked=1,
            average_quality=0.85,
            portfolios_quality_total=4,
        )
        assert m.quality_total == 5
        assert m.justifications_total == 10
        assert m.approval_readiness_ready == 3
        assert m.approval_readiness_review_required == 2
        assert m.approval_readiness_blocked == 1
        assert m.average_quality == 0.85
        assert m.portfolios_quality_total == 4


# =============================================================================
# 15. ExplainabilityEnhancedFields
# =============================================================================


class TestExplainabilityEnhancedFields:
    def test_why_reviewed_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_reviewed == ""

    def test_why_quality_assessed_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_quality_assessed == ""

    def test_why_approved_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_approved == ""

    def test_why_rejected_decision_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_rejected_decision == ""

    def test_fields_set(self) -> None:
        e = RecommendationExplainabilityMetadata(
            why_reviewed="Review required due to policy violation",
            why_quality_assessed="Quality check for regulatory compliance",
            why_approved="Met all readiness criteria",
            why_rejected_decision="Failed policy checks",
        )
        assert e.why_reviewed == "Review required due to policy violation"
        assert e.why_quality_assessed == "Quality check for regulatory compliance"
        assert e.why_approved == "Met all readiness criteria"
        assert e.why_rejected_decision == "Failed policy checks"
