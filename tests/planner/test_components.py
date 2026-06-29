"""Unit tests for Phase 2 planner components (refreshed for Phase 3.5)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from adip.planner.components.capability_matcher import (
    DeterministicCapabilityMatcher,
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
    PlanningTask,
)
from adip.planner.enums import (
    PlanningStrategyEnum,
    PriorityEnum,
    TaskStatusEnum,
)

# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def sample_goal() -> PlanningGoal:
    return PlanningGoal(
        objective="Search the database and compute the average. Then generate a report.",
        priority=PriorityEnum.HIGH,
    )


@pytest.fixture
def sample_context() -> PlanningContext:
    return PlanningContext(
        timestamp=datetime.now(UTC),
        available_capabilities=["data_search", "computation", "analytics"],
    )


@pytest.fixture
def sample_tasks() -> list[PlanningTask]:
    t1 = PlanningTask(
        task_id=uuid.uuid4(),
        description="Task 1",
        dependencies=[],
    )
    t2 = PlanningTask(
        task_id=uuid.uuid4(),
        description="Task 2",
        dependencies=[t1.task_id],
    )
    t3 = PlanningTask(
        task_id=uuid.uuid4(),
        description="Task 3",
        dependencies=[t2.task_id],
    )
    return [t1, t2, t3]


# ── GoalAnalyzer ────────────────────────────────────────────────────────


class TestDeterministicGoalAnalyzer:
    async def test_analyze_returns_enriched_goal(self, sample_goal: PlanningGoal) -> None:
        analyzer = DeterministicGoalAnalyzer()
        goal = await analyzer.analyze(sample_goal)
        assert isinstance(goal, PlanningGoal)
        assert goal.domain == "search"  # derived from "search" (first keyword match)
        assert goal.intent == "information_retrieval"  # derived from "search"

    async def test_analyze_sets_ambiguity_score(self) -> None:
        goal = PlanningGoal(objective="Short")
        analyzer = DeterministicGoalAnalyzer()
        result = await analyzer.analyze(goal)
        assert result.ambiguity_score >= 0.0

    async def test_analyze_preserves_existing_fields(self) -> None:
        goal = PlanningGoal(
            objective="Find data.",
            domain="custom_domain",
            intent="custom_intent",
        )
        analyzer = DeterministicGoalAnalyzer()
        result = await analyzer.analyze(goal)
        assert result.domain == "custom_domain"
        assert result.intent == "custom_intent"
        assert result.ambiguity_score >= 0.0


# ── ContextAnalyzer ─────────────────────────────────────────────────────


class TestDeterministicContextAnalyzer:
    async def test_analyze_enriches_capabilities(
        self, sample_goal: PlanningGoal, sample_context: PlanningContext
    ) -> None:
        analyzer = DeterministicContextAnalyzer()
        enriched = await analyzer.analyze(sample_goal, sample_context)
        assert len(enriched.available_capabilities) >= len(
            sample_context.available_capabilities
        )
        assert "summarization" in enriched.available_capabilities
        assert "translation" in enriched.available_capabilities

    async def test_analyze_does_not_duplicate(
        self, sample_goal: PlanningGoal, sample_context: PlanningContext
    ) -> None:
        analyzer = DeterministicContextAnalyzer()
        first = await analyzer.analyze(sample_goal, sample_context)
        second = await analyzer.analyze(sample_goal, first)
        assert set(first.available_capabilities) == set(second.available_capabilities)


# ── StrategySelector ────────────────────────────────────────────────────


class TestDeterministicStrategySelector:
    async def test_high_priority_selects_greedy(
        self, sample_goal: PlanningGoal, sample_context: PlanningContext
    ) -> None:
        selector = DeterministicStrategySelector()
        strategy = await selector.select(sample_goal, sample_context)
        assert strategy == PlanningStrategyEnum.GREEDY

    async def test_low_priority_selects_pessimistic(
        self, sample_context: PlanningContext
    ) -> None:
        goal = PlanningGoal(objective="Low priority", priority=PriorityEnum.LOW)
        selector = DeterministicStrategySelector()
        strategy = await selector.select(goal, sample_context)
        assert strategy == PlanningStrategyEnum.PESSIMISTIC

    async def test_critical_priority_selects_best_first(
        self, sample_context: PlanningContext
    ) -> None:
        goal = PlanningGoal(objective="Critical", priority=PriorityEnum.CRITICAL)
        selector = DeterministicStrategySelector()
        strategy = await selector.select(goal, sample_context)
        assert strategy == PlanningStrategyEnum.BEST_FIRST


# ── CapabilityMatcher ───────────────────────────────────────────────────


class TestDeterministicCapabilityMatcher:
    async def test_match_search_keywords(
        self, sample_context: PlanningContext
    ) -> None:
        matcher = DeterministicCapabilityMatcher()
        matches = await matcher.match_capabilities(
            "Search for data and find results", sample_context
        )
        assert any(m.capability_id == "data_search" for m in matches)

    async def test_match_scores_are_sorted_descending(
        self, sample_context: PlanningContext
    ) -> None:
        matcher = DeterministicCapabilityMatcher()
        matches = await matcher.match_capabilities(
            "Search, compute, analyze, and summarize the data",
            sample_context,
        )
        scores = [m.score for m in matches]
        assert scores == sorted(scores, reverse=True)

    async def test_no_match_returns_empty_list(self) -> None:
        context = PlanningContext(
            timestamp=datetime.now(UTC),
            available_capabilities=["unknown_cap"],
        )
        matcher = DeterministicCapabilityMatcher()
        matches = await matcher.match_capabilities("Do something", context)
        assert matches == []


# ── TaskDecomposer ──────────────────────────────────────────────────────


class TestDeterministicTaskDecomposer:
    async def test_decompose_creates_tasks(
        self, sample_goal: PlanningGoal, sample_context: PlanningContext
    ) -> None:
        decomposer = DeterministicTaskDecomposer()
        tasks = await decomposer.decompose(sample_goal, sample_context)
        assert len(tasks) >= 1
        assert all(isinstance(t, PlanningTask) for t in tasks)

    async def test_decompose_orders_dependencies(
        self, sample_goal: PlanningGoal, sample_context: PlanningContext
    ) -> None:
        decomposer = DeterministicTaskDecomposer()
        tasks = await decomposer.decompose(sample_goal, sample_context)
        if len(tasks) > 1:
            assert tasks[0].dependencies == []
            assert tasks[1].dependencies == [tasks[0].task_id]

    async def test_decompose_single_sentence_goal(
        self, sample_context: PlanningContext
    ) -> None:
        goal = PlanningGoal(objective="Just do it.")
        decomposer = DeterministicTaskDecomposer()
        tasks = await decomposer.decompose(goal, sample_context)
        assert len(tasks) == 1


# ── PlanGenerator ───────────────────────────────────────────────────────


class TestDeterministicPlanGenerator:
    async def test_generate_creates_execution_plan(
        self,
        sample_tasks: list[PlanningTask],
        sample_context: PlanningContext,
        sample_goal: PlanningGoal,
    ) -> None:
        generator = DeterministicPlanGenerator()
        plan = await generator.generate(sample_tasks, sample_context, sample_goal)
        assert isinstance(plan, ExecutionPlan)
        assert plan.goal.objective == sample_goal.objective
        assert len(plan.tasks) == len(sample_tasks)

    async def test_generate_topological_ordering(
        self,
        sample_tasks: list[PlanningTask],
        sample_context: PlanningContext,
        sample_goal: PlanningGoal,
    ) -> None:
        generator = DeterministicPlanGenerator()
        plan = await generator.generate(sample_tasks, sample_context, sample_goal)
        task_ids = [t.task_id for t in plan.tasks]
        assert task_ids.index(sample_tasks[0].task_id) < task_ids.index(
            sample_tasks[1].task_id
        )


# ── PlanValidator ───────────────────────────────────────────────────────


class TestDeterministicPlanValidator:
    async def test_validate_valid_plan(
        self, sample_tasks: list[PlanningTask]
    ) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=sample_tasks,
        )
        validator = DeterministicPlanValidator()
        result = await validator.validate(
            plan, PlanningContext(timestamp=datetime.now(UTC))
        )
        assert result.is_valid is True
        assert result.errors == []

    async def test_validate_empty_plan(self) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Empty"),
            tasks=[],
        )
        validator = DeterministicPlanValidator()
        result = await validator.validate(
            plan, PlanningContext(timestamp=datetime.now(UTC))
        )
        assert result.is_valid is False
        assert any("at least one task" in e for e in result.errors)

    async def test_validate_missing_dependency(self) -> None:
        missing_id = uuid.uuid4()
        tasks = [
            PlanningTask(
                task_id=uuid.uuid4(),
                description="Task with bad dep",
                dependencies=[missing_id],
            )
        ]
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=tasks,
        )
        validator = DeterministicPlanValidator()
        result = await validator.validate(
            plan, PlanningContext(timestamp=datetime.now(UTC))
        )
        assert result.is_valid is False
        assert any("missing dependency" in e for e in result.errors)

    async def test_validate_empty_description(self) -> None:
        tasks = [
            PlanningTask(task_id=uuid.uuid4(), description="")
        ]
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=tasks,
        )
        validator = DeterministicPlanValidator()
        result = await validator.validate(
            plan, PlanningContext(timestamp=datetime.now(UTC))
        )
        assert result.is_valid is False
        assert any("empty description" in e for e in result.errors)


# ── PlanOptimizer ───────────────────────────────────────────────────────


class TestDeterministicPlanOptimizer:
    async def test_optimize_removes_transitive_deps(
        self, sample_context: PlanningContext, sample_goal: PlanningGoal
    ) -> None:
        t1 = PlanningTask(task_id=uuid.uuid4(), description="A")
        t2 = PlanningTask(
            task_id=uuid.uuid4(), description="B", dependencies=[t1.task_id]
        )
        t3 = PlanningTask(
            task_id=uuid.uuid4(),
            description="C",
            dependencies=[t1.task_id, t2.task_id],
        )
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=[t1, t2, t3],
        )
        optimizer = DeterministicPlanOptimizer()
        optimized = await optimizer.optimize(plan, sample_context, sample_goal)
        t3_opt = next(t for t in optimized.tasks if t.task_id == t3.task_id)
        assert t2.task_id in t3_opt.dependencies
        assert len(optimized.tasks) == 3


# ── Replanner ───────────────────────────────────────────────────────────


class TestDeterministicReplanner:
    async def test_replan_with_pending_tasks(
        self, sample_context: PlanningContext, sample_goal: PlanningGoal
    ) -> None:
        t1 = PlanningTask(task_id=uuid.uuid4(), description="Pending")
        t2 = PlanningTask(
            task_id=uuid.uuid4(),
            description="Completed",
            status=TaskStatusEnum.COMPLETED,
        )
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=[t1, t2],
        )
        replanner = DeterministicReplanner()
        new_plan = await replanner.replan(
            plan, sample_context, "Deviation occurred", sample_goal
        )
        assert new_plan is not None
        assert len(new_plan.tasks) == 1
        assert all(t.status == TaskStatusEnum.PENDING for t in new_plan.tasks)

    async def test_replan_no_pending_tasks_returns_none(
        self, sample_context: PlanningContext, sample_goal: PlanningGoal
    ) -> None:
        t1 = PlanningTask(
            task_id=uuid.uuid4(),
            description="Completed",
            status=TaskStatusEnum.COMPLETED,
        )
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test"),
            tasks=[t1],
        )
        replanner = DeterministicReplanner()
        new_plan = await replanner.replan(
            plan, sample_context, "All done", sample_goal
        )
        assert new_plan is None


# ── ExecutionDispatcher ─────────────────────────────────────────────────


class TestDeterministicExecutionDispatcher:
    async def test_dispatch_pending_task(
        self, sample_context: PlanningContext
    ) -> None:
        task = PlanningTask(task_id=uuid.uuid4(), description="Dispatch me")
        dispatcher = DeterministicExecutionDispatcher()
        dispatched = await dispatcher.dispatch(task, sample_context)
        assert dispatched.status == TaskStatusEnum.IN_PROGRESS
        assert dispatched.task_id == task.task_id

    async def test_dispatch_completed_task_unchanged(
        self, sample_context: PlanningContext
    ) -> None:
        task = PlanningTask(
            task_id=uuid.uuid4(),
            description="Already done",
            status=TaskStatusEnum.COMPLETED,
        )
        dispatcher = DeterministicExecutionDispatcher()
        result = await dispatcher.dispatch(task, sample_context)
        assert result.status == TaskStatusEnum.COMPLETED


# ── Expanded CapabilityMatch ────────────────────────


class TestExpandedCapabilityMatch:
    def test_default_fields(self) -> None:
        from adip.planner.contracts.models import CapabilityMatch
        cm = CapabilityMatch(capability_id="test", score=0.8)
        assert cm.estimated_execution_time is None
        assert cm.estimated_resource_cost is None
        assert cm.estimated_risk is None
        assert cm.required_permissions == []
        assert cm.capability_version == "1.0.0"
        assert cm.provider == ""

    def test_custom_fields(self) -> None:
        from adip.planner.contracts.models import CapabilityMatch
        from adip.planner.enums import ConfidenceLevelEnum
        cm = CapabilityMatch(
            capability_id="exact",
            score=0.95,
            confidence=ConfidenceLevelEnum.VERY_HIGH,
            estimated_execution_time=12.5,
            estimated_resource_cost=100.0,
            estimated_risk=0.1,
            required_permissions=["read", "write"],
            capability_version="2.1.0",
            provider="openai",
        )
        assert cm.estimated_execution_time == 12.5
        assert cm.estimated_resource_cost == 100.0
        assert cm.estimated_risk == 0.1
        assert "read" in cm.required_permissions
        assert cm.capability_version == "2.1.0"
        assert cm.provider == "openai"


# ── DetectedEntity ──────────────────────────────────


class TestDetectedEntity:
    def test_default_creation(self) -> None:
        from adip.planner.contracts.entities import DetectedEntity
        entity = DetectedEntity(name="Transformer T102")
        assert entity.entity_type == "unknown"
        assert entity.confidence == 0.0
        assert entity.source == ""
        assert entity.metadata == {}

    def test_custom_entity(self) -> None:
        from adip.planner.contracts.entities import DetectedEntity
        entity = DetectedEntity(
            name="Plant A",
            entity_type="Facility",
            confidence=0.93,
            source="GoalAnalyzer",
            metadata={"location": "Building 1"},
        )
        assert entity.name == "Plant A"
        assert entity.entity_type == "Facility"
        assert entity.confidence == 0.93
        assert entity.source == "GoalAnalyzer"
        assert entity.metadata["location"] == "Building 1"

    def test_uuid_auto_generated(self) -> None:
        from adip.planner.contracts.entities import DetectedEntity
        e1 = DetectedEntity(name="A")
        e2 = DetectedEntity(name="B")
        assert e1.entity_id != e2.entity_id
