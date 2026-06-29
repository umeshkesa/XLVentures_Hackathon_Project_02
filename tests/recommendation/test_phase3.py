"""Comprehensive tests for the Recommendation Engine Phase 3 (Enterprise Orchestration).

Tests all Phase 3 orchestration components:
  1. RecommendationSessionManager
  2. RecommendationConfidenceCalculator
  3. RecommendationReview
  4. RecommendationVersionManager
  5. RecommendationReadiness
  6. RecommendationLineage
  7. RecommendationSnapshot
  8. PortfolioComparator
  9. RecommendationCoordinator
 10. RecommendationManager
 11. DefaultRecommendationService
 12. IntegrationHooks
 13. Enhanced Contract Models
"""

from __future__ import annotations

from uuid import uuid4

from adip.recommendation.contracts.models import (
    RecommendationConfidence,
    RecommendationDecision,
    RecommendationExplainabilityMetadata,
    RecommendationHealth,
    RecommendationMetrics,
    RecommendationRequest,
    RecommendationResult,
    RecommendationSession,
)
from adip.recommendation.dtos import RecommendationRequestDTO
from adip.recommendation.enums import (
    FeasibilityStatus,
    RecommendationDomain,
    RecommendationReadinessStatus,
    RecommendationStatus,
)
from adip.recommendation.enums import (
    RecommendationGoal as RecGoal,
)
from adip.recommendation.execution.generator import RecommendationGenerator
from adip.recommendation.execution.models import (
    FeasibilityAnalysis,
    PolicyEvalResult,
    RecommendationPortfolio,
)
from adip.recommendation.execution.ranker import RecommendationRanker
from adip.recommendation.orchestration.confidence import RecommendationConfidenceCalculator
from adip.recommendation.orchestration.coordinator import RecommendationCoordinator
from adip.recommendation.orchestration.lineage import RecommendationLineage
from adip.recommendation.orchestration.manager import RecommendationManager
from adip.recommendation.orchestration.portfolio_comparator import PortfolioComparator
from adip.recommendation.orchestration.readiness import RecommendationReadiness
from adip.recommendation.orchestration.review import RecommendationReview, ReviewResult
from adip.recommendation.orchestration.session import RecommendationSessionManager
from adip.recommendation.orchestration.snapshot import RecommendationSnapshot
from adip.recommendation.orchestration.version_manager import RecommendationVersionManager
from adip.recommendation.services.hooks import IntegrationHooks
from adip.recommendation.services.hooks import hooks as global_hooks
from adip.recommendation.services.service import DefaultRecommendationService

# =============================================================================
# 1. RecommendationSessionManager
# =============================================================================


class TestRecommendationSessionManager:
    def test_create_session(self) -> None:
        sm = RecommendationSessionManager()
        session = sm.create_session(
            request_id=str(uuid4()),
            domain=RecommendationDomain.ENERGY,
            goal="Reduce energy",
            strategy="COST_OPTIMIZATION",
        )
        assert isinstance(session, RecommendationSession)
        assert session.domain == RecommendationDomain.ENERGY
        assert session.goal == "Reduce energy"
        assert session.strategy == "COST_OPTIMIZATION"
        assert session.status == RecommendationStatus.INITIALIZED

    def test_get_session(self) -> None:
        sm = RecommendationSessionManager()
        session = sm.create_session(request_id=str(uuid4()))
        assert sm.get_session(str(session.session_id)) is session

    def test_get_session_not_found(self) -> None:
        sm = RecommendationSessionManager()
        assert sm.get_session("nonexistent") is None

    def test_update_status(self) -> None:
        sm = RecommendationSessionManager()
        session = sm.create_session(request_id=str(uuid4()))
        updated = sm.update_status(str(session.session_id), RecommendationStatus.GENERATED)
        assert updated is not None
        assert updated.status == RecommendationStatus.GENERATED

    def test_update_status_not_found(self) -> None:
        sm = RecommendationSessionManager()
        assert sm.update_status("nonexistent", RecommendationStatus.FAILED) is None

    def test_complete_session(self) -> None:
        sm = RecommendationSessionManager()
        session = sm.create_session(request_id=str(uuid4()))
        stats = {"candidates": 5, "confidence": 0.85}
        completed = sm.complete_session(str(session.session_id), statistics=stats)
        assert completed is not None
        assert completed.status == RecommendationStatus.COMPLETED
        assert completed.completed_at is not None
        assert completed.statistics == stats

    def test_complete_session_not_found(self) -> None:
        sm = RecommendationSessionManager()
        assert sm.complete_session("nonexistent") is None

    def test_fail_session(self) -> None:
        sm = RecommendationSessionManager()
        session = sm.create_session(request_id=str(uuid4()))
        failed = sm.fail_session(str(session.session_id), error="Something went wrong")
        assert failed is not None
        assert failed.status == RecommendationStatus.FAILED
        assert failed.completed_at is not None
        assert failed.metadata.get("error") == "Something went wrong"

    def test_fail_session_not_found(self) -> None:
        sm = RecommendationSessionManager()
        assert sm.fail_session("nonexistent") is None

    def test_get_all_sessions(self) -> None:
        sm = RecommendationSessionManager()
        assert len(sm.get_all_sessions()) == 0
        sm.create_session(request_id=str(uuid4()))
        sm.create_session(request_id=str(uuid4()))
        assert len(sm.get_all_sessions()) == 2

    def test_clear(self) -> None:
        sm = RecommendationSessionManager()
        sm.create_session(request_id=str(uuid4()))
        sm.clear()
        assert sm.count() == 0

    def test_count(self) -> None:
        sm = RecommendationSessionManager()
        assert sm.count() == 0
        sm.create_session(request_id=str(uuid4()))
        assert sm.count() == 1
        sm.create_session(request_id=str(uuid4()))
        assert sm.count() == 2


# =============================================================================
# 2. RecommendationConfidenceCalculator
# =============================================================================


