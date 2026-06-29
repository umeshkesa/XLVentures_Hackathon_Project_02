"""Phase 2 tests for the Action Manager (Planning, Optimization & Execution Preparation Pipeline).

Tests all 15 execution components, trace, and metrics with
deterministic placeholder implementations.
"""

from __future__ import annotations

import uuid

from adip.actions.contracts.models import ActionPlan, ActionPlanStep, ActionRequest
from adip.actions.enums import ActionPriority, ActionType
from adip.actions.execution.action_graph import ActionGraphBuilder
from adip.actions.execution.action_planner import ActionPlanner
from adip.actions.execution.compensation_strategy import (
    CompensationStrategyManager,
)
from adip.actions.execution.conflict_detector import ResourceConflictDetector
from adip.actions.execution.cost_estimator import ActionCostEstimator
from adip.actions.execution.critical_path import CriticalPathAnalyzer
from adip.actions.execution.dependency_resolver import DependencyResolver
from adip.actions.execution.execution_window import ExecutionWindowManager
from adip.actions.execution.feasibility_analyzer import ActionFeasibilityAnalyzer
from adip.actions.execution.metrics import ActionMetrics
from adip.actions.execution.models import (
    ResourceAllocationResult,
)
from adip.actions.execution.optimization_engine import ActionOptimizationEngine
from adip.actions.execution.parallel_planner import ParallelActionPlanner
from adip.actions.execution.policy_engine import ActionPolicyEngine
from adip.actions.execution.resource_allocator import ResourceAllocator
from adip.actions.execution.risk_evaluator import ActionRiskEvaluator
from adip.actions.execution.timeline import ExecutionTimeline
from adip.actions.execution.trace import ActionTrace

# ═════════════════════════════════════════════════════════════════════════════
# ActionPlanner
# ═════════════════════════════════════════════════════════════════════════════


class TestActionPlanner:
    def make_request(self, action_type: ActionType = ActionType.AUTOMATED) -> ActionRequest:
        return ActionRequest(
            review_decision_id=uuid.uuid4(),
            action_type=action_type,
            priority=ActionPriority.HIGH,
            domain="ENERGY",
            target="turbine-01",
        )

    def test_generate_plan_automated(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.AUTOMATED)
        plan = planner.generate_plan(req)
        assert plan.plan_id is not None
        assert plan.request_id == req.request_id
        assert len(plan.steps) == 3
        assert plan.status == "DRAFT"
        assert plan.is_primary is True

    def test_generate_plan_manual(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.MANUAL)
        plan = planner.generate_plan(req)
        assert len(plan.steps) == 4

    def test_generate_plan_approval(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.APPROVAL)
        plan = planner.generate_plan(req)
        assert len(plan.steps) == 3

    def test_generate_plan_notification(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.NOTIFICATION)
        plan = planner.generate_plan(req)
        assert len(plan.steps) == 3

    def test_generate_plan_workflow(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.WORKFLOW)
        plan = planner.generate_plan(req)
        assert len(plan.steps) == 5

    def test_generate_plan_external(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.EXTERNAL_INTEGRATION)
        plan = planner.generate_plan(req)
        assert len(plan.steps) == 4

    def test_generate_plan_emergency(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.EMERGENCY)
        plan = planner.generate_plan(req)
        assert len(plan.steps) == 4

    def test_validate_plan_valid(self) -> None:
        planner = ActionPlanner()
        req = self.make_request()
        plan = planner.generate_plan(req)
        violations = planner.validate_plan(plan)
        assert violations == []

    def test_validate_plan_empty_steps(self) -> None:
        planner = ActionPlanner()
        req = self.make_request()
        plan = ActionPlan(
            request_id=req.request_id,
            review_decision_id=req.review_decision_id,
            steps=[],
        )
        violations = planner.validate_plan(plan)
        assert "Plan must have at least one step" in violations

    def test_validate_plan_no_name(self) -> None:
        planner = ActionPlanner()
        req = self.make_request()
        plan = ActionPlan(
            request_id=req.request_id,
            review_decision_id=req.review_decision_id,
            steps=[ActionPlanStep(plan_id=uuid.uuid4(), action_type=ActionType.AUTOMATED)],
            name="",
        )
        violations = planner.validate_plan(plan)
        assert "Plan must have a name" in violations

    def test_step_order_sequential(self) -> None:
        planner = ActionPlanner()
        req = self.make_request(ActionType.AUTOMATED)
        plan = planner.generate_plan(req)
        for i, step in enumerate(plan.steps):
            assert step.order == i


