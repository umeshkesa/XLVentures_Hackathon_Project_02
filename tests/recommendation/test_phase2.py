"""Comprehensive tests for the Recommendation Engine Phase 2 (Execution Pipeline).

Tests all 15 deterministic-placeholder execution components:
  1. StrategySelector
  2. RecommendationGenerator
  3. RecommendationRanker
  4. ScoreManager
  5. FeasibilityAnalyzer
  6. CostAnalyzer
  7. DependencyManager
  8. ImplementationPlanBuilder
  9. TimelineManager
 10. TradeoffAnalyzer
 11. PolicyEvaluator
 12. OutcomePredictor
 13. RecommendationPortfolio
 14. RecommendationTrace
 15. RecommendationMetricsCollector
"""

from __future__ import annotations

from adip.recommendation.contracts.models import (
    RecommendationBenefit,
    RecommendationCandidate,
    RecommendationConstraint,
    RecommendationRisk,
)
from adip.recommendation.enums import (
    BenefitType,
    ConstraintType,
    FeasibilityStatus,
    ImplementationTimeline,
    RecommendationDomain,
    RecommendationPriority,
    RecommendationStrategy,
)
from adip.recommendation.enums import (
    RecommendationGoal as RecGoal,
)
from adip.recommendation.execution.cost_analyzer import CostAnalyzer
from adip.recommendation.execution.dependency_manager import DependencyManager
from adip.recommendation.execution.feasibility_analyzer import FeasibilityAnalyzer
from adip.recommendation.execution.generator import RecommendationGenerator
from adip.recommendation.execution.implementation_plan_builder import ImplementationPlanBuilder
from adip.recommendation.execution.metrics import RecommendationMetricsCollector
from adip.recommendation.execution.models import (
    CostEstimate,
    DependencyGraph,
    FeasibilityAnalysis,
    ImplementationPlan,
    OutcomePrediction,
    PolicyEvalResult,
    RecommendationMetrics,
    RecommendationPortfolio,
    RecommendationScore,
    TimelineEstimate,
    TraceRecord,
    TradeoffAnalysis,
)
from adip.recommendation.execution.outcome_predictor import OutcomePredictor
from adip.recommendation.execution.policy_evaluator import PolicyEvaluator
from adip.recommendation.execution.portfolio import RecommendationPortfolio as PortfolioComponent
from adip.recommendation.execution.ranker import RecommendationRanker
from adip.recommendation.execution.score_manager import ScoreManager
from adip.recommendation.execution.strategy_selector import StrategySelector
from adip.recommendation.execution.timeline_manager import TimelineManager
from adip.recommendation.execution.trace import RecommendationTrace
from adip.recommendation.execution.tradeoff_analyzer import TradeoffAnalyzer

# =============================================================================
# 1. StrategySelector
# =============================================================================