class TestRecommendationConfidenceCalculator:
    def test_calculate_default(self) -> None:
        cc = RecommendationConfidenceCalculator()
        c = cc.calculate()
        assert isinstance(c, RecommendationConfidence)
        # With all defaults: rc=0, bs=0, f=0, pc=1, op=0, pq=0
        # strategy_confidence=(0+0)/2=0, impact_accuracy=(0+0)/2=0
        # benefit_reliability=(0+0)/2=0, risk_assessment=(1+0)/2=0.5
        # constraint_compliance=1.0
        # overall = 0*0.2 + 0*0.2 + 0*0.15 + 0.5*0.15 + 1.0*0.15 + 0*0.15 = 0.225
        assert c.overall_confidence == 0.225
        assert c.strategy_confidence == 0.0
        assert c.impact_accuracy == 0.0
        assert c.benefit_reliability == 0.0
        assert c.risk_assessment == 0.5
        assert c.constraint_compliance == 1.0

    def test_calculate_full(self) -> None:
        cc = RecommendationConfidenceCalculator()
        c = cc.calculate(
            reasoning_confidence=1.0,
            business_score=1.0,
            feasibility=1.0,
            policy_compliance=1.0,
            outcome_prediction=1.0,
            portfolio_quality=1.0,
        )
        assert c.overall_confidence == 1.0
        assert c.strategy_confidence == 1.0
        assert c.impact_accuracy == 1.0
        assert c.benefit_reliability == 1.0
        assert c.risk_assessment == 1.0
        assert c.constraint_compliance == 1.0

    def test_calculate_mixed(self) -> None:
        cc = RecommendationConfidenceCalculator()
        c = cc.calculate(
            reasoning_confidence=0.8,
            business_score=0.6,
            feasibility=0.7,
            policy_compliance=0.9,
            outcome_prediction=0.5,
            portfolio_quality=0.4,
        )
        # strategy_confidence = (0.8 + 0.6) / 2 = 0.7
        assert c.strategy_confidence == 0.7
        # impact_accuracy = (0.6 + 0.7) / 2 = 0.65
        assert c.impact_accuracy == 0.65
        # benefit_reliability = (0.8 + 0.5) / 2 = 0.65
        assert c.benefit_reliability == 0.65
        # risk_assessment = (0.9 + 0.7) / 2 = 0.8
        assert c.risk_assessment == 0.8
        # constraint_compliance = 0.9
        assert c.constraint_compliance == 0.9
        # overall = 0.7*0.2 + 0.65*0.2 + 0.65*0.15 + 0.8*0.15 + 0.9*0.15 + 0.4*0.15
        expected = round(0.7 * 0.20 + 0.65 * 0.20 + 0.65 * 0.15 + 0.8 * 0.15 + 0.9 * 0.15 + 0.4 * 0.15, 4)
        assert c.overall_confidence == expected

    def test_calculate_clamps_values(self) -> None:
        cc = RecommendationConfidenceCalculator()
        c = cc.calculate(
            reasoning_confidence=1.5,
            business_score=-0.5,
            feasibility=2.0,
            policy_compliance=-1.0,
            outcome_prediction=1.2,
            portfolio_quality=-0.3,
        )
        # clamped: rc=1.0, bs=0.0, f=1.0, pc=0.0, op=1.0, pq=0.0
        assert c.strategy_confidence == 0.5  # (1.0 + 0.0) / 2
        assert c.impact_accuracy == 0.5  # (0.0 + 1.0) / 2
        assert c.benefit_reliability == 1.0  # (1.0 + 1.0) / 2
        assert c.risk_assessment == 0.5  # (0.0 + 1.0) / 2
        assert c.constraint_compliance == 0.0
        assert 0.0 <= c.overall_confidence <= 1.0


# =============================================================================
# 3. RecommendationReview
# =============================================================================


class TestRecommendationReview:
    def test_review_default(self) -> None:
        r = RecommendationReview()
        result = r.review()
        assert isinstance(result, ReviewResult)
        assert result.policy_compliant
        assert result.feasible
        assert result.dependencies_resolved
        assert not result.portfolio_complete
        assert not result.confidence_adequate
        assert "No portfolio created" in result.violations
        assert "Confidence below 0.3 threshold" in result.warnings
        assert not result.passed

    def test_review_not_feasible(self) -> None:
        r = RecommendationReview()
        feasibility = FeasibilityAnalysis(status=FeasibilityStatus.NOT_FEASIBLE)
        result = r.review(feasibility=feasibility)
        assert not result.feasible
        assert "Recommendation is not feasible" in result.violations

    def test_review_no_portfolio(self) -> None:
        r = RecommendationReview()
        result = r.review(portfolio=None)
        assert not result.portfolio_complete
        assert "No portfolio created" in result.violations

    def test_review_low_confidence(self) -> None:
        r = RecommendationReview()
        result = r.review(confidence=0.2)
        assert not result.confidence_adequate
        assert "Confidence below 0.3 threshold" in result.warnings

    def test_review_policy_violations(self) -> None:
        r = RecommendationReview()
        policy_result = PolicyEvalResult(
            overall_passed=False,
            violations=["Safety policy violation"],
            warnings=["Review required"],
        )
        result = r.review(policy_result=policy_result)
        assert not result.policy_compliant
        assert "Safety policy violation" in result.violations
        assert "Review required" in result.warnings
        assert not result.passed

    def test_review_with_portfolio(self) -> None:
        r = RecommendationReview()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1")
        result = r.review(portfolio=portfolio, confidence=0.8)
        assert result.portfolio_complete
        assert result.confidence_adequate
        assert result.passed


# =============================================================================
# 4. RecommendationVersionManager
# =============================================================================