# ═════════════════════════════════════════════════════════════════════════════
# ActionGraphBuilder
# ═════════════════════════════════════════════════════════════════════════════


class TestActionGraphBuilder:
    def test_build_graph_empty(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(plan_id="plan-1")
        assert graph.plan_id == "plan-1"
        assert graph.nodes == []
        assert graph.edges == []
        assert graph.is_dag is True

    def test_build_graph_no_edges(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["step-1", "step-2", "step-3"],
        )
        assert len(graph.nodes) == 3
        assert graph.edges == []
        assert graph.is_dag is True

    def test_build_graph_with_edges(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "b", "hard"), ("b", "c", "hard")],
        )
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert graph.is_dag is True
        assert graph.topological_order == ["a", "b", "c"]

    def test_cycle_detection(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "b", "hard"), ("b", "c", "hard"), ("c", "a", "hard")],
        )
        assert graph.has_cycle is True
        assert graph.is_dag is False

    def test_topological_sort(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c", "d"],
            dependencies=[("a", "c", "hard"), ("b", "c", "hard"), ("c", "d", "hard")],
        )
        assert graph.topological_order is not None
        # a and b must come before c, c before d
        assert graph.topological_order.index("c") > graph.topological_order.index("a")
        assert graph.topological_order.index("c") > graph.topological_order.index("b")
        assert graph.topological_order.index("d") > graph.topological_order.index("c")

    def test_level_assignment(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "b", "hard"), ("b", "c", "hard")],
        )
        node_map = {n.step_id: n for n in graph.nodes}
        assert node_map["a"].level == 0
        assert node_map["b"].level == 1
        assert node_map["c"].level == 2

    def test_validate_graph_valid(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "hard")],
        )
        violations = builder.validate_graph(graph)
        assert violations == []

    def test_validate_graph_invalid_edge(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "c", "hard")],
        )
        violations = builder.validate_graph(graph)
        assert any("c" in v for v in violations)

    def test_validate_graph_cycle(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "hard"), ("b", "a", "hard")],
        )
        violations = builder.validate_graph(graph)
        assert any("cycle" in v.lower() for v in violations)


# ═════════════════════════════════════════════════════════════════════════════
# ParallelActionPlanner
# ═════════════════════════════════════════════════════════════════════════════


class TestParallelActionPlanner:
    def test_identify_parallel_groups(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "c", "hard"), ("b", "c", "hard")],
        )
        planner = ParallelActionPlanner()
        groups = planner.identify_parallel_groups(graph)
        assert len(groups) == 2  # level 0 (a,b), level 1 (c)

    def test_parallel_groups_empty_graph(self) -> None:
        planner = ParallelActionPlanner()
        groups = planner.identify_parallel_groups(
            ActionGraphBuilder().build_graph(plan_id="p")
        )
        assert groups == []

    def test_parallel_groups_cycle_graph(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "hard"), ("b", "a", "hard")],
        )
        planner = ParallelActionPlanner()
        groups = planner.identify_parallel_groups(graph)
        assert groups == []

    def test_optimize_parallelism_unlimited(self) -> None:
        planner = ParallelActionPlanner()
        from adip.actions.execution.models import ParallelGroup
        groups = [
            ParallelGroup(level=0, step_ids=["a", "b", "c"]),
        ]
        result = planner.optimize_parallelism(groups, max_parallel=0)
        assert len(result) == 1

    def test_optimize_parallelism_limited(self) -> None:
        planner = ParallelActionPlanner()
        from adip.actions.execution.models import ParallelGroup
        groups = [
            ParallelGroup(level=0, step_ids=["a", "b", "c", "d", "e"]),
        ]
        result = planner.optimize_parallelism(groups, max_parallel=2)
        assert len(result) == 3  # 5 steps split into groups of 2, 2, 1

    def test_parallel_group_levels(self) -> None:
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c", "d"],
            dependencies=[("a", "c", "hard"), ("b", "c", "hard"), ("c", "d", "hard")],
        )
        planner = ParallelActionPlanner()
        groups = planner.identify_parallel_groups(graph)
        levels = sorted(g.level for g in groups)
        assert levels == [0, 1, 2]


# ═════════════════════════════════════════════════════════════════════════════
# CriticalPathAnalyzer
# ═════════════════════════════════════════════════════════════════════════════