class TestStrategySelector:
    def test_select_strategy_default(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy()
        assert isinstance(strategy, RecommendationStrategy)

    def test_select_strategy_reduce_downtime(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(goals=[RecGoal.REDUCE_DOWNTIME])
        assert strategy == RecommendationStrategy.PREVENTIVE_MAINTENANCE

    def test_select_strategy_reduce_cost(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(goals=[RecGoal.REDUCE_COST])
        assert strategy == RecommendationStrategy.COST_OPTIMIZATION

    def test_select_strategy_increase_safety(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(goals=[RecGoal.INCREASE_SAFETY])
        assert strategy == RecommendationStrategy.RISK_MITIGATION

    def test_select_strategy_reduce_energy(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(goals=[RecGoal.REDUCE_ENERGY_CONSUMPTION])
        assert strategy == RecommendationStrategy.ENERGY_OPTIMIZATION

    def test_select_strategy_meet_sla(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(goals=[RecGoal.MEET_SLA])
        assert strategy == RecommendationStrategy.SLA_RECOVERY

    def test_select_strategy_energy_domain(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(domain=RecommendationDomain.ENERGY)
        assert strategy == RecommendationStrategy.ENERGY_OPTIMIZATION

    def test_select_strategy_safety_domain(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(domain=RecommendationDomain.SAFETY)
        assert strategy == RecommendationStrategy.RISK_MITIGATION

    def test_select_strategy_maintenance_domain(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(domain=RecommendationDomain.MAINTENANCE)
        assert strategy == RecommendationStrategy.PREVENTIVE_MAINTENANCE

    def test_select_strategy_hybrid(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(has_policy=True, has_context=True)
        assert strategy == RecommendationStrategy.HYBRID_RECOMMENDATION

    def test_select_strategy_next_best_action(self) -> None:
        s = StrategySelector()
        strategy = s.select_strategy(has_policy=False, has_context=False)
        assert strategy == RecommendationStrategy.NEXT_BEST_ACTION

    def test_get_available_strategies(self) -> None:
        s = StrategySelector()
        strategies = s.get_available_strategies()
        assert len(strategies) == len(list(RecommendationStrategy))

    def test_rank_strategies_default(self) -> None:
        s = StrategySelector()
        ranked = s.rank_strategies()
        assert len(ranked) == len(list(RecommendationStrategy))
        for i in range(len(ranked) - 1):
            assert ranked[i][1] >= ranked[i + 1][1]

    def test_rank_strategies_reduce_downtime(self) -> None:
        s = StrategySelector()
        ranked = s.rank_strategies(goals=[RecGoal.REDUCE_DOWNTIME])
        assert ranked[0][0] == RecommendationStrategy.PREVENTIVE_MAINTENANCE
        assert ranked[0][1] == 0.9

    def test_rank_strategies_reduce_cost(self) -> None:
        s = StrategySelector()
        ranked = s.rank_strategies(goals=[RecGoal.REDUCE_COST])
        assert ranked[0][0] == RecommendationStrategy.COST_OPTIMIZATION

    def test_rank_strategies_increase_safety(self) -> None:
        s = StrategySelector()
        ranked = s.rank_strategies(goals=[RecGoal.INCREASE_SAFETY])
        assert ranked[0][0] == RecommendationStrategy.RISK_MITIGATION


# =============================================================================
# 2. RecommendationGenerator
# =============================================================================


class TestRecommendationGenerator:
    def test_generate_default(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1")
        assert len(candidates) == 5
        assert all(isinstance(c, RecommendationCandidate) for c in candidates)

    def test_generate_with_strategy(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate(
            "reasoning-1",
            strategy=RecommendationStrategy.COST_OPTIMIZATION,
            domain=RecommendationDomain.ENERGY,
        )
        assert len(candidates) == 5
        assert candidates[0].strategy == RecommendationStrategy.COST_OPTIMIZATION
        assert candidates[0].domain == RecommendationDomain.ENERGY

    def test_generate_custom_count(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1", count=3)
        assert len(candidates) == 3

    def test_generate_confidence_descending(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1", count=4)
        for i in range(len(candidates) - 1):
            assert candidates[i].confidence >= candidates[i + 1].confidence

    def test_generate_priorities(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1", count=5)
        assert candidates[0].priority == RecommendationPriority.CRITICAL
        assert candidates[1].priority == RecommendationPriority.HIGH
        assert candidates[2].priority == RecommendationPriority.HIGH
        assert candidates[3].priority == RecommendationPriority.MEDIUM
        assert candidates[4].priority == RecommendationPriority.MEDIUM

    def test_get_candidate(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1", count=2)
        found = g.get_candidate(str(candidates[0].candidate_id))
        assert found is not None
        assert str(found.candidate_id) == str(candidates[0].candidate_id)

    def test_get_candidate_not_found(self) -> None:
        g = RecommendationGenerator()
        assert g.get_candidate("nonexistent") is None

    def test_get_all_candidates(self) -> None:
        g = RecommendationGenerator()
        g.generate("reasoning-1", count=3)
        assert len(g.get_all_candidates()) == 3

    def test_clear(self) -> None:
        g = RecommendationGenerator()
        g.generate("reasoning-1", count=3)
        g.clear()
        assert g.count() == 0

    def test_count(self) -> None:
        g = RecommendationGenerator()
        assert g.count() == 0
        g.generate("reasoning-1", count=4)
        assert g.count() == 4

    def test_benefits_generated(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1", count=1)
        assert len(candidates[0].expected_benefits) >= 1
        first_benefit = candidates[0].expected_benefits[0]
        assert isinstance(first_benefit, RecommendationBenefit)
        assert first_benefit.benefit_type == BenefitType.EFFICIENCY_GAIN

    def test_risks_generated(self) -> None:
        g = RecommendationGenerator()
        candidates = g.generate("reasoning-1", count=1)
        assert len(candidates[0].expected_risks) >= 1
        first_risk = candidates[0].expected_risks[0]
        assert isinstance(first_risk, RecommendationRisk)


# =============================================================================
# 3. RecommendationRanker
# =============================================================================


class TestRecommendationRanker:
    def _make_candidates(self, count: int = 3) -> list[RecommendationCandidate]:
        g = RecommendationGenerator()
        return g.generate("reasoning-1", count=count)

    def test_rank_empty(self) -> None:
        r = RecommendationRanker()
        ranked = r.rank([])
        assert ranked == []

    def test_rank_sorts_by_score(self) -> None:
        r = RecommendationRanker()
        candidates = self._make_candidates(5)
        ranked = r.rank(candidates)
        assert len(ranked) == 5
        scores = [
            r.get_ranking_score(str(c.candidate_id)) for c in ranked
        ]
        for i in range(len(scores) - 1):
            if scores[i] is not None and scores[i + 1] is not None:
                assert scores[i] >= scores[i + 1]

    def test_rank_with_goals(self) -> None:
        r = RecommendationRanker()
        candidates = self._make_candidates(3)
        ranked = r.rank(candidates, goals=[RecGoal.REDUCE_DOWNTIME])
        assert len(ranked) == 3

    def test_rank_with_constraints(self) -> None:
        r = RecommendationRanker()
        candidates = self._make_candidates(3)
        constraints = [RecommendationConstraint(type=ConstraintType.HARD, description="Must comply")]
        ranked = r.rank(candidates, constraints=constraints)
        assert len(ranked) == 3

    def test_get_best(self) -> None:
        r = RecommendationRanker()
        candidates = self._make_candidates(3)
        ranked = r.rank(candidates)
        best = r.get_best(ranked)
        assert best is not None
        assert str(best.candidate_id) == str(ranked[0].candidate_id)

    def test_get_best_empty(self) -> None:
        r = RecommendationRanker()
        assert r.get_best([]) is None

    def test_clear(self) -> None:
        r = RecommendationRanker()
        r.rank(self._make_candidates(3))
        assert r.count() > 0
        r.clear()
        assert r.count() == 0

    def test_get_all_rankings(self) -> None:
        r = RecommendationRanker()
        candidates = self._make_candidates(2)
        r.rank(candidates)
        rankings = r.get_all_rankings()
        assert len(rankings) == 2

    def test_get_ranking_score_missing(self) -> None:
        r = RecommendationRanker()
        assert r.get_ranking_score("nonexistent") is None

    def test_rank_same_candidates_twice(self) -> None:
        r = RecommendationRanker()
        candidates = self._make_candidates(3)
        r.rank(candidates)
        count1 = r.count()
        r.rank(candidates)
        count2 = r.count()
        assert count2 == count1


# =============================================================================
# 4. ScoreManager
# =============================================================================


class TestScoreManager:
    def test_calculate_default(self) -> None:
        sm = ScoreManager()
        score = sm.calculate()
        assert isinstance(score, RecommendationScore)
        assert score.overall == 0.35  # risk_adjustment=1.0*0.20 + policy_compliance=1.0*0.15

    def test_calculate_full_scores(self) -> None:
        sm = ScoreManager()
        score = sm.calculate(
            business_value=1.0,
            feasibility=1.0,
            impact=1.0,
            risk_adjustment=1.0,
            policy_compliance=1.0,
        )
        assert score.overall == 1.0

    def test_calculate_weighted_formula(self) -> None:
        sm = ScoreManager()
        score = sm.calculate(
            business_value=0.8,
            feasibility=0.7,
            impact=0.6,
            risk_adjustment=0.9,
            policy_compliance=1.0,
        )
        expected = round(0.8 * 0.25 + 0.7 * 0.20 + 0.6 * 0.20 + 0.9 * 0.20 + 1.0 * 0.15, 4)
        assert score.overall == expected

    def test_clamps_values_above_range(self) -> None:
        sm = ScoreManager()
        score = sm.calculate(business_value=1.5)
        assert score.business_value == 1.0

    def test_clamps_values_below_range(self) -> None:
        sm = ScoreManager()
        score = sm.calculate(business_value=-0.5)
        assert score.business_value == 0.0

    def test_calculate_batch(self) -> None:
        sm = ScoreManager()
        scores_data = [
            {"business_value": 0.8, "feasibility": 0.7, "impact": 0.6, "risk_adjustment": 0.9, "policy_compliance": 1.0},
            {"business_value": 0.5, "feasibility": 0.5, "impact": 0.5},
            {"business_value": 0.2, "feasibility": 0.3, "impact": 0.4, "policy_compliance": 0.0},
        ]
        results = sm.calculate_batch(scores_data)
        assert len(results) == 3
        for r in results:
            assert isinstance(r, RecommendationScore)

    def test_calculate_batch_empty(self) -> None:
        sm = ScoreManager()
        results = sm.calculate_batch([])
        assert results == []


# =============================================================================
# 5. FeasibilityAnalyzer
# =============================================================================


class TestFeasibilityAnalyzer:
    def test_analyze_default(self) -> None:
        fa = FeasibilityAnalyzer()
        result = fa.analyze()
        assert isinstance(result, FeasibilityAnalysis)
        assert result.status == FeasibilityStatus.PARTIALLY_FEASIBLE

    def test_analyze_fully_feasible(self) -> None:
        fa = FeasibilityAnalyzer()
        result = fa.analyze(
            resource_score=0.9,
            budget_score=0.9,
            inventory_score=0.9,
            technician_score=0.9,
            time_window_score=0.9,
            operational_score=0.9,
        )
        assert result.status == FeasibilityStatus.FEASIBLE
        assert result.resources_available
        assert result.budget_available
        assert result.inventory_available
        assert result.technician_available
        assert result.time_window_available
        assert result.operational_feasible

    def test_analyze_not_feasible(self) -> None:
        fa = FeasibilityAnalyzer()
        result = fa.analyze(
            resource_score=0.0,
            budget_score=0.0,
            inventory_score=0.0,
            technician_score=0.0,
            time_window_score=0.0,
            operational_score=0.0,
        )
        assert result.status == FeasibilityStatus.NOT_FEASIBLE
        assert not result.resources_available

    def test_analyze_partially_feasible(self) -> None:
        fa = FeasibilityAnalyzer()
        result = fa.analyze(
            resource_score=0.5,
            budget_score=0.5,
            inventory_score=0.5,
            technician_score=0.5,
            time_window_score=0.5,
            operational_score=0.5,
        )
        assert result.status == FeasibilityStatus.PARTIALLY_FEASIBLE

    def test_feasibility_score_calculation(self) -> None:
        fa = FeasibilityAnalyzer()
        result = fa.analyze(
            resource_score=1.0,
            budget_score=1.0,
            inventory_score=1.0,
            technician_score=1.0,
            time_window_score=1.0,
            operational_score=1.0,
        )
        expected = round(1.0 * 0.2 + 1.0 * 0.2 + 1.0 * 0.15 + 1.0 * 0.15 + 1.0 * 0.15 + 1.0 * 0.15, 4)
        assert result.feasibility_score == expected

    def test_analyze_with_constraints(self) -> None:
        fa = FeasibilityAnalyzer()
        constraints = ["No available technician", "Budget not approved"]
        result = fa.analyze(constraints=constraints)
        assert result.constraints == constraints

    def test_analyze_candidate_budget_ok(self) -> None:
        fa = FeasibilityAnalyzer()
        candidate = RecommendationCandidate(action="test")
        result = fa.analyze_candidate(candidate)
        assert isinstance(result, FeasibilityAnalysis)

    def test_analyze_candidate_high_cost(self) -> None:
        fa = FeasibilityAnalyzer()
        candidate = RecommendationCandidate(action="test")
        result = fa.analyze_candidate(candidate, domain="high_cost")
        assert isinstance(result, FeasibilityAnalysis)


# =============================================================================
# 6. CostAnalyzer
# =============================================================================


class TestCostAnalyzer:
    def test_estimate_default(self) -> None:
        ca = CostAnalyzer()
        estimate = ca.estimate()
        assert isinstance(estimate, CostEstimate)
        assert estimate.total_cost == 1500.0  # 1000 + 500 + 0

    def test_estimate_with_downtime(self) -> None:
        ca = CostAnalyzer()
        estimate = ca.estimate(
            implementation_cost=5000.0,
            operational_cost=2000.0,
            downtime_cost=1000.0,
            expected_benefit=20000.0,
        )
        assert estimate.total_cost == 8000.0

    def test_estimate_roi_positive(self) -> None:
        ca = CostAnalyzer()
        estimate = ca.estimate(
            implementation_cost=1000.0,
            expected_benefit=5000.0,
        )
        assert estimate.roi > 0

    def test_estimate_roi_zero_total(self) -> None:
        ca = CostAnalyzer()
        estimate = ca.estimate(
            implementation_cost=0.0,
            operational_cost=0.0,
            downtime_cost=0.0,
            expected_benefit=0.0,
        )
        assert estimate.roi == 0.0

    def test_estimate_clamps_negative(self) -> None:
        ca = CostAnalyzer()
        estimate = ca.estimate(
            implementation_cost=-500.0,
            operational_cost=-200.0,
        )
        assert estimate.implementation_cost == 0.0
        assert estimate.operational_cost == 0.0

    def test_estimate_candidate(self) -> None:
        ca = CostAnalyzer()
        candidate = RecommendationCandidate(action="test")
        estimate = ca.estimate_candidate(candidate)
        assert isinstance(estimate, CostEstimate)
        assert estimate.implementation_cost > 0

    def test_estimate_candidate_with_multiplier(self) -> None:
        ca = CostAnalyzer()
        candidate = RecommendationCandidate(action="test")
        estimate = ca.estimate_candidate(candidate, multiplier=2.0)
        assert estimate.implementation_cost > 0

    def test_currency_default(self) -> None:
        ca = CostAnalyzer()
        estimate = ca.estimate()
        assert estimate.currency == "USD"


# =============================================================================
# 7. DependencyManager
# =============================================================================


class TestDependencyManager:
    def test_build_graph_empty(self) -> None:
        dm = DependencyManager()
        graph = dm.build_graph([])
        assert isinstance(graph, DependencyGraph)
        assert graph.nodes == []
        assert graph.execution_order == []

    def test_build_graph_simple(self) -> None:
        dm = DependencyManager()
        graph = dm.build_graph(["rec-1", "rec-2", "rec-3"])
        assert len(graph.nodes) == 3
        assert len(graph.execution_order) == 3

    def test_build_graph_with_blocking(self) -> None:
        dm = DependencyManager()
        graph = dm.build_graph(
            ["rec-1", "rec-2", "rec-3"],
            blocking_map={"rec-3": ["rec-1", "rec-2"]},
        )
        # rec-3 depends on rec-1 and rec-2, so it should be after them
        assert graph.execution_order.index("rec-3") > graph.execution_order.index("rec-1")
        assert graph.execution_order.index("rec-3") > graph.execution_order.index("rec-2")

    def test_build_graph_with_optional(self) -> None:
        dm = DependencyManager()
        graph = dm.build_graph(
            ["rec-1", "rec-2"],
            optional_map={"rec-2": ["rec-1"]},
        )
        assert len(graph.nodes) == 2

    def test_cycle_detection(self) -> None:
        dm = DependencyManager()
        graph = dm.build_graph(
            ["rec-1", "rec-2"],
            blocking_map={"rec-1": ["rec-2"], "rec-2": ["rec-1"]},
        )
        assert graph.has_cycles

    def test_node_fields(self) -> None:
        dm = DependencyManager()
        graph = dm.build_graph(
            ["rec-1", "rec-2"],
            blocking_map={"rec-1": ["rec-2"]},
        )
        node = graph.nodes[0]
        assert node.recommendation_id == "rec-1"
        assert "rec-2" in node.blocking_dependencies
        assert node.is_blocked

    def test_get_graph(self) -> None:
        dm = DependencyManager()
        g1 = dm.build_graph(["rec-1"])
        g2 = dm.get_graph(g1.graph_id)
        assert g2 is not None
        assert g2.graph_id == g1.graph_id

    def test_get_graph_not_found(self) -> None:
        dm = DependencyManager()
        assert dm.get_graph("nonexistent") is None

    def test_clear(self) -> None:
        dm = DependencyManager()
        dm.build_graph(["rec-1"])
        assert dm.count() == 1
        dm.clear()
        assert dm.count() == 0

    def test_count(self) -> None:
        dm = DependencyManager()
        assert dm.count() == 0
        dm.build_graph(["rec-1"])
        assert dm.count() == 1
        dm.build_graph(["rec-2"])
        assert dm.count() == 2


# =============================================================================
# 8. ImplementationPlanBuilder
# =============================================================================


class TestImplementationPlanBuilder:
    def test_build_default(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1")
        assert isinstance(plan, ImplementationPlan)
        assert plan.recommendation_id == "rec-1"
        assert len(plan.steps) == 3

    def test_build_custom_steps(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1", step_count=5)
        assert len(plan.steps) == 5

    def test_build_with_action(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1", action="Replace filter")
        assert "Replace filter" in plan.steps[0].description

    def test_build_with_resources(self) -> None:
        ipb = ImplementationPlanBuilder()
        resources = ["Specialist", "Toolkit"]
        plan = ipb.build(recommendation_id="rec-1", resources=resources)
        for res in resources:
            assert res in plan.required_resources

    def test_step_ordering(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1", step_count=4)
        for i, step in enumerate(plan.steps):
            assert step.order == i + 1

    def test_step_has_success_criteria(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1")
        for step in plan.steps:
            assert len(step.success_criteria) > 0

    def test_plan_success_criteria(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1")
        assert len(plan.success_criteria) == 3

    def test_plan_total_duration(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1", step_count=3)
        assert "h" in plan.total_duration

    def test_build_from_candidate(self) -> None:
        ipb = ImplementationPlanBuilder()
        candidate = RecommendationCandidate(action="Inspect valve")
        plan = ipb.build_from_candidate(candidate)
        assert isinstance(plan, ImplementationPlan)
        assert plan.recommendation_id == str(candidate.candidate_id)

    def test_build_zero_steps(self) -> None:
        ipb = ImplementationPlanBuilder()
        plan = ipb.build(recommendation_id="rec-1", step_count=0)
        assert len(plan.steps) == 0


# =============================================================================
# 9. TimelineManager
# =============================================================================


class TestTimelineManager:
    def test_estimate_default(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate()
        assert isinstance(estimate, TimelineEstimate)
        assert estimate.timeline == ImplementationTimeline.WITHIN_24_HOURS

    def test_estimate_immediate(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.95)
        assert estimate.timeline == ImplementationTimeline.IMMEDIATE
        assert estimate.estimated_hours == 1.0

    def test_estimate_today(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.8)
        assert estimate.timeline == ImplementationTimeline.TODAY
        assert estimate.estimated_hours == 8.0

    def test_estimate_within_24h(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.6)
        assert estimate.timeline == ImplementationTimeline.WITHIN_24_HOURS
        assert estimate.estimated_hours == 24.0

    def test_estimate_maintenance_window(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.4)
        assert estimate.timeline == ImplementationTimeline.MAINTENANCE_WINDOW
        assert estimate.estimated_hours == 72.0

    def test_estimate_planned_future(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.1)
        assert estimate.timeline == ImplementationTimeline.PLANNED_FUTURE
        assert estimate.estimated_hours == 168.0

    def test_complexity_high_doubles_hours(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.95, complexity="high")
        assert estimate.estimated_hours == 2.0

    def test_complexity_low_halves_hours(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.95, complexity="low")
        assert estimate.estimated_hours == 0.5

    def test_estimate_with_factors(self) -> None:
        tm = TimelineManager()
        factors = ["Urgent safety concern", "Available technician"]
        estimate = tm.estimate(urgency_score=0.9, factors=factors)
        assert estimate.factors == factors

    def test_estimate_priority_critical(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate_priority("CRITICAL")
        assert estimate.timeline == ImplementationTimeline.IMMEDIATE

    def test_estimate_priority_low(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate_priority("LOW")
        assert estimate.timeline == ImplementationTimeline.PLANNED_FUTURE

    def test_estimate_clamps_urgency(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=-0.5)
        assert estimate.urgency_score == 0.0

    def test_estimate_has_description(self) -> None:
        tm = TimelineManager()
        estimate = tm.estimate(urgency_score=0.8)
        assert len(estimate.description) > 0


# =============================================================================
# 10. TradeoffAnalyzer
# =============================================================================


class TestTradeoffAnalyzer:
    def test_analyze_default(self) -> None:
        ta = TradeoffAnalyzer()
        result = ta.analyze()
        assert isinstance(result, TradeoffAnalysis)

    def test_analyze_primary_cheaper(self) -> None:
        ta = TradeoffAnalyzer()
        result = ta.analyze(
            primary_id="primary-1",
            alternative_id="alt-1",
            primary_cost=1000.0,
            alternative_cost=5000.0,
        )
        assert result.cost_difference < 0
        assert result.overall_recommendation == "primary"

    def test_analyze_alternative_better(self) -> None:
        ta = TradeoffAnalyzer()
        result = ta.analyze(
            primary_id="primary-1",
            alternative_id="alt-1",
            primary_cost=5000.0,
            alternative_cost=1000.0,
            primary_risk=0.9,
            alternative_risk=0.1,
        )
        # Alternative is cheaper and less risky
        assert result.overall_recommendation == "alternative"

    def test_analyze_all_dims(self) -> None:
        ta = TradeoffAnalyzer()
        result = ta.analyze(
            primary_id="p1",
            alternative_id="a1",
            primary_cost=2000.0,
            alternative_cost=3000.0,
            primary_risk=0.3,
            alternative_risk=0.5,
            primary_downtime=4.0,
            alternative_downtime=8.0,
            primary_energy=100.0,
            alternative_energy=200.0,
            primary_safety=0.9,
            alternative_safety=0.7,
            primary_sla=0.95,
            alternative_sla=0.85,
        )
        assert result.overall_recommendation == "primary"

    def test_dimension_differences(self) -> None:
        ta = TradeoffAnalyzer()
        result = ta.analyze(
            primary_id="p1",
            alternative_id="a1",
            primary_cost=1000.0,
            alternative_cost=2000.0,
        )
        assert result.cost_difference == -1000.0

    def test_difference_clamping(self) -> None:
        ta = TradeoffAnalyzer()
        result = ta.analyze(
            primary_id="p1",
            alternative_id="a1",
            primary_risk=2.0,
            alternative_risk=-1.0,
        )
        assert -1.0 <= result.risk_difference <= 1.0

    def test_analyze_candidates(self) -> None:
        ta = TradeoffAnalyzer()
        primary = RecommendationCandidate(action="primary")
        alts = [RecommendationCandidate(action="alt1"), RecommendationCandidate(action="alt2")]
        results = ta.analyze_candidates(primary, alts)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, TradeoffAnalysis)

    def test_analyze_candidates_skip_self(self) -> None:
        ta = TradeoffAnalyzer()
        primary = RecommendationCandidate(action="same")
        alts = [primary]
        results = ta.analyze_candidates(primary, alts)
        assert len(results) == 0


# =============================================================================
# 11. PolicyEvaluator
# =============================================================================


class TestPolicyEvaluator:
    def test_evaluate_default(self) -> None:
        pe = PolicyEvaluator()
        result = pe.evaluate()
        assert isinstance(result, PolicyEvalResult)
        assert result.overall_passed

    def test_evaluate_all_pass(self) -> None:
        pe = PolicyEvaluator()
        result = pe.evaluate(
            safety_score=1.0,
            compliance_score=1.0,
            business_score=1.0,
            operational_score=1.0,
        )
        assert result.safety_passed
        assert result.compliance_passed
        assert result.business_passed
        assert result.operational_passed
        assert result.overall_passed

    def test_evaluate_safety_fails(self) -> None:
        pe = PolicyEvaluator()
        result = pe.evaluate(safety_score=0.0)
        assert not result.safety_passed
        assert not result.overall_passed
        assert "Safety policy not fully satisfied" in result.warnings

    def test_evaluate_compliance_fails(self) -> None:
        pe = PolicyEvaluator()
        result = pe.evaluate(compliance_score=0.0)
        assert not result.compliance_passed
        assert not result.overall_passed
        assert "Compliance policy not fully satisfied" in result.warnings

    def test_evaluate_with_violations(self) -> None:
        pe = PolicyEvaluator()
        violations = ["Safety violation: no PPE", "Compliance breach: unapproved vendor"]
        result = pe.evaluate(violations=violations)
        assert result.violations == violations

    def test_evaluate_candidate(self) -> None:
        pe = PolicyEvaluator()
        candidate = RecommendationCandidate(action="test", confidence=0.8)
        result = pe.evaluate_candidate(candidate)
        assert isinstance(result, PolicyEvalResult)

    def test_evaluate_candidate_low_confidence(self) -> None:
        pe = PolicyEvaluator()
        candidate = RecommendationCandidate(action="test", confidence=0.2)
        result = pe.evaluate_candidate(candidate)
        assert isinstance(result, PolicyEvalResult)


# =============================================================================
# 12. OutcomePredictor
# =============================================================================


class TestOutcomePredictor:
    def test_predict_default(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict()
        assert isinstance(prediction, OutcomePrediction)
        assert prediction.success_probability == 0.3  # 0.5 * 0.6

    def test_predict_high_confidence(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict(confidence=1.0, complexity="low")
        assert prediction.success_probability == 0.8

    def test_predict_low_confidence(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict(confidence=0.1, complexity="high")
        assert prediction.success_probability == 0.04

    def test_predict_cost_savings(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict(confidence=0.8, estimated_cost=10000.0)
        assert prediction.cost_savings == 16000.0

    def test_predict_downtime_reduction(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict(confidence=0.7)
        assert prediction.downtime_reduction == 7.0

    def test_predict_risk_reduction(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict(confidence=0.9)
        assert prediction.risk_reduction == 0.54

    def test_predict_clamps_values(self) -> None:
        op = OutcomePredictor()
        prediction = op.predict(confidence=1.5, estimated_cost=-100.0)
        assert prediction.success_probability <= 1.0
        assert prediction.cost_savings >= 0.0

    def test_predict_batch(self) -> None:
        op = OutcomePredictor()
        candidates = [
            RecommendationCandidate(action="a"),
            RecommendationCandidate(action="b"),
        ]
        predictions = op.predict_batch(candidates)
        assert len(predictions) == 2
        for p in predictions:
            assert isinstance(p, OutcomePrediction)

    def test_predict_batch_empty(self) -> None:
        op = OutcomePredictor()
        assert op.predict_batch([]) == []


# =============================================================================
# 13. RecommendationPortfolio
# =============================================================================


class TestRecommendationPortfolio:
    def test_create_default(self) -> None:
        pc = PortfolioComponent()
        portfolio = pc.create(primary_id="rec-1")
        assert isinstance(portfolio, RecommendationPortfolio)
        assert portfolio.primary_recommendation_id == "rec-1"

    def test_create_with_alternatives(self) -> None:
        pc = PortfolioComponent()
        portfolio = pc.create(
            primary_id="rec-1",
            alternative_ids=["rec-2", "rec-3"],
        )
        assert len(portfolio.alternative_ids) == 2
        assert "rec-2" in portfolio.alternative_ids

    def test_create_with_tradeoffs(self) -> None:
        pc = PortfolioComponent()
        ta = TradeoffAnalysis(primary_id="rec-1", alternative_id="rec-2")
        portfolio = pc.create(
            primary_id="rec-1",
            alternative_ids=["rec-2"],
            tradeoffs=[ta],
        )
        assert len(portfolio.tradeoffs) == 1

    def test_create_with_dependencies(self) -> None:
        pc = PortfolioComponent()
        dm = DependencyManager()
        graph = dm.build_graph(["rec-1", "rec-2"])
        portfolio = pc.create(
            primary_id="rec-1",
            dependencies=graph,
        )
        assert portfolio.dependencies is not None
        assert portfolio.dependencies.graph_id == graph.graph_id

    def test_create_with_outcomes(self) -> None:
        pc = PortfolioComponent()
        outcome = OutcomePrediction(candidate_id="rec-1")
        portfolio = pc.create(
            primary_id="rec-1",
            outcomes=[outcome],
        )
        assert len(portfolio.expected_outcomes) == 1

    def test_create_clamps_confidence(self) -> None:
        pc = PortfolioComponent()
        portfolio = pc.create(primary_id="rec-1", overall_confidence=1.5)
        assert portfolio.overall_confidence == 1.0

    def test_create_negative_confidence(self) -> None:
        pc = PortfolioComponent()
        portfolio = pc.create(primary_id="rec-1", overall_confidence=-1.0)
        assert portfolio.overall_confidence == 0.0

    def test_get_portfolio(self) -> None:
        pc = PortfolioComponent()
        p1 = pc.create(primary_id="rec-1")
        p2 = pc.get_portfolio(p1.portfolio_id)
        assert p2 is not None
        assert p2.portfolio_id == p1.portfolio_id

    def test_get_portfolio_not_found(self) -> None:
        pc = PortfolioComponent()
        assert pc.get_portfolio("nonexistent") is None

    def test_get_all_portfolios(self) -> None:
        pc = PortfolioComponent()
        pc.create(primary_id="rec-1")
        pc.create(primary_id="rec-2")
        assert len(pc.get_all_portfolios()) == 2

    def test_clear(self) -> None:
        pc = PortfolioComponent()
        pc.create(primary_id="rec-1")
        assert pc.count() == 1
        pc.clear()
        assert pc.count() == 0

    def test_count(self) -> None:
        pc = PortfolioComponent()
        assert pc.count() == 0
        pc.create(primary_id="rec-1")
        assert pc.count() == 1


# =============================================================================
# 14. RecommendationTrace
# =============================================================================


class TestRecommendationTrace:
    def test_record_event(self) -> None:
        t = RecommendationTrace()
        record = t.record_event(stage_name="TEST", operation="test")
        assert isinstance(record, TraceRecord)
        assert record.stage_name == "TEST"
        assert record.operation == "test"
        assert record.success

    def test_record_strategy_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_strategy_stage("rec-1")
        assert record.stage_name == "STRATEGY"
        assert record.operation == "select"

    def test_record_generation_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_generation_stage("rec-1")
        assert record.stage_name == "GENERATION"
        assert record.operation == "generate"

    def test_record_ranking_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_ranking_stage("rec-1")
        assert record.stage_name == "RANKING"
        assert record.operation == "rank"

    def test_record_scoring_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_scoring_stage("rec-1")
        assert record.stage_name == "SCORING"
        assert record.operation == "score"

    def test_record_feasibility_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_feasibility_stage("rec-1")
        assert record.stage_name == "FEASIBILITY"
        assert record.operation == "analyze"

    def test_record_cost_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_cost_stage("rec-1")
        assert record.stage_name == "COST"
        assert record.operation == "estimate"

    def test_record_dependency_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_dependency_stage("rec-1")
        assert record.stage_name == "DEPENDENCY"
        assert record.operation == "build"

    def test_record_plan_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_plan_stage("rec-1")
        assert record.stage_name == "PLAN"
        assert record.operation == "build"

    def test_record_timeline_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_timeline_stage("rec-1")
        assert record.stage_name == "TIMELINE"
        assert record.operation == "estimate"

    def test_record_tradeoff_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_tradeoff_stage("rec-1")
        assert record.stage_name == "TRADEOFF"
        assert record.operation == "analyze"

    def test_record_policy_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_policy_stage("rec-1")
        assert record.stage_name == "POLICY"
        assert record.operation == "evaluate"

    def test_record_outcome_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_outcome_stage("rec-1")
        assert record.stage_name == "OUTCOME"
        assert record.operation == "predict"

    def test_record_portfolio_stage(self) -> None:
        t = RecommendationTrace()
        record = t.record_portfolio_stage("rec-1")
        assert record.stage_name == "PORTFOLIO"
        assert record.operation == "create"

    def test_get_by_recommendation_id(self) -> None:
        t = RecommendationTrace()
        t.record_strategy_stage("rec-1")
        t.record_generation_stage("rec-1")
        t.record_strategy_stage("rec-2")
        records = t.get_by_recommendation_id("rec-1")
        assert len(records) == 2

    def test_get_by_stage(self) -> None:
        t = RecommendationTrace()
        t.record_strategy_stage("rec-1")
        t.record_strategy_stage("rec-2")
        t.record_generation_stage("rec-1")
        records = t.get_by_stage("STRATEGY")
        assert len(records) == 2

    def test_get_recent(self) -> None:
        t = RecommendationTrace()
        for i in range(15):
            t.record_event(stage_name=f"stage-{i}", operation="test")
        recent = t.get_recent(5)
        assert len(recent) == 5

    def test_clear(self) -> None:
        t = RecommendationTrace()
        t.record_strategy_stage("rec-1")
        assert t.count() == 1
        t.clear()
        assert t.count() == 0

    def test_count(self) -> None:
        t = RecommendationTrace()
        assert t.count() == 0
        t.record_strategy_stage("rec-1")
        assert t.count() == 1
        t.record_generation_stage("rec-1")
        assert t.count() == 2

    def test_event_with_duration(self) -> None:
        t = RecommendationTrace()
        record = t.record_event(stage_name="TEST", operation="test", duration_ms=150.0)
        assert record.duration_ms == 150.0

    def test_event_with_errors(self) -> None:
        t = RecommendationTrace()
        record = t.record_event(
            stage_name="TEST",
            operation="test",
            success=False,
            errors=["Something went wrong"],
        )
        assert not record.success
        assert "Something went wrong" in record.errors


# =============================================================================
# 15. RecommendationMetricsCollector
# =============================================================================


class TestRecommendationMetricsCollector:
    def test_initial_state(self) -> None:
        mc = RecommendationMetricsCollector()
        snap = mc.snapshot()
        assert snap.candidates_generated == 0
        assert snap.rankings_performed == 0
        assert snap.scores_calculated == 0
        assert snap.policy_violations == 0
        assert snap.portfolios_created == 0
        assert snap.trace_count == 0
        assert snap.average_feasibility == 0.0
        assert snap.average_cost == 0.0
        assert snap.average_confidence == 0.0

    def test_increment_candidates(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_candidates(5)
        assert mc.snapshot().candidates_generated == 5

    def test_increment_rankings(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_rankings(3)
        assert mc.snapshot().rankings_performed == 3

    def test_increment_scores(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_scores(7)
        assert mc.snapshot().scores_calculated == 7

    def test_increment_policy_violations(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_policy_violations(2)
        assert mc.snapshot().policy_violations == 2

    def test_increment_portfolios(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_portfolios(1)
        assert mc.snapshot().portfolios_created == 1

    def test_record_feasibility(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_feasibility(0.85)
        assert mc.snapshot().average_feasibility == 0.85

    def test_record_cost(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_cost(5000.0)
        assert mc.snapshot().average_cost == 5000.0

    def test_record_confidence(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_confidence(0.75)
        assert mc.snapshot().average_confidence == 0.75

    def test_record_trace(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_trace()
        assert mc.snapshot().trace_count == 1

    def test_averages(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_feasibility(0.8)
        mc.record_feasibility(0.6)
        mc.record_cost(1000.0)
        mc.record_cost(3000.0)
        mc.record_confidence(0.9)
        mc.record_confidence(0.7)
        snap = mc.snapshot()
        assert snap.average_feasibility == 0.7
        assert snap.average_cost == 2000.0
        assert snap.average_confidence == 0.8

    def test_increment_negative_clamped(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_candidates(-5)
        assert mc.snapshot().candidates_generated == 0

    def test_record_feasibility_clamped(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.record_feasibility(1.5)
        assert mc.snapshot().average_feasibility == 1.0

    def test_reset(self) -> None:
        mc = RecommendationMetricsCollector()
        mc.increment_candidates(10)
        mc.increment_rankings(5)
        mc.record_cost(5000.0)
        mc.reset()
        snap = mc.snapshot()
        assert snap.candidates_generated == 0
        assert snap.rankings_performed == 0
        assert snap.average_cost == 0.0

    def test_snapshot_type(self) -> None:
        mc = RecommendationMetricsCollector()
        snap = mc.snapshot()
        assert isinstance(snap, RecommendationMetrics)