class TestRecommendationVersionManager:
    def test_create_version(self) -> None:
        vm = RecommendationVersionManager()
        v = vm.create_version(
            recommendation_id="rec-1",
            data={"strategy": "COST_OPTIMIZATION"},
            description="Initial version",
        )
        assert v.recommendation_id == "rec-1"
        assert v.version_number == 1
        assert v.data == {"strategy": "COST_OPTIMIZATION"}
        assert v.is_active

    def test_get_version_history(self) -> None:
        vm = RecommendationVersionManager()
        vm.create_version("rec-1", {"a": 1})
        vm.create_version("rec-1", {"a": 2})
        history = vm.get_version_history("rec-1")
        assert len(history) == 2
        assert history[0].version_number == 1
        assert history[1].version_number == 2

    def test_get_version_history_empty(self) -> None:
        vm = RecommendationVersionManager()
        assert vm.get_version_history("nonexistent") == []

    def test_get_active_version(self) -> None:
        vm = RecommendationVersionManager()
        v1 = vm.create_version("rec-1", {"a": 1}, make_active=True)
        active = vm.get_active_version("rec-1")
        assert active is not None
        assert active.version_id == v1.version_id

    def test_get_active_version_no_active(self) -> None:
        vm = RecommendationVersionManager()
        vm.create_version("rec-1", {"a": 1}, make_active=False)
        active = vm.get_active_version("rec-1")
        assert active is not None
        assert active.version_number == 1

    def test_get_active_version_nonexistent(self) -> None:
        vm = RecommendationVersionManager()
        assert vm.get_active_version("nonexistent") is None

    def test_set_active_version(self) -> None:
        vm = RecommendationVersionManager()
        v1 = vm.create_version("rec-1", {"a": 1}, make_active=False)
        v2 = vm.create_version("rec-1", {"a": 2}, make_active=False)
        activated = vm.set_active_version("rec-1", 1)
        assert activated is not None
        assert activated.version_number == 1
        active = vm.get_active_version("rec-1")
        assert active is not None
        assert active.version_number == 1

    def test_set_active_version_not_found(self) -> None:
        vm = RecommendationVersionManager()
        assert vm.set_active_version("rec-1", 99) is None

    def test_compare_versions(self) -> None:
        vm = RecommendationVersionManager()
        vm.create_version("rec-1", {"a": 1, "b": 2})
        vm.create_version("rec-1", {"a": 10, "b": 20})
        comp = vm.compare_versions("rec-1", 1, 2)
        assert comp["version_a_exists"]
        assert comp["version_b_exists"]
        assert comp["data_changed"]
        assert comp["version_a_data"] == {"a": 1, "b": 2}
        assert comp["version_b_data"] == {"a": 10, "b": 20}

    def test_compare_versions_same(self) -> None:
        vm = RecommendationVersionManager()
        vm.create_version("rec-1", {"a": 1})
        comp = vm.compare_versions("rec-1", 1, 2)
        assert comp["version_a_exists"]
        assert not comp["version_b_exists"]
        assert not comp["data_changed"]

    def test_compare_versions_nonexistent(self) -> None:
        vm = RecommendationVersionManager()
        comp = vm.compare_versions("nonexistent", 1, 2)
        assert not comp["version_a_exists"]
        assert not comp["version_b_exists"]

    def test_clear(self) -> None:
        vm = RecommendationVersionManager()
        vm.create_version("rec-1")
        vm.clear()
        assert vm.count() == 0

    def test_count(self) -> None:
        vm = RecommendationVersionManager()
        assert vm.count() == 0
        vm.create_version("rec-1")
        assert vm.count() == 1
        vm.create_version("rec-1")
        assert vm.count() == 2
        vm.create_version("rec-2")
        assert vm.count() == 3


# =============================================================================
# 5. RecommendationReadiness
# =============================================================================


class TestRecommendationReadiness:
    def test_assess_ready(self) -> None:
        rd = RecommendationReadiness()
        result = ReviewResult(
            passed=True,
            policy_compliant=True,
            feasible=True,
            portfolio_complete=True,
            confidence_adequate=True,
        )
        status = rd.assess(
            review_result=result,
            confidence=0.8,
            feasibility_score=0.9,
            policy_passed=True,
        )
        assert status == RecommendationReadinessStatus.READY

    def test_assess_blocked_by_violations(self) -> None:
        rd = RecommendationReadiness()
        result = ReviewResult(
            passed=False,
            violations=["Not feasible"],
        )
        status = rd.assess(review_result=result, confidence=0.8, feasibility_score=0.9, policy_passed=True)
        assert status == RecommendationReadinessStatus.BLOCKED

    def test_assest_blocked_by_policy(self) -> None:
        rd = RecommendationReadiness()
        status = rd.assess(
            review_result=None,
            confidence=0.8,
            feasibility_score=0.9,
            policy_passed=False,
        )
        assert status == RecommendationReadinessStatus.BLOCKED

    def test_assess_requires_review_low_confidence(self) -> None:
        rd = RecommendationReadiness()
        status = rd.assess(
            review_result=None,
            confidence=0.2,
            feasibility_score=0.9,
            policy_passed=True,
        )
        assert status == RecommendationReadinessStatus.REQUIRES_REVIEW

    def test_assess_blocked_low_feasibility(self) -> None:
        rd = RecommendationReadiness()
        status = rd.assess(
            review_result=None,
            confidence=0.8,
            feasibility_score=0.2,
            policy_passed=True,
        )
        assert status == RecommendationReadinessStatus.BLOCKED

    def test_assess_no_review_not_ready(self) -> None:
        rd = RecommendationReadiness()
        status = rd.assess(
            review_result=None,
            confidence=0.5,
            feasibility_score=0.5,
            policy_passed=True,
        )
        assert status == RecommendationReadinessStatus.REQUIRES_REVIEW

    def test_assess_portfolio(self) -> None:
        rd = RecommendationReadiness()
        portfolio = RecommendationPortfolio(primary_recommendation_id="rec-1", overall_confidence=0.85)
        status = rd.assess_portfolio(portfolio)
        assert status == RecommendationReadinessStatus.READY

    def test_assess_portfolio_none(self) -> None:
        rd = RecommendationReadiness()
        status = rd.assess_portfolio(None)
        assert status == RecommendationReadinessStatus.REQUIRES_REVIEW


