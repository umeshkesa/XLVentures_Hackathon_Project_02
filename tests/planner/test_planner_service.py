"""Tests for the PlannerService facade."""

from __future__ import annotations

from datetime import UTC, datetime

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
)
from adip.planner.contracts.policy import PlanningPolicy
from adip.planner.enums import (
    PlanningStatusEnum,
    PriorityEnum,
)
from adip.planner.services.planner_service import PlannerService


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
def planner_service(planner_agent: PlannerAgent) -> PlannerService:
    return PlannerService(planner=planner_agent)


@pytest.fixture
def sample_request() -> PlanningRequest:
    return PlanningRequest(
        context=PlanningContext(timestamp=datetime.now(UTC)),
        goal=PlanningGoal(
            objective="Search the database and compute the average.",
            priority=PriorityEnum.HIGH,
        ),
    )


class TestPlannerServiceCreation:
    async def test_create_plan_returns_result(
        self, planner_service: PlannerService, sample_request: PlanningRequest
    ) -> None:
        result = await planner_service.create_plan(sample_request)
        assert isinstance(result, PlanningResult)
        assert result.execution_status == PlanningStatusEnum.COMPLETED
        assert result.plan is not None

    async def test_plan_has_metrics(
        self, planner_service: PlannerService, sample_request: PlanningRequest
    ) -> None:
        result = await planner_service.create_plan(sample_request)
        assert result.metrics.total_planning_time >= 0
        assert result.metrics.cpu_time >= 0
        assert result.metrics.memory_usage == 128.0
        assert result.metrics.llm_latency >= 0

    async def test_custom_policy(self, planner_agent: PlannerAgent) -> None:
        policy = PlanningPolicy(
            auto_execute_threshold=90.0,
            optimization_enabled=False,
        )
        service = PlannerService(planner=planner_agent, policy=policy)
        assert service._policy.auto_execute_threshold == 90.0
        assert service._policy.optimization_enabled is False


class TestPlannerServiceValidation:
    async def test_empty_goal_raises(
        self, planner_service: PlannerService
    ) -> None:
        request = PlanningRequest(
            context=PlanningContext(timestamp=datetime.now(UTC)),
            goal=PlanningGoal(objective=""),
        )
        with pytest.raises(ValueError, match="must not be empty"):
            await planner_service.create_plan(request)

    async def test_valid_request_passes(
        self, planner_service: PlannerService, sample_request: PlanningRequest
    ) -> None:
        result = await planner_service.create_plan(sample_request)
        assert result.execution_status == PlanningStatusEnum.COMPLETED


class TestPlannerServiceReplan:
    async def test_replan_delegates(self, planner_service: PlannerService) -> None:
        import uuid
        t1 = PlanningTask(
            task_id=uuid.uuid4(), description="Pending",
        )
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=[t1],
        )
        context = PlanningContext(timestamp=datetime.now(UTC))
        goal = PlanningGoal(objective="Test goal")
        result = await planner_service.replan(plan, context, "deviation", goal)
        assert result is not None