class TestCriticalPathAnalyzer:
    def test_analyze_empty_graph(self) -> None:
        analyzer = CriticalPathAnalyzer()
        builder = ActionGraphBuilder()
        graph = builder.build_graph(plan_id="plan-1")
        path = analyzer.analyze(graph)
        assert path.total_duration_minutes == 0
        assert path.step_ids == []

    def test_analyze_cycle_graph(self) -> None:
        analyzer = CriticalPathAnalyzer()
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "hard"), ("b", "a", "hard")],
        )
        path = analyzer.analyze(graph)
        assert path.total_duration_minutes == 0

    def test_analyze_single_path(self) -> None:
        analyzer = CriticalPathAnalyzer()
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "b", "hard"), ("b", "c", "hard")],
        )
        # Set durations via node metadata
        for node in graph.nodes:
            if node.step_id == "a":
                node.duration_minutes = 10
            elif node.step_id == "b":
                node.duration_minutes = 20
            elif node.step_id == "c":
                node.duration_minutes = 15
        path = analyzer.analyze(graph)
        assert path.total_duration_minutes == 10 + 20 + 15
        assert "a" in path.step_ids
        assert "b" in path.step_ids
        assert "c" in path.step_ids

    def test_analyze_parallel_paths(self) -> None:
        analyzer = CriticalPathAnalyzer()
        builder = ActionGraphBuilder()
        # a -> c (10 -> 30) and b -> c (20 -> 30), critical path is b -> c
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "c", "hard"), ("b", "c", "hard")],
        )
        for node in graph.nodes:
            if node.step_id == "a":
                node.duration_minutes = 10
            elif node.step_id == "b":
                node.duration_minutes = 20
            elif node.step_id == "c":
                node.duration_minutes = 30
        path = analyzer.analyze(graph)
        assert path.total_duration_minutes == 50  # max(10,20) + 30
        assert "c" in path.step_ids

    def test_bottleneck_detection(self) -> None:
        analyzer = CriticalPathAnalyzer()
        builder = ActionGraphBuilder()
        graph = builder.build_graph(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "hard")],
        )
        for node in graph.nodes:
            if node.step_id == "b":
                node.duration_minutes = 120  # >= 60 => bottleneck
        path = analyzer.analyze(graph)
        assert "b" in path.bottleneck_step_ids


# ═════════════════════════════════════════════════════════════════════════════
# DependencyResolver
# ═════════════════════════════════════════════════════════════════════════════


class TestDependencyResolver:
    def test_resolve_hard_dependencies(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve_dependencies(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "b", "hard"), ("b", "c", "hard")],
        )
        assert "b" in result.hard_dependencies
        assert "c" in result.hard_dependencies

    def test_resolve_soft_dependencies(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve_dependencies(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "soft")],
        )
        assert "b" in result.soft_dependencies

    def test_resolve_optional_dependencies(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve_dependencies(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "optional")],
        )
        assert "b" in result.optional_dependencies

    def test_resolve_unresolved(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve_dependencies(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "unknown")],
        )
        assert "b" in result.unresolved_dependencies

    def test_validate_dependencies_valid(self) -> None:
        resolver = DependencyResolver()
        violations = resolver.validate_dependencies(
            plan_id="plan-1",
            step_ids=["a", "b"],
            dependencies=[("a", "b", "hard")],
        )
        assert violations == []

    def test_validate_dependencies_invalid_source(self) -> None:
        resolver = DependencyResolver()
        violations = resolver.validate_dependencies(
            plan_id="plan-1",
            step_ids=["a"],
            dependencies=[("x", "a", "hard")],
        )
        assert any("x" in v for v in violations)

    def test_validate_dependencies_self_ref(self) -> None:
        resolver = DependencyResolver()
        violations = resolver.validate_dependencies(
            plan_id="plan-1",
            step_ids=["a"],
            dependencies=[("a", "a", "hard")],
        )
        assert any("Self-referencing" in v for v in violations)

    def test_get_execution_order(self) -> None:
        resolver = DependencyResolver()
        result = resolver.resolve_dependencies(
            plan_id="plan-1",
            step_ids=["a", "b"],
        )
        order = resolver.get_execution_order(result)
        assert len(order) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ResourceAllocator
# ═════════════════════════════════════════════════════════════════════════════