# =============================================================================
# 6. RecommendationLineage
# =============================================================================


class TestRecommendationLineage:
    def test_record(self) -> None:
        ll = RecommendationLineage()
        entry = ll.record(
            lineage_type="recommendation",
            source_id="reasoning-1",
            target_id="rec-1",
            description="From reasoning to recommendation",
        )
        assert entry.lineage_type == "recommendation"
        assert entry.source_id == "reasoning-1"
        assert entry.target_id == "rec-1"
        assert entry.description == "From reasoning to recommendation"

    def test_get_by_target(self) -> None:
        ll = RecommendationLineage()
        ll.record("recommendation", source_id="src-1", target_id="rec-1")
        ll.record("portfolio", source_id="rec-1", target_id="port-1")
        entries = ll.get_by_target("rec-1")
        assert len(entries) == 1
        assert entries[0].lineage_type == "recommendation"

    def test_get_by_target_empty(self) -> None:
        ll = RecommendationLineage()
        assert ll.get_by_target("nonexistent") == []

    def test_get_by_source(self) -> None:
        ll = RecommendationLineage()
        ll.record("recommendation", source_id="reasoning-1", target_id="rec-1")
        ll.record("recommendation", source_id="reasoning-1", target_id="rec-2")
        ll.record("portfolio", source_id="reasoning-2", target_id="port-1")
        entries = ll.get_by_source("reasoning-1")
        assert len(entries) == 2

    def test_get_by_source_empty(self) -> None:
        ll = RecommendationLineage()
        assert ll.get_by_source("nonexistent") == []

    def test_get_by_type(self) -> None:
        ll = RecommendationLineage()
        ll.record("recommendation", source_id="src-1", target_id="rec-1")
        ll.record("portfolio", source_id="rec-1", target_id="port-1")
        ll.record("review", source_id="port-1", target_id="review-1")
        entries = ll.get_by_type("portfolio")
        assert len(entries) == 1
        assert entries[0].lineage_type == "portfolio"

    def test_get_by_type_empty(self) -> None:
        ll = RecommendationLineage()
        assert ll.get_by_type("nonexistent") == []

    def test_get_all(self) -> None:
        ll = RecommendationLineage()
        assert len(ll.get_all()) == 0
        ll.record("recommendation", source_id="src-1", target_id="rec-1")
        ll.record("portfolio", source_id="rec-1", target_id="port-1")
        assert len(ll.get_all()) == 2

    def test_clear(self) -> None:
        ll = RecommendationLineage()
        ll.record("recommendation", source_id="src-1", target_id="rec-1")
        ll.clear()
        assert ll.count() == 0

    def test_count(self) -> None:
        ll = RecommendationLineage()
        assert ll.count() == 0
        ll.record("recommendation", source_id="src-1", target_id="rec-1")
        assert ll.count() == 1
        ll.record("portfolio", source_id="rec-1", target_id="port-1")
        assert ll.count() == 2


# =============================================================================
# 7. RecommendationSnapshot
# =============================================================================


class TestRecommendationSnapshot:
    def test_create_snapshot(self) -> None:
        ss = RecommendationSnapshot()
        snap = ss.create_snapshot(
            recommendation_id="rec-1",
            snapshot_type="confidence",
            data={"overall": 0.85},
            description="Confidence snapshot",
        )
        assert snap.recommendation_id == "rec-1"
        assert snap.snapshot_type == "confidence"
        assert snap.data == {"overall": 0.85}
        assert snap.description == "Confidence snapshot"

    def test_create_portfolio_snapshot(self) -> None:
        ss = RecommendationSnapshot()
        portfolio = RecommendationPortfolio(
            portfolio_id="port-1",
            primary_recommendation_id="rec-1",
            alternative_ids=["rec-2", "rec-3"],
            overall_confidence=0.75,
        )
        snap = ss.create_portfolio_snapshot(recommendation_id="rec-1", portfolio=portfolio)
        assert snap.snapshot_type == "portfolio"
        assert snap.data["portfolio_id"] == "port-1"
        assert snap.data["primary_recommendation_id"] == "rec-1"
        assert snap.data["alternative_ids"] == ["rec-2", "rec-3"]
        assert snap.data["overall_confidence"] == 0.75

    def test_create_portfolio_snapshot_none(self) -> None:
        ss = RecommendationSnapshot()
        snap = ss.create_portfolio_snapshot(recommendation_id="rec-1", portfolio=None)
        assert snap.data == {}

    def test_get_by_recommendation(self) -> None:
        ss = RecommendationSnapshot()
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="confidence")
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="cost")
        ss.create_snapshot(recommendation_id="rec-2", snapshot_type="confidence")
        snaps = ss.get_by_recommendation("rec-1")
        assert len(snaps) == 2

    def test_get_by_recommendation_empty(self) -> None:
        ss = RecommendationSnapshot()
        assert ss.get_by_recommendation("nonexistent") == []

    def test_get_by_type(self) -> None:
        ss = RecommendationSnapshot()
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="confidence")
        ss.create_snapshot(recommendation_id="rec-2", snapshot_type="confidence")
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="cost")
        snaps = ss.get_by_type("confidence")
        assert len(snaps) == 2

    def test_get_by_type_empty(self) -> None:
        ss = RecommendationSnapshot()
        assert ss.get_by_type("nonexistent") == []

    def test_get_all(self) -> None:
        ss = RecommendationSnapshot()
        assert len(ss.get_all()) == 0
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="confidence")
        ss.create_snapshot(recommendation_id="rec-2", snapshot_type="cost")
        assert len(ss.get_all()) == 2

    def test_clear(self) -> None:
        ss = RecommendationSnapshot()
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="confidence")
        ss.clear()
        assert ss.count() == 0

    def test_count(self) -> None:
        ss = RecommendationSnapshot()
        assert ss.count() == 0
        ss.create_snapshot(recommendation_id="rec-1", snapshot_type="confidence")
        assert ss.count() == 1
        ss.create_snapshot(recommendation_id="rec-2", snapshot_type="cost")
        assert ss.count() == 2


