"""Unit tests for the PlannerAgent orchestrator (Phase 3.5)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from adip.planner.components.capability_matcher import (
    DeterministicCapabilityMatcher,
)
from adip.planner.components.confidence_calculator import (
    DeterministicConfidenceCalculator,
)
from adip.planner.components.context_analyzer import (
    DeterministicContextAnalyzer,
)
from adip.planner.components.execution_dispatcher import (
    DeterministicExecutionDispatcher,
)
from adip.planner.components.goal_analyzer import DeterministicGoalAnalyzer
from adip.planner.components.plan_generator import DeterministicPlanGenerator
from adip.planner.components.plan_optimizer import DeterministicPlanOptimizer
from adip.planner.components.plan_validator import DeterministicPlanValidator
from adip.planner.components.planner_agent import PlannerAgent
from adip.planner.components.replanner import DeterministicReplanner
from adip.planner.components.strategy_selector import (
    DeterministicStrategySelector,
)
from adip.planner.components.task_decomposer import (
    DeterministicTaskDecomposer,
)
from adip.planner.contracts.models import (
    ExecutionPlan,
    PlanningContext,
    PlanningGoal,
    PlanningRequest,
    PlanningResult,
    PlanningTask,
    ValidationResult,
)
from adip.planner.contracts.policy import PlanningPolicy
from adip.planner.enums import (
    PlanningStatusEnum,
    PriorityEnum,
    TaskStatusEnum,
)

# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def planner_agent() -> PlannerAgent:
    return PlannerAgent(
        goal_analyzer=DeterministicGoalAnalyzer(),
        context_analyzer=DeterministicContextAnalyzer(),
        strategy_selector=DeterministicStrategySelector(),
        capability_matcher=DeterministicCapabilityMatcher(),
        task_decomposer=DeterministicTaskDecomposer(),
        plan_generator=DeterministicPlanGenerator(),
        plan_validator=DeterministicPlanValidator(),
        confidence_calculator=DeterministicConfidenceCalculator(),
        plan_optimizer=DeterministicPlanOptimizer(),
        execution_dispatcher=DeterministicExecutionDispatcher(),
        replanner=DeterministicReplanner(),
    )


@pytest.fixture
def sample_request() -> PlanningRequest:
    return PlanningRequest(
        context=PlanningContext(
            timestamp=datetime.now(UTC),
        ),
        goal=PlanningGoal(
            objective="Search the database and compute the average. Then generate a report.",
            priority=PriorityEnum.HIGH,
        ),
    )


@pytest.fixture
def simple_request() -> PlanningRequest:
    return PlanningRequest(
        context=PlanningContext(
            timestamp=datetime.now(UTC),
        ),
        goal=PlanningGoal(
            objective="Run a single task.",
        ),
    )


@pytest.fixture
def custom_result() -> PlanningResult:
    return PlanningResult(
        request_id=uuid.uuid4(),
        execution_status=PlanningStatusEnum.CREATED,
    )


# ── Happy path ──────────────────────────────────────────────────────────


class TestPlannerAgentHappyPath:
    async def test_create_plan_returns_result(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert isinstance(result, PlanningResult)
        assert result.execution_status == PlanningStatusEnum.COMPLETED
        assert result.plan is not None

    async def test_plan_alias(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.plan(sample_request)
        assert isinstance(result, PlanningResult)
        assert result.execution_status == PlanningStatusEnum.COMPLETED

    async def test_creates_valid_execution_plan(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.plan is not None
        assert len(result.plan.tasks) > 0
        assert result.plan.goal.objective == sample_request.goal.objective

    async def test_all_tasks_are_dispatched(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.plan is not None
        for task in result.plan.tasks:
            assert task.status in (
                TaskStatusEnum.IN_PROGRESS,
                TaskStatusEnum.PENDING,
            )

    async def test_validation_is_valid(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.validation_status.is_valid is True
        assert result.validation_status.errors == []

    async def test_final_decision_present(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.final_decision is not None
        assert "completed" in result.final_decision.reasoning.lower()

    async def test_metrics_collected(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.metrics.planning_duration_ms >= 0
        assert result.metrics.generated_tasks > 0
        assert result.metrics.capabilities_matched > 0

    async def test_capabilities_matched(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.metrics.capabilities_matched > 0
        assert result.plan is not None
        for task in result.plan.tasks:
            if "search" in task.description.lower():
                assert len(task.matched_capabilities) > 0
                break

    async def test_single_sentence_request(
        self, planner_agent: PlannerAgent, simple_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(simple_request)
        assert result.execution_status == PlanningStatusEnum.COMPLETED
        assert result.plan is not None
        assert len(result.plan.tasks) == 1

    async def test_traces_collected(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert len(result.traces) >= 4  # at least goal, context, strategy, decomposition
        assert all(t.success for t in result.traces)
        stage_names = [t.stage_name for t in result.traces]
        assert "goal_analyzer" in stage_names
        assert "context_analyzer" in stage_names
        assert "strategy_selector" in stage_names
        assert "task_decomposer" in stage_names
        assert "plan_generator" in stage_names
        assert "plan_validator" in stage_names

    async def test_confidence_in_plan(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.plan is not None
        assert result.plan.confidence is not None
        assert 0.0 <= result.plan.confidence <= 100.0


# ── State transitions ───────────────────────────────────────────────────


class TestPlannerAgentStateTransitions:
    async def test_completed_final_state(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.COMPLETED

    async def test_failed_state_on_validation_error(
        self, sample_request: PlanningRequest
    ) -> None:
        failing_validator = AsyncMock()
        failing_validator.validate.return_value = ValidationResult(
            is_valid=False,
            errors=["Simulated failure"],
        )
        agent = PlannerAgent(
            goal_analyzer=DeterministicGoalAnalyzer(),
            context_analyzer=DeterministicContextAnalyzer(),
            strategy_selector=DeterministicStrategySelector(),
            capability_matcher=DeterministicCapabilityMatcher(),
            task_decomposer=DeterministicTaskDecomposer(),
            plan_generator=DeterministicPlanGenerator(),
            plan_validator=failing_validator,
            confidence_calculator=DeterministicConfidenceCalculator(),
            plan_optimizer=DeterministicPlanOptimizer(),
            execution_dispatcher=DeterministicExecutionDispatcher(),
            replanner=DeterministicReplanner(),
        )
        result = await agent.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.FAILED
        assert result.validation_status.is_valid is False
        assert "Simulated failure" in result.validation_status.errors

    async def test_failed_state_on_exception(
        self, sample_request: PlanningRequest
    ) -> None:
        broken_analyzer = AsyncMock()
        broken_analyzer.analyze.side_effect = RuntimeError("Unexpected error")
        agent = PlannerAgent(
            goal_analyzer=broken_analyzer,
            context_analyzer=DeterministicContextAnalyzer(),
            strategy_selector=DeterministicStrategySelector(),
            capability_matcher=DeterministicCapabilityMatcher(),
            task_decomposer=DeterministicTaskDecomposer(),
            plan_generator=DeterministicPlanGenerator(),
            plan_validator=DeterministicPlanValidator(),
            confidence_calculator=DeterministicConfidenceCalculator(),
            plan_optimizer=DeterministicPlanOptimizer(),
            execution_dispatcher=DeterministicExecutionDispatcher(),
            replanner=DeterministicReplanner(),
        )
        result = await agent.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.FAILED


# ── Replanner delegation ────────────────────────────────────────────────


class TestPlannerAgentReplan:
    async def test_replan_delegates_to_replanner(
        self, planner_agent: PlannerAgent
    ) -> None:
        t1 = PlanningTask(
            task_id=uuid.uuid4(),
            description="Pending task",
        )
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=[t1],
        )
        context = PlanningContext(timestamp=datetime.now(UTC))
        goal = PlanningGoal(objective="Test goal")

        new_plan = await planner_agent.replan(
            plan, context, "Something went wrong", goal
        )
        assert new_plan is not None
        assert len(new_plan.tasks) == 1
        assert all(t.status == TaskStatusEnum.PENDING for t in new_plan.tasks)

    async def test_replan_returns_none_when_no_pending(
        self, planner_agent: PlannerAgent
    ) -> None:
        t1 = PlanningTask(
            task_id=uuid.uuid4(),
            description="Done",
            status=TaskStatusEnum.COMPLETED,
        )
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=[t1],
        )
        context = PlanningContext(timestamp=datetime.now(UTC))
        goal = PlanningGoal(objective="Test goal")

        result = await planner_agent.replan(
            plan, context, "All done", goal
        )
        assert result is None


# ── Metrics tracking ────────────────────────────────────────────────────


class TestPlannerAgentMetrics:
    async def test_metrics_are_positive(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.metrics.planning_duration_ms >= 0
        assert result.metrics.tasks_processed > 0

    async def test_tasks_processed_matches_plan(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.plan is not None
        assert result.metrics.tasks_processed == len(result.plan.tasks)

    async def test_metrics_not_zero_on_failure(
        self, sample_request: PlanningRequest
    ) -> None:
        failing_validator = AsyncMock()
        failing_validator.validate.return_value = ValidationResult(
            is_valid=False,
            errors=["Failure"],
        )
        agent = PlannerAgent(
            goal_analyzer=DeterministicGoalAnalyzer(),
            context_analyzer=DeterministicContextAnalyzer(),
            strategy_selector=DeterministicStrategySelector(),
            capability_matcher=DeterministicCapabilityMatcher(),
            task_decomposer=DeterministicTaskDecomposer(),
            plan_generator=DeterministicPlanGenerator(),
            plan_validator=failing_validator,
            confidence_calculator=DeterministicConfidenceCalculator(),
            plan_optimizer=DeterministicPlanOptimizer(),
            execution_dispatcher=DeterministicExecutionDispatcher(),
            replanner=DeterministicReplanner(),
        )
        result = await agent.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.FAILED
        assert result.metrics.planning_duration_ms >= 0


# ── Policy integration ───────────────────────────────


class TestPlannerAgentPolicy:
    async def test_optimization_enabled_by_default(
        self, sample_request: PlanningRequest
    ) -> None:
        agent = PlannerAgent(
            goal_analyzer=DeterministicGoalAnalyzer(),
            context_analyzer=DeterministicContextAnalyzer(),
            strategy_selector=DeterministicStrategySelector(),
            capability_matcher=DeterministicCapabilityMatcher(),
            task_decomposer=DeterministicTaskDecomposer(),
            plan_generator=DeterministicPlanGenerator(),
            plan_validator=DeterministicPlanValidator(),
            confidence_calculator=DeterministicConfidenceCalculator(),
            plan_optimizer=DeterministicPlanOptimizer(),
            execution_dispatcher=DeterministicExecutionDispatcher(),
            replanner=DeterministicReplanner(),
        )
        assert agent._policy.optimization_enabled is True
        result = await agent.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.COMPLETED

    async def test_optimization_disabled(
        self, sample_request: PlanningRequest
    ) -> None:
        agent = PlannerAgent(
            goal_analyzer=DeterministicGoalAnalyzer(),
            context_analyzer=DeterministicContextAnalyzer(),
            strategy_selector=DeterministicStrategySelector(),
            capability_matcher=DeterministicCapabilityMatcher(),
            task_decomposer=DeterministicTaskDecomposer(),
            plan_generator=DeterministicPlanGenerator(),
            plan_validator=DeterministicPlanValidator(),
            confidence_calculator=DeterministicConfidenceCalculator(),
            plan_optimizer=DeterministicPlanOptimizer(),
            execution_dispatcher=DeterministicExecutionDispatcher(),
            replanner=DeterministicReplanner(),
            policy=PlanningPolicy(optimization_enabled=False),
        )
        result = await agent.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.COMPLETED
        # Should have a trace for optimizer even when disabled
        assert any(t.stage_name == "plan_optimizer" for t in result.traces)

    async def test_decision_reflects_threshold(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.final_decision is not None
        assert "70.0" in result.final_decision.reasoning  # default auto_execute_threshold


# ── Enhanced traces ─────────────────────────────────


class TestPlannerAgentEnhancedTraces:
    async def test_traces_have_duration(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        for trace in result.traces:
            assert trace.duration_ms is not None
            assert trace.duration_ms >= 0

    async def test_traces_have_planner_version(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        for trace in result.traces:
            assert trace.planner_version == "0.1.0"

    async def test_traces_have_correlation_id(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        for trace in result.traces:
            assert trace.correlation_id != ""

    async def test_metrics_include_new_fields(
        self, planner_agent: PlannerAgent, sample_request: PlanningRequest
    ) -> None:
        result = await planner_agent.create_plan(sample_request)
        assert result.metrics.total_planning_time >= 0
        assert result.metrics.decisions_made >= 1