class TestResourceAllocator:
    def test_allocate_resources(self) -> None:
        allocator = ResourceAllocator()
        result = allocator.allocate_resources(
            plan_id="plan-1",
            step_ids=["step-1", "step-2"],
        )
        assert result.plan_id == "plan-1"
        assert "step-1" in result.personnel
        assert "step-2" in result.personnel
        assert result.total_personnel == 4  # 2 per step
        assert result.total_equipment == 4  # 2 per step
        assert result.budget > 0

    def test_allocate_resources_empty(self) -> None:
        allocator = ResourceAllocator()
        result = allocator.allocate_resources(plan_id="plan-1")
        assert result.personnel == {}

    def test_validate_resources_valid(self) -> None:
        allocator = ResourceAllocator()
        violations = allocator.validate_resources(
            plan_id="plan-1",
            step_ids=["step-1"],
        )
        assert violations == []

    def test_validate_resources_no_steps(self) -> None:
        allocator = ResourceAllocator()
        violations = allocator.validate_resources(plan_id="plan-1")
        assert "No steps" in violations[0]


# ═════════════════════════════════════════════════════════════════════════════
# ResourceConflictDetector
# ═════════════════════════════════════════════════════════════════════════════


class TestResourceConflictDetector:
    def test_detect_conflicts_no_conflicts(self) -> None:
        detector = ResourceConflictDetector()
        allocation = ResourceAllocationResult(plan_id="plan-1")
        allocation.personnel = {"a": ["p1"], "b": ["p2"]}
        conflicts = detector.detect_conflicts(
            plan_id="plan-1",
            allocation=allocation,
            step_ids=["a", "b"],
        )
        double_booked = detector.get_double_booking_conflicts(conflicts)
        assert double_booked == []

    def test_detect_double_booking(self) -> None:
        detector = ResourceConflictDetector()
        allocation = ResourceAllocationResult(plan_id="plan-1")
        allocation.personnel = {"a": ["engineer-1"], "b": ["engineer-1"]}
        conflicts = detector.detect_conflicts(
            plan_id="plan-1",
            allocation=allocation,
            step_ids=["a", "b"],
        )
        double_booked = detector.get_double_booking_conflicts(conflicts)
        assert len(double_booked) == 1
        assert double_booked[0].resource_id == "engineer-1"

    def test_detect_capacity_conflict(self) -> None:
        detector = ResourceConflictDetector()
        allocation = ResourceAllocationResult(plan_id="plan-1")
        allocation.personnel = {"a": [f"p{i}" for i in range(6)]}
        conflicts = detector.detect_conflicts(
            plan_id="plan-1",
            allocation=allocation,
            step_ids=["a"],
        )
        capacity = detector.get_capacity_conflicts(conflicts)
        assert len(capacity) == 1

    def test_validate_no_conflicts(self) -> None:
        detector = ResourceConflictDetector()
        from adip.actions.execution.models import ResourceConflict
        conflicts = [
            ResourceConflict(
                plan_id="p", resource_type="personnel", resource_id="r1",
                conflict_type="double_booking", step_ids=["a", "b"],
                description="Double booking",
            )
        ]
        issues = detector.validate_no_conflicts(conflicts)
        assert len(issues) == 1


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionWindowManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionWindowManager:
    def test_create_immediate_window(self) -> None:
        mgr = ExecutionWindowManager()
        window = mgr.create_window(window_type="immediate")
        assert window.window_type == "immediate"
        assert window.scheduled_start is not None
        assert window.scheduled_end is not None

    def test_create_scheduled_window(self) -> None:
        mgr = ExecutionWindowManager()
        window = mgr.create_window(window_type="scheduled")
        assert window.window_type == "scheduled"

    def test_create_maintenance_window(self) -> None:
        mgr = ExecutionWindowManager()
        window = mgr.create_window(window_type="maintenance")
        assert window.window_type == "maintenance"

    def test_create_business_hours_window(self) -> None:
        mgr = ExecutionWindowManager()
        window = mgr.create_window(window_type="business_hours")
        assert window.window_type == "business_hours"

    def test_create_emergency_window(self) -> None:
        mgr = ExecutionWindowManager()
        window = mgr.create_window(window_type="emergency")
        assert window.window_type == "emergency"

    def test_validate_valid_window(self) -> None:
        mgr = ExecutionWindowManager()
        window = mgr.create_window(window_type="immediate")
        violations = mgr.validate_window(window)
        assert violations == []

    def test_validate_invalid_type(self) -> None:
        mgr = ExecutionWindowManager()
        from adip.actions.execution.models import ExecutionWindow
        window = ExecutionWindow(window_type="invalid_type")
        violations = mgr.validate_window(window)
        assert any("Invalid" in v for v in violations)

    def test_get_window_types(self) -> None:
        mgr = ExecutionWindowManager()
        types = mgr.get_window_types()
        assert "immediate" in types
        assert "emergency" in types
        assert len(types) == 5

    def test_estimate_duration(self) -> None:
        mgr = ExecutionWindowManager()
        assert mgr.estimate_duration_minutes("immediate") == 60
        assert mgr.estimate_duration_minutes("emergency") == 30