# =============================================================================
# 8. PortfolioComparator
# =============================================================================


class TestPortfolioComparator:
    def test_compare_default(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare()
        assert result["cost"]["a"] == 0.0
        assert result["cost"]["b"] == 0.0
        assert result["overall_recommendation"] == "equal"

    def test_compare_a_better_cost(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare(
            portfolio_a={"cost": 1000, "risk": 0.3, "roi": 0.5, "business_value": 0.7, "feasibility": 0.8},
            portfolio_b={"cost": 5000, "risk": 0.3, "roi": 0.5, "business_value": 0.7, "feasibility": 0.8},
        )
        assert result["cost"]["better"] == "a"
        assert result["overall_recommendation"] == "portfolio_a"

    def test_compare_b_better_risk(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare(
            portfolio_a={"cost": 1000, "risk": 0.9, "roi": 0.5, "business_value": 0.7, "feasibility": 0.8},
            portfolio_b={"cost": 1000, "risk": 0.1, "roi": 0.5, "business_value": 0.7, "feasibility": 0.8},
        )
        assert result["risk"]["better"] == "b"
        assert result["overall_recommendation"] == "portfolio_b"

    def test_compare_equal(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare(
            portfolio_a={"cost": 1000, "risk": 0.3, "roi": 0.5, "business_value": 0.7, "feasibility": 0.8},
            portfolio_b={"cost": 1000, "risk": 0.3, "roi": 0.5, "business_value": 0.7, "feasibility": 0.8},
        )
        assert result["cost"]["better"] == "equal"
        assert result["risk"]["better"] == "equal"
        assert result["roi"]["better"] == "equal"
        assert result["business_value"]["better"] == "equal"
        assert result["feasibility"]["better"] == "equal"
        assert result["overall_recommendation"] == "equal"

    def test_compare_portfolios(self) -> None:
        pc = PortfolioComparator()
        pa = RecommendationPortfolio(primary_recommendation_id="rec-1", overall_confidence=0.9)
        pb = RecommendationPortfolio(primary_recommendation_id="rec-2", overall_confidence=0.5)
        result = pc.compare_portfolios(pa, pb)
        assert isinstance(result, dict)
        assert "cost" in result
        assert "risk" in result
        assert "roi" in result
        assert "business_value" in result
        assert "feasibility" in result
        assert "overall_recommendation" in result

    def test_compare_portfolios_first_none(self) -> None:
        pc = PortfolioComparator()
        pb = RecommendationPortfolio(primary_recommendation_id="rec-2", overall_confidence=0.7)
        result = pc.compare_portfolios(None, pb)
        assert result["overall_recommendation"] == "portfolio_b"

    def test_compare_portfolios_both_none(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare_portfolios(None, None)
        assert result["overall_recommendation"] == "equal"

    def test_compare_a_better_roi(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare(
            portfolio_a={"cost": 1000, "risk": 0.3, "roi": 0.9, "business_value": 0.7, "feasibility": 0.8},
            portfolio_b={"cost": 1000, "risk": 0.3, "roi": 0.1, "business_value": 0.7, "feasibility": 0.8},
        )
        assert result["roi"]["better"] == "a"
        assert result["overall_recommendation"] == "portfolio_a"

    def test_compare_b_better_business_value(self) -> None:
        pc = PortfolioComparator()
        result = pc.compare(
            portfolio_a={"cost": 1000, "risk": 0.3, "roi": 0.5, "business_value": 0.2, "feasibility": 0.8},
            portfolio_b={"cost": 1000, "risk": 0.3, "roi": 0.5, "business_value": 0.9, "feasibility": 0.8},
        )
        assert result["business_value"]["better"] == "b"
        assert result["overall_recommendation"] == "portfolio_b"


# =============================================================================
# 9. RecommendationCoordinator
# =============================================================================


class TestRecommendationCoordinator:
    def test_recommend_completes(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest()
        result = coord.recommend(request)
        assert result.status in (
            RecommendationStatus.COMPLETED,
            RecommendationStatus.VALIDATED,
            RecommendationStatus.FAILED,
        )

    def test_recommend_returns_result(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest()
        result = coord.recommend(request)
        assert isinstance(result, RecommendationResult)
        assert result.decision is not None
        assert result.confidence is not None
        assert result.readiness != ""
        assert result.status != RecommendationStatus.INITIALIZED

    def test_recommend_with_goals(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest(goals=[RecGoal.REDUCE_COST])
        result = coord.recommend(request)
        assert isinstance(result, RecommendationResult)
        assert result.decision is not None

    def test_recommend_with_context(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest(context={"asset_id": "asset-1"})
        result = coord.recommend(request)
        assert isinstance(result, RecommendationResult)

    def test_recommend_with_correlation_id(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest()
        result = coord.recommend(request, correlation_id="test-cid")
        assert isinstance(result, RecommendationResult)

    def test_health(self) -> None:
        coord = RecommendationCoordinator()
        health = coord.health()
        assert isinstance(health, RecommendationHealth)
        assert health.overall_status == "HEALTHY"
        assert health.coordinator_status == "HEALTHY"
        assert health.generator_status == "HEALTHY"
        assert health.session_manager_status == "HEALTHY"
        assert health.confidence_calculator_status == "HEALTHY"
        assert health.review_status == "HEALTHY"
        assert health.version_manager_status == "HEALTHY"
        assert health.readiness_status == "HEALTHY"
        assert health.lineage_status == "HEALTHY"
        assert health.snapshot_status == "HEALTHY"
        assert health.portfolio_comparator_status == "HEALTHY"
        assert health.hooks_status == "HEALTHY"

    def test_metrics(self) -> None:
        coord = RecommendationCoordinator()
        metrics = coord.metrics()
        assert isinstance(metrics, RecommendationMetrics)
        assert metrics.sessions_total == 0
        assert metrics.versions_created == 0
        assert metrics.snapshots_taken == 0

    def test_metrics_after_recommend(self) -> None:
        coord = RecommendationCoordinator()
        request = RecommendationRequest()
        coord.recommend(request)
        metrics = coord.metrics()
        assert metrics.sessions_total >= 1
        assert metrics.versions_created >= 1
        assert metrics.snapshots_taken >= 1

    def test_get_result(self) -> None:
        coord = RecommendationCoordinator()
        assert coord.get_result("nonexistent") is None

    def test_recommend_injects_injected_components(self) -> None:
        generator = RecommendationGenerator()
        ranker = RecommendationRanker()
        coord = RecommendationCoordinator(
            generator=generator,
            ranker=ranker,
        )
        request = RecommendationRequest()
        result = coord.recommend(request)
        assert isinstance(result, RecommendationResult)


# =============================================================================
# 10. RecommendationManager
# =============================================================================


class TestRecommendationManager:
    def test_execute_recommendation(self) -> None:
        mgr = RecommendationManager()
        request = RecommendationRequest()
        result = mgr.execute_recommendation(request)
        assert isinstance(result, RecommendationResult)
        assert result.status != RecommendationStatus.INITIALIZED

    def test_get_result(self) -> None:
        mgr = RecommendationManager()
        request = RecommendationRequest()
        result = mgr.execute_recommendation(request)
        retrieved = mgr.get_result(str(result.result_id))
        assert retrieved is not None
        assert str(retrieved.result_id) == str(result.result_id)

    def test_get_result_not_found(self) -> None:
        mgr = RecommendationManager()
        assert mgr.get_result("nonexistent") is None

    def test_get_health(self) -> None:
        mgr = RecommendationManager()
        health = mgr.get_health()
        assert isinstance(health, RecommendationHealth)
        assert health.overall_status == "HEALTHY"

    def test_get_metrics(self) -> None:
        mgr = RecommendationManager()
        metrics = mgr.get_metrics()
        assert isinstance(metrics, RecommendationMetrics)

    def test_get_metrics_after_execution(self) -> None:
        mgr = RecommendationManager()
        mgr.execute_recommendation(RecommendationRequest())
        metrics = mgr.get_metrics()
        assert metrics.sessions_total >= 1

    def test_multiple_executions(self) -> None:
        mgr = RecommendationManager()
        r1 = mgr.execute_recommendation(RecommendationRequest())
        r2 = mgr.execute_recommendation(RecommendationRequest())
        assert str(r1.result_id) != str(r2.result_id)
        assert mgr.get_result(str(r1.result_id)) is not None
        assert mgr.get_result(str(r2.result_id)) is not None

    def test_execute_with_correlation_id(self) -> None:
        mgr = RecommendationManager()
        result = mgr.execute_recommendation(RecommendationRequest(), correlation_id="my-cid")
        assert isinstance(result, RecommendationResult)


# =============================================================================
# 11. DefaultRecommendationService
# =============================================================================


class TestDefaultRecommendationService:
    def test_recommend_default(self) -> None:
        svc = DefaultRecommendationService()
        dto = RecommendationRequestDTO(reasoning_result_id=str(uuid4()))
        response = svc.recommend(dto)
        assert response is not None
        assert response.status is not None

    def test_recommend_with_auth_fail(self) -> None:
        def auth_fail(user_id: str, action: str) -> bool:
            return False

        svc = DefaultRecommendationService(auth_callback=auth_fail)
        dto = RecommendationRequestDTO(reasoning_result_id=str(uuid4()))
        response = svc.recommend(dto, user_id="user-1")
        assert response is None

    def test_recommend_with_auth_pass(self) -> None:
        def auth_pass(user_id: str, action: str) -> bool:
            return True

        svc = DefaultRecommendationService(auth_callback=auth_pass)
        dto = RecommendationRequestDTO(reasoning_result_id=str(uuid4()))
        response = svc.recommend(dto, user_id="user-1")
        assert response is not None

    def test_get_result(self) -> None:
        svc = DefaultRecommendationService()
        dto = RecommendationRequestDTO(reasoning_result_id=str(uuid4()))
        svc.recommend(dto)
        result_id = "test-result"
        result = svc.get_result(result_id)
        assert result is None or isinstance(result, RecommendationResult)

    def test_get_result_with_auth_fail(self) -> None:
        def auth_fail(user_id: str, action: str) -> bool:
            return False

        svc = DefaultRecommendationService(auth_callback=auth_fail)
        assert svc.get_result("test", user_id="user-1") is None

    def test_get_health(self) -> None:
        svc = DefaultRecommendationService()
        health = svc.get_health()
        assert isinstance(health, RecommendationHealth)

    def test_get_metrics(self) -> None:
        svc = DefaultRecommendationService()
        metrics = svc.get_metrics()
        assert isinstance(metrics, RecommendationMetrics)

    def test_recommend_with_audit_callback(self) -> None:
        audit_log: list[str] = []

        def audit(action: str, user: str, resource: str, details: dict) -> None:
            audit_log.append(f"{action}:{user}")

        svc = DefaultRecommendationService(audit_callback=audit)
        dto = RecommendationRequestDTO(reasoning_result_id=str(uuid4()))
        svc.recommend(dto, user_id="user-1")
        assert len(audit_log) >= 1
        assert "recommend:user-1" in audit_log

    def test_recommend_with_correlation_id(self) -> None:
        svc = DefaultRecommendationService()
        dto = RecommendationRequestDTO(reasoning_result_id=str(uuid4()))
        response = svc.recommend(dto, correlation_id="test-cid")
        assert response is not None

    def test_get_package_returns_none(self) -> None:
        svc = DefaultRecommendationService()
        assert svc.get_package("any-package-id") is None


# =============================================================================
# 12. IntegrationHooks
# =============================================================================


class TestIntegrationHooks:
    def test_register_and_run_pre_recommend(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook1(**kwargs: object) -> None:
            calls.append("hook1")

        h.register_pre_recommend(hook1)
        h.run_pre_recommend()
        assert calls == ["hook1"]

    def test_register_and_run_post_recommend(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook1(**kwargs: object) -> None:
            calls.append("hook1")

        h.register_post_recommend(hook1)
        h.run_post_recommend()
        assert calls == ["hook1"]

    def test_exception_isolation(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def failing_hook(**kwargs: object) -> None:
            raise ValueError("Hook failed")

        def working_hook(**kwargs: object) -> None:
            calls.append("working")

        h.register_pre_recommend(failing_hook)
        h.register_pre_recommend(working_hook)
        h.run_pre_recommend()
        assert calls == ["working"]

    def test_global_hooks_singleton(self) -> None:
        assert isinstance(global_hooks, IntegrationHooks)

    def test_register_and_run_pre_session_create(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("pre_session")

        h.register_pre_session_create(hook)
        h.run_pre_session_create()
        assert calls == ["pre_session"]

    def test_register_and_run_post_session_create(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("post_session")

        h.register_post_session_create(hook)
        h.run_post_session_create()
        assert calls == ["post_session"]

    def test_register_and_run_pre_portfolio(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("pre_portfolio")

        h.register_pre_portfolio(hook)
        h.run_pre_portfolio()
        assert calls == ["pre_portfolio"]

    def test_register_and_run_post_portfolio(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("post_portfolio")

        h.register_post_portfolio(hook)
        h.run_post_portfolio()
        assert calls == ["post_portfolio"]

    def test_register_and_run_pre_review(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("pre_review")

        h.register_pre_review(hook)
        h.run_pre_review()
        assert calls == ["pre_review"]

    def test_register_and_run_post_review(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("post_review")

        h.register_post_review(hook)
        h.run_post_review()
        assert calls == ["post_review"]

    def test_register_and_run_pre_confidence(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("pre_confidence")

        h.register_pre_confidence(hook)
        h.run_pre_confidence()
        assert calls == ["pre_confidence"]

    def test_register_and_run_post_confidence(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("post_confidence")

        h.register_post_confidence(hook)
        h.run_post_confidence()
        assert calls == ["post_confidence"]

    def test_register_and_run_on_error(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("on_error")

        h.register_on_error(hook)
        h.run_on_error()
        assert calls == ["on_error"]

    def test_register_and_run_on_complete(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("on_complete")

        h.register_on_complete(hook)
        h.run_on_complete()
        assert calls == ["on_complete"]

    def test_hooks_pass_kwargs(self) -> None:
        h = IntegrationHooks()
        received: dict[str, object] = {}

        def hook(**kwargs: object) -> None:
            received.update(kwargs)

        h.register_pre_recommend(hook)
        h.run_pre_recommend(request_id="req-1", user_id="user-1")
        assert received.get("request_id") == "req-1"
        assert received.get("user_id") == "user-1"

    def test_multiple_hooks_all_run(self) -> None:
        h = IntegrationHooks()
        calls: list[int] = []

        def h1(**kwargs: object) -> None:
            calls.append(1)

        def h2(**kwargs: object) -> None:
            calls.append(2)

        def h3(**kwargs: object) -> None:
            calls.append(3)

        h.register_pre_recommend(h1)
        h.register_pre_recommend(h2)
        h.register_pre_recommend(h3)
        h.run_pre_recommend()
        assert calls == [1, 2, 3]

    def test_all_exceptions_isolated(self) -> None:
        h = IntegrationHooks()
        calls: list[int] = []

        def fail1(**kwargs: object) -> None:
            raise RuntimeError("fail1")

        def ok1(**kwargs: object) -> None:
            calls.append(1)

        def fail2(**kwargs: object) -> None:
            raise ValueError("fail2")

        def ok2(**kwargs: object) -> None:
            calls.append(2)

        h.register_pre_recommend(fail1)
        h.register_pre_recommend(ok1)
        h.register_pre_recommend(fail2)
        h.register_pre_recommend(ok2)
        h.run_pre_recommend()
        assert calls == [1, 2]


# =============================================================================
# 13. Enhanced Contract Models
# =============================================================================


class TestDecisionNewFields:
    def test_business_score_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.business_score == 0.0

    def test_primary_recommendation_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.primary_recommendation == ""

    def test_alternative_recommendations_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.alternative_recommendations == []

    def test_portfolio_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.portfolio is None

    def test_feasibility_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.feasibility == "UNKNOWN"

    def test_readiness_default(self) -> None:
        d = RecommendationDecision(result_id=uuid4())
        assert d.readiness == "UNKNOWN"

    def test_business_score_set(self) -> None:
        d = RecommendationDecision(result_id=uuid4(), business_score=0.85)
        assert d.business_score == 0.85

    def test_primary_recommendation_set(self) -> None:
        d = RecommendationDecision(result_id=uuid4(), primary_recommendation="Replace filter")
        assert d.primary_recommendation == "Replace filter"

    def test_alternative_recommendations_set(self) -> None:
        d = RecommendationDecision(
            result_id=uuid4(),
            alternative_recommendations=["Clean valve", "Inspect piping"],
        )
        assert len(d.alternative_recommendations) == 2

    def test_feasibility_set(self) -> None:
        d = RecommendationDecision(result_id=uuid4(), feasibility="FEASIBLE")
        assert d.feasibility == "FEASIBLE"

    def test_readiness_set(self) -> None:
        d = RecommendationDecision(result_id=uuid4(), readiness="READY")
        assert d.readiness == "READY"


class TestSessionNewFields:
    def test_goal_default(self) -> None:
        s = RecommendationSession(request_id=uuid4())
        assert s.goal == ""

    def test_strategy_default(self) -> None:
        s = RecommendationSession(request_id=uuid4())
        assert s.strategy == ""

    def test_constraints_default(self) -> None:
        s = RecommendationSession(request_id=uuid4())
        assert s.constraints == []

    def test_portfolio_default(self) -> None:
        s = RecommendationSession(request_id=uuid4())
        assert s.portfolio is None

    def test_reasoning_session_default(self) -> None:
        s = RecommendationSession(request_id=uuid4())
        assert s.reasoning_session == ""

    def test_goal_set(self) -> None:
        s = RecommendationSession(request_id=uuid4(), goal="Reduce energy by 20%")
        assert s.goal == "Reduce energy by 20%"

    def test_strategy_set(self) -> None:
        s = RecommendationSession(request_id=uuid4(), strategy="COST_OPTIMIZATION")
        assert s.strategy == "COST_OPTIMIZATION"

    def test_constraints_set(self) -> None:
        s = RecommendationSession(request_id=uuid4(), constraints=["Budget < $5000", "Must complete today"])
        assert len(s.constraints) == 2

    def test_portfolio_set(self) -> None:
        s = RecommendationSession(request_id=uuid4(), portfolio={"primary": "rec-1"})
        assert s.portfolio == {"primary": "rec-1"}

    def test_statistics_default(self) -> None:
        s = RecommendationSession(request_id=uuid4())
        assert s.statistics == {}


class TestHealthNewFields:
    def test_session_manager_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.session_manager_status == "UNKNOWN"

    def test_confidence_calculator_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.confidence_calculator_status == "UNKNOWN"

    def test_review_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.review_status == "UNKNOWN"

    def test_version_manager_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.version_manager_status == "UNKNOWN"

    def test_readiness_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.readiness_status == "UNKNOWN"

    def test_lineage_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.lineage_status == "UNKNOWN"

    def test_snapshot_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.snapshot_status == "UNKNOWN"

    def test_portfolio_comparator_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.portfolio_comparator_status == "UNKNOWN"

    def test_hooks_status_default(self) -> None:
        h = RecommendationHealth()
        assert h.hooks_status == "UNKNOWN"

    def test_fields_set(self) -> None:
        h = RecommendationHealth(
            session_manager_status="HEALTHY",
            confidence_calculator_status="HEALTHY",
            review_status="HEALTHY",
            version_manager_status="HEALTHY",
            readiness_status="HEALTHY",
            lineage_status="HEALTHY",
            snapshot_status="HEALTHY",
            portfolio_comparator_status="HEALTHY",
            hooks_status="HEALTHY",
        )
        assert h.session_manager_status == "HEALTHY"
        assert h.confidence_calculator_status == "HEALTHY"
        assert h.review_status == "HEALTHY"
        assert h.version_manager_status == "HEALTHY"
        assert h.readiness_status == "HEALTHY"
        assert h.lineage_status == "HEALTHY"
        assert h.snapshot_status == "HEALTHY"
        assert h.portfolio_comparator_status == "HEALTHY"
        assert h.hooks_status == "HEALTHY"


class TestMetricsNewFields:
    def test_sessions_total_default(self) -> None:
        m = RecommendationMetrics()
        assert m.sessions_total == 0

    def test_reviews_total_default(self) -> None:
        m = RecommendationMetrics()
        assert m.reviews_total == 0

    def test_versions_created_default(self) -> None:
        m = RecommendationMetrics()
        assert m.versions_created == 0

    def test_snapshots_taken_default(self) -> None:
        m = RecommendationMetrics()
        assert m.snapshots_taken == 0

    def test_readiness_ready_default(self) -> None:
        m = RecommendationMetrics()
        assert m.readiness_ready == 0

    def test_readiness_blocked_default(self) -> None:
        m = RecommendationMetrics()
        assert m.readiness_blocked == 0

    def test_average_business_score_default(self) -> None:
        m = RecommendationMetrics()
        assert m.average_business_score == 0.0

    def test_average_feasibility_default(self) -> None:
        m = RecommendationMetrics()
        assert m.average_feasibility == 0.0

    def test_sessions_total_set(self) -> None:
        m = RecommendationMetrics(sessions_total=10)
        assert m.sessions_total == 10

    def test_versions_created_set(self) -> None:
        m = RecommendationMetrics(versions_created=5)
        assert m.versions_created == 5

    def test_snapshots_taken_set(self) -> None:
        m = RecommendationMetrics(snapshots_taken=3)
        assert m.snapshots_taken == 3


class TestExplainabilityNewFields:
    def test_why_generated_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_generated == ""

    def test_why_ranked_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_ranked == ""

    def test_why_portfolio_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_portfolio == ""

    def test_why_candidate_selected_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_candidate_selected == ""

    def test_why_candidate_rejected_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_candidate_rejected == ""

    def test_why_strategy_chosen_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_strategy_chosen == ""

    def test_why_priority_assigned_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_priority_assigned == ""

    def test_why_policy_applied_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_policy_applied == ""

    def test_why_confidence_calculated_default(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_confidence_calculated == ""

    def test_fields_set(self) -> None:
        e = RecommendationExplainabilityMetadata(
            why_generated="Based on energy data",
            why_ranked="Highest confidence first",
            why_portfolio="Combined best options",
            why_candidate_selected="Best cost-benefit ratio",
            why_candidate_rejected="Below confidence threshold",
            why_strategy_chosen="Aligned with goals",
            why_priority_assigned="Critical impact",
            why_policy_applied="Safety policy enforced",
            why_confidence_calculated="Multi-dimension aggregation",
        )
        assert e.why_generated == "Based on energy data"
        assert e.why_ranked == "Highest confidence first"
        assert e.why_portfolio == "Combined best options"
        assert e.why_candidate_selected == "Best cost-benefit ratio"
        assert e.why_candidate_rejected == "Below confidence threshold"
        assert e.why_strategy_chosen == "Aligned with goals"
        assert e.why_priority_assigned == "Critical impact"
        assert e.why_policy_applied == "Safety policy enforced"
        assert e.why_confidence_calculated == "Multi-dimension aggregation"