# ═════════════════════════════════════════════════════════════════════════════
# CompensationStrategyManager
# ═════════════════════════════════════════════════════════════════════════════


class TestCompensationStrategyManager:
    def test_create_rollback_strategy(self) -> None:
        mgr = CompensationStrategyManager()
        strategy = mgr.create_strategy(step_id="step-1", strategy_type="rollback")
        assert strategy.strategy_type == "rollback"
        assert strategy.step_id == "step-1"
        assert "rollback" in strategy.description.lower()

    def test_create_compensation_strategy(self) -> None:
        mgr = CompensationStrategyManager()
        strategy = mgr.create_strategy(step_id="step-1", strategy_type="compensation")
        assert strategy.strategy_type == "compensation"

    def test_create_retry_strategy(self) -> None:
        mgr = CompensationStrategyManager()
        strategy = mgr.create_strategy(step_id="step-1", strategy_type="retry")
        assert strategy.strategy_type == "retry"
        assert strategy.parameters.get("max_retries") == 3

    def test_create_manual_recovery(self) -> None:
        mgr = CompensationStrategyManager()
        strategy = mgr.create_strategy(step_id="step-1", strategy_type="manual_recovery")
        assert strategy.strategy_type == "manual_recovery"

    def test_create_alternative_strategy(self) -> None:
        mgr = CompensationStrategyManager()
        strategy = mgr.create_strategy(step_id="step-1", strategy_type="alternative")
        assert strategy.strategy_type == "alternative"

    def test_get_default_strategies(self) -> None:
        mgr = CompensationStrategyManager()
        strategies = mgr.get_default_strategies(step_ids=["a", "b", "c"])
        assert len(strategies) == 3
        assert all(s.strategy_type == "rollback" for s in strategies)

    def test_validate_valid_strategy(self) -> None:
        mgr = CompensationStrategyManager()
        strategy = mgr.create_strategy(step_id="s1", strategy_type="rollback")
        violations = mgr.validate_strategy(strategy)
        assert violations == []

    def test_validate_invalid_type(self) -> None:
        mgr = CompensationStrategyManager()
        from adip.actions.execution.models import CompensationStrategy
        strategy = CompensationStrategy(step_id="s1", strategy_type="unknown")
        violations = mgr.validate_strategy(strategy)
        assert any("Invalid" in v for v in violations)


# ═════════════════════════════════════════════════════════════════════════════
# ActionCostEstimator
# ═════════════════════════════════════════════════════════════════════════════


class TestActionCostEstimator:
    def test_estimate_costs(self) -> None:
        estimator = ActionCostEstimator()
        estimate = estimator.estimate_costs(plan_id="plan-1", step_count=3)
        assert estimate.plan_id == "plan-1"
        assert estimate.labor_cost > 0
        assert estimate.equipment_cost > 0
        assert estimate.downtime_cost > 0
        assert estimate.materials_cost > 0
        assert estimate.external_services_cost > 0
        assert estimate.total_cost > 0

    def test_estimate_costs_zero_steps(self) -> None:
        estimator = ActionCostEstimator()
        estimate = estimator.estimate_costs(plan_id="plan-1", step_count=0)
        assert estimate.total_cost == 0.0

    def test_estimate_step_cost(self) -> None:
        estimator = ActionCostEstimator()
        assert estimator.estimate_step_cost(step_type="manual") == 500.0
        assert estimator.estimate_step_cost(step_type="automated") == 100.0
        assert estimator.estimate_step_cost(step_type="emergency") == 1000.0

    def test_get_cost_breakdown(self) -> None:
        estimator = ActionCostEstimator()
        estimate = estimator.estimate_costs(plan_id="plan-1", step_count=2)
        breakdown = estimator.get_cost_breakdown(estimate)
        assert "labor" in breakdown
        assert "equipment" in breakdown
        assert "downtime" in breakdown
        assert "materials" in breakdown
        assert "external_services" in breakdown


# ═════════════════════════════════════════════════════════════════════════════
# ActionRiskEvaluator
# ═════════════════════════════════════════════════════════════════════════════


class TestActionRiskEvaluator:
    def test_evaluate_low_risk(self) -> None:
        evaluator = ActionRiskEvaluator()
        result = evaluator.evaluate(
            plan_id="plan-1",
            action_type="AUTOMATED",
            priority="LOW",
            step_count=2,
        )
        assert result.overall_risk == "LOW"

    def test_evaluate_emergency_risk(self) -> None:
        evaluator = ActionRiskEvaluator()
        result = evaluator.evaluate(
            plan_id="plan-1",
            action_type="EMERGENCY",
            priority="CRITICAL",
            step_count=1,
        )
        assert result.overall_risk == "CRITICAL"
        assert result.operational_risk == "CRITICAL"
        assert result.safety_risk == "CRITICAL"

    def test_evaluate_safety_domain(self) -> None:
        evaluator = ActionRiskEvaluator()
        result = evaluator.evaluate(
            plan_id="plan-1",
            action_type="MANUAL",
            domain="SAFETY",
        )
        assert result.safety_risk == "HIGH"

    def test_evaluate_risk_factors(self) -> None:
        evaluator = ActionRiskEvaluator()
        result = evaluator.evaluate(
            plan_id="plan-1",
            action_type="EMERGENCY",
            priority="CRITICAL",
            domain="ENERGY",
        )
        assert len(result.risk_factors) > 0


# ═════════════════════════════════════════════════════════════════════════════
# ActionPolicyEngine
# ═════════════════════════════════════════════════════════════════════════════


class TestActionPolicyEngine:
    def test_validate_compliant(self) -> None:
        engine = ActionPolicyEngine()
        result = engine.validate(
            plan_id="plan-1",
            action_type="AUTOMATED",
            priority="LOW",
            step_count=2,
        )
        assert result.is_policy_compliant is True

    def test_validate_safety_violation(self) -> None:
        engine = ActionPolicyEngine()
        result = engine.validate(
            plan_id="plan-1",
            action_type="MANUAL",
            domain="ENERGY",
        )
        assert len(result.safety_policy_violations) > 0

    def test_validate_business_violation(self) -> None:
        engine = ActionPolicyEngine()
        result = engine.validate(
            plan_id="plan-1",
            priority="HIGH",
            step_count=6,
        )
        assert len(result.business_policy_violations) > 0

    def test_validate_compliance_violation(self) -> None:
        engine = ActionPolicyEngine()
        result = engine.validate(
            plan_id="plan-1",
            action_type="EXTERNAL_INTEGRATION",
        )
        assert len(result.compliance_policy_violations) > 0

    def test_check_policy_compliance(self) -> None:
        engine = ActionPolicyEngine()
        result = engine.validate(plan_id="plan-1")
        assert engine.check_policy_compliance(plan_id="plan-1", result=result) is True


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionTimeline
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionTimeline:
    def test_generate_timeline(self) -> None:
        timeline = ExecutionTimeline()
        graph = ActionGraphBuilder().build_graph(
            plan_id="plan-1",
            step_ids=["a", "b", "c"],
            dependencies=[("a", "c", "hard"), ("b", "c", "hard")],
        )
        parallel_groups = ParallelActionPlanner().identify_parallel_groups(graph)
        critical_path = CriticalPathAnalyzer().analyze(graph)
        entries = timeline.generate(
            plan_id="plan-1",
            graph=graph,
            parallel_groups=parallel_groups,
            critical_path=critical_path,
        )
        assert len(entries) == 3

    def test_timeline_entries_have_sequence(self) -> None:
        timeline = ExecutionTimeline()
        from adip.actions.execution.models import ParallelGroup
        entries = timeline.generate(
            plan_id="plan-1",
            parallel_groups=[ParallelGroup(level=0, step_ids=["a", "b"])],
        )
        assert entries[0].sequence == 0
        assert entries[1].sequence == 1

    def test_get_total_duration(self) -> None:
        timeline = ExecutionTimeline()
        from adip.actions.execution.models import ParallelGroup
        entries = timeline.generate(
            plan_id="plan-1",
            parallel_groups=[ParallelGroup(level=0, step_ids=["a"])],
        )
        duration = timeline.get_total_duration_minutes(entries)
        assert duration >= 0

    def test_get_critical_entries(self) -> None:
        timeline = ExecutionTimeline()
        from adip.actions.execution.models import TimelineEntry
        entries = [
            TimelineEntry(plan_id="p", step_id="a", step_name="A", is_critical=True),
            TimelineEntry(plan_id="p", step_id="b", step_name="B", is_critical=False),
        ]
        critical = timeline.get_critical_entries(entries)
        assert len(critical) == 1


# ═════════════════════════════════════════════════════════════════════════════
# ActionOptimizationEngine
# ═════════════════════════════════════════════════════════════════════════════


class TestActionOptimizationEngine:
    def test_optimize(self) -> None:
        engine = ActionOptimizationEngine()
        from adip.actions.execution.models import CostEstimate, CriticalPath
        cost = CostEstimate(plan_id="plan-1", total_cost=10000.0)
        path = CriticalPath(plan_id="plan-1", total_duration_minutes=120)
        result = engine.optimize(
            plan_id="plan-1",
            cost_estimate=cost,
            critical_path=path,
            step_count=5,
        )
        assert result.optimized_cost < result.original_cost
        assert result.optimized_duration_minutes < result.original_duration_minutes
        assert result.cost_savings > 0
        assert len(result.improvements) > 0

    def test_optimization_score_range(self) -> None:
        engine = ActionOptimizationEngine()
        result = engine.optimize(plan_id="plan-1", step_count=3)
        assert 0.0 <= result.optimization_score <= 1.0


# ═════════════════════════════════════════════════════════════════════════════
# ActionFeasibilityAnalyzer
# ═════════════════════════════════════════════════════════════════════════════


class TestActionFeasibilityAnalyzer:
    def test_analyze_feasible(self) -> None:
        analyzer = ActionFeasibilityAnalyzer()
        result = analyzer.analyze(
            plan_id="plan-1",
            budget_required=50000.0,
            step_count=5,
        )
        assert result.is_feasible is True
        assert result.resource_available is True
        assert result.budget_available is True

    def test_analyze_resource_exceeded(self) -> None:
        analyzer = ActionFeasibilityAnalyzer()
        allocation = ResourceAllocationResult(plan_id="plan-1", total_personnel=25)
        result = analyzer.analyze(
            plan_id="plan-1",
            allocation=allocation,
            step_count=3,
        )
        assert result.resource_available is False

    def test_analyze_budget_exceeded(self) -> None:
        analyzer = ActionFeasibilityAnalyzer()
        result = analyzer.analyze(
            plan_id="plan-1",
            budget_required=200000.0,
            step_count=3,
        )
        assert result.budget_available is False

    def test_analyze_skills_exceeded(self) -> None:
        analyzer = ActionFeasibilityAnalyzer()
        result = analyzer.analyze(
            plan_id="plan-1",
            step_count=15,
        )
        assert result.skills_available is False

    def test_issues_populated_when_infeasible(self) -> None:
        analyzer = ActionFeasibilityAnalyzer()
        result = analyzer.analyze(
            plan_id="plan-1",
            budget_required=200000.0,
            step_count=60,
        )
        assert len(result.issues) > 0
        assert result.is_feasible is False


# ═════════════════════════════════════════════════════════════════════════════
# ActionTrace
# ═════════════════════════════════════════════════════════════════════════════


class TestActionTrace:
    def test_record_stage(self) -> None:
        trace = ActionTrace()
        record = trace.record_stage(
            stage_name="planning",
            plan_id="plan-1",
            details="Generated plan",
        )
        assert record.stage_name == "planning"
        assert record.plan_id == "plan-1"
        assert trace.count() == 1

    def test_record_planning(self) -> None:
        trace = ActionTrace()
        trace.record_planning(plan_id="p1")
        assert trace.count() == 1

    def test_record_optimization(self) -> None:
        trace = ActionTrace()
        trace.record_optimization(plan_id="p1")
        assert trace.count() == 1

    def test_record_dependency(self) -> None:
        trace = ActionTrace()
        trace.record_dependency(plan_id="p1")
        assert trace.count() == 1

    def test_record_resource(self) -> None:
        trace = ActionTrace()
        trace.record_resource(plan_id="p1")
        assert trace.count() == 1

    def test_record_cost(self) -> None:
        trace = ActionTrace()
        trace.record_cost(plan_id="p1")
        assert trace.count() == 1

    def test_record_timeline(self) -> None:
        trace = ActionTrace()
        trace.record_timeline(plan_id="p1")
        assert trace.count() == 1

    def test_record_risk(self) -> None:
        trace = ActionTrace()
        trace.record_risk(plan_id="p1")
        assert trace.count() == 1

    def test_record_policy(self) -> None:
        trace = ActionTrace()
        trace.record_policy(plan_id="p1")
        assert trace.count() == 1

    def test_record_conflict(self) -> None:
        trace = ActionTrace()
        trace.record_conflict(plan_id="p1")
        assert trace.count() == 1

    def test_record_feasibility(self) -> None:
        trace = ActionTrace()
        trace.record_feasibility(plan_id="p1")
        assert trace.count() == 1

    def test_record_graph(self) -> None:
        trace = ActionTrace()
        trace.record_graph(plan_id="p1")
        assert trace.count() == 1

    def test_record_execution_window(self) -> None:
        trace = ActionTrace()
        trace.record_execution_window(plan_id="p1")
        assert trace.count() == 1

    def test_record_compensation(self) -> None:
        trace = ActionTrace()
        trace.record_compensation(plan_id="p1")
        assert trace.count() == 1

    def test_query_methods(self) -> None:
        trace = ActionTrace()
        trace.record_planning(plan_id="p1")
        trace.record_optimization(plan_id="p2")
        assert len(trace.get_by_plan_id("p1")) == 1
        assert len(trace.get_by_operation("planning")) == 1
        assert len(trace.get_by_stage("planning")) == 1

    def test_get_recent(self) -> None:
        trace = ActionTrace()
        for _ in range(5):
            trace.record_planning(plan_id="p1")
        recent = trace.get_recent(limit=3)
        assert len(recent) == 3

    def test_clear(self) -> None:
        trace = ActionTrace()
        trace.record_planning(plan_id="p1")
        trace.clear()
        assert trace.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# ActionMetrics
# ═════════════════════════════════════════════════════════════════════════════


class TestActionMetrics:
    def test_record_plan(self) -> None:
        metrics = ActionMetrics()
        metrics.record_plan(action_type="AUTOMATED", step_count=3)
        assert metrics.get_plans_total() == 1
        assert metrics.get_tasks_total() == 3

    def test_record_resource_allocation(self) -> None:
        metrics = ActionMetrics()
        metrics.record_resource_allocation(10)
        assert metrics.get_resources_allocated() == 10

    def test_record_conflict(self) -> None:
        metrics = ActionMetrics()
        metrics.record_conflict()
        assert metrics.get_conflicts_detected() == 1

    def test_record_planning_time(self) -> None:
        metrics = ActionMetrics()
        metrics.record_planning_time(150.0)
        assert metrics.get_average_planning_time_ms() == 150.0

    def test_record_optimization_score(self) -> None:
        metrics = ActionMetrics()
        metrics.record_optimization_score(0.85)
        assert metrics.get_average_optimization_score() == 0.85

    def test_record_cost_and_duration(self) -> None:
        metrics = ActionMetrics()
        metrics.record_plan(action_type="AUTOMATED")
        metrics.record_cost(5000.0)
        metrics.record_duration(120)
        assert metrics.get_average_cost() == 5000.0
        assert metrics.get_average_duration_minutes() == 120.0

    def test_plan_types(self) -> None:
        metrics = ActionMetrics()
        metrics.record_plan(action_type="AUTOMATED")
        metrics.record_plan(action_type="MANUAL")
        snapshot = metrics.snapshot()
        assert snapshot.plans_per_action_type.get("AUTOMATED") == 1
        assert snapshot.plans_per_action_type.get("MANUAL") == 1

    def test_snapshot(self) -> None:
        metrics = ActionMetrics()
        metrics.record_plan(action_type="AUTOMATED", step_count=3)
        metrics.record_resource_allocation(5)
        metrics.record_conflict()
        snap = metrics.snapshot()
        assert snap.plans_total == 1
        assert snap.tasks_total == 3
        assert snap.resources_allocated == 5
        assert snap.conflicts_detected == 1

    def test_reset(self) -> None:
        metrics = ActionMetrics()
        metrics.record_plan(action_type="AUTOMATED")
        metrics.reset()
        assert metrics.get_plans_total() == 0

    def test_optimization_score_clamped(self) -> None:
        metrics = ActionMetrics()
        metrics.record_optimization_score(1.5)
        assert metrics.get_average_optimization_score() == 1.0
        metrics.record_optimization_score(-0.5)
        assert metrics.get_average_optimization_score() == 0.5  # (1.0 + 0.0) / 2

    def test_empty_metrics_defaults(self) -> None:
        metrics = ActionMetrics()
        assert metrics.get_average_planning_time_ms() == 0.0
        assert metrics.get_average_optimization_score() == 0.0
        assert metrics.get_average_cost() == 0.0
