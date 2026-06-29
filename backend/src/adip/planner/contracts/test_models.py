"""Validation tests for planner Pydantic models."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from adip.planner.contracts.models import (
    CapabilityMatch,
    ExecutionPlan,
    PlanningContext,
    PlanningDecision,
    PlanningGoal,
    PlanningMetrics,
    PlanningRequest,
    PlanningResult,
    PlanningTask,
    ValidationResult,
)
from adip.planner.enums import (
    ConfidenceLevelEnum,
    PlanningStatusEnum,
    PlanningStrategyEnum,
    PriorityEnum,
    TaskStatusEnum,
)


def test_planning_request_model() -> None:
    """Test PlanningRequest model creation and validation."""
    context = PlanningContext(timestamp=datetime.now(UTC))
    goal = PlanningGoal(objective="Test objective")
    metrics = PlanningMetrics(execution_time_ms=100.5)

    req = PlanningRequest(context=context, goal=goal, metrics=metrics)

    assert req.context == context
    assert req.goal == goal
    assert req.metrics == metrics

    with pytest.raises(ValueError):  # Missing context
        PlanningRequest(goal=goal, metrics=metrics)

    with pytest.raises(ValueError):  # Missing goal
        PlanningRequest(context=context, metrics=metrics)


def test_planning_context_model() -> None:
    """Test PlanningContext model creation and validation."""
    now = datetime.now(UTC)
    ctx = PlanningContext(timestamp=now, available_capabilities=["cap1", "cap2"])

    assert ctx.timestamp == now
    assert ctx.available_capabilities == ["cap1", "cap2"]

    ctx_default = PlanningContext(timestamp=now)
    assert ctx_default.available_capabilities == []


def test_planning_goal_model() -> None:
    """Test PlanningGoal model creation and validation."""
    goal = PlanningGoal(
        objective="Test objective",
        priority=PriorityEnum.HIGH,
        strategy=PlanningStrategyEnum.GREEDY,
        constraints=["constraint1", "constraint2"],
    )

    assert goal.objective == "Test objective"
    assert goal.priority == PriorityEnum.HIGH
    assert goal.strategy == PlanningStrategyEnum.GREEDY
    assert goal.constraints == ["constraint1", "constraint2"]

    goal_default = PlanningGoal(objective="Default test")
    assert goal_default.priority == PriorityEnum.MEDIUM
    assert goal_default.strategy == PlanningStrategyEnum.DEFAULT
    assert goal_default.constraints == []


def test_capability_match_model() -> None:
    """Test CapabilityMatch model creation and validation."""
    match = CapabilityMatch(
        capability_id="cap1", score=0.95, confidence=ConfidenceLevelEnum.HIGH,
        match_details={"param": "value"}
    )

    assert match.capability_id == "cap1"
    assert match.score == 0.95
    assert match.confidence == ConfidenceLevelEnum.HIGH
    assert match.match_details == {"param": "value"}

    match_default = CapabilityMatch(capability_id="cap2", score=0.7)
    assert match_default.confidence == ConfidenceLevelEnum.MEDIUM
    assert match_default.match_details == {}


def test_planning_task_model() -> None:
    """Test PlanningTask model creation and validation."""
    task_id = uuid.uuid4()
    dep_id = uuid.uuid4()
    task = PlanningTask(
        task_id=task_id,
        description="Test task description",
        dependencies=[dep_id],
        status=TaskStatusEnum.IN_PROGRESS,
        matched_capabilities=[
            CapabilityMatch(capability_id="capA", score=0.8),
            CapabilityMatch(capability_id="capB", score=0.7),
        ],
    )

    assert task.task_id == task_id
    assert task.description == "Test task description"
    assert task.dependencies == [dep_id]
    assert task.status == TaskStatusEnum.IN_PROGRESS
    assert len(task.matched_capabilities) == 2

    task_default = PlanningTask(description="Default task")
    assert task_default.task_id != task_id  # Check default UUID generation
    assert task_default.dependencies == []
    assert task_default.status == TaskStatusEnum.PENDING
    assert task_default.matched_capabilities == []

    with pytest.raises(ValueError):  # Missing description
        PlanningTask(task_id=uuid.uuid4())


def test_execution_plan_model() -> None:
    """Test ExecutionPlan model creation and validation."""
    plan_id = uuid.uuid4()
    task1_id = uuid.uuid4()
    task2_id = uuid.uuid4()
    plan = ExecutionPlan(
        plan_id=plan_id,
        goal_objective="Plan objective",
        tasks=[
            PlanningTask(task_id=task1_id, description="Task 1", dependencies=[]),
            PlanningTask(task_id=task2_id, description="Task 2", dependencies=[task1_id]),
        ],
        created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
    )

    assert plan.plan_id == plan_id
    assert plan.goal_objective == "Plan objective"
    assert len(plan.tasks) == 2
    assert plan.created_at == datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)

    plan_default = ExecutionPlan(goal_objective="Default plan")
    assert plan_default.plan_id != plan_id  # Check default UUID generation
    assert plan_default.tasks == []
    assert plan_default.created_at != datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)


def test_planning_decision_model() -> None:
    """Test PlanningDecision model creation and validation."""
    decision_id = uuid.uuid4()
    task_id = uuid.uuid4()
    decision = PlanningDecision(
        decision_id=decision_id,
        task_id=task_id,
        reasoning="Test reasoning",
        created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
    )

    assert decision.decision_id == decision_id
    assert decision.task_id == task_id
    assert decision.reasoning == "Test reasoning"
    assert decision.created_at == datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)

    decision_no_task = PlanningDecision(decision_id=uuid.uuid4(), reasoning="General reasoning")
    assert decision_no_task.task_id is None
    assert decision_no_task.reasoning == "General reasoning"


def test_planning_metrics_model() -> None:
    """Test PlanningMetrics model creation and validation."""
    metrics = PlanningMetrics(
        execution_time_ms=150.75, tasks_processed=5,
        capabilities_matched=10, decisions_made=2
    )

    assert metrics.execution_time_ms == 150.75
    assert metrics.tasks_processed == 5
    assert metrics.capabilities_matched == 10
    assert metrics.decisions_made == 2

    metrics_default = PlanningMetrics()
    assert metrics_default.execution_time_ms == 0.0
    assert metrics_default.tasks_processed == 0
    assert metrics_default.capabilities_matched == 0
    assert metrics_default.decisions_made == 0


def test_validation_result_model() -> None:
    """Test ValidationResult model creation and validation."""
    result = ValidationResult(
        is_valid=False, errors=["Error 1", "Error 2"], warnings=["Warn 1"]
    )

    assert result.is_valid is False
    assert result.errors == ["Error 1", "Error 2"]
    assert result.warnings == ["Warn 1"]

    result_default = ValidationResult(is_valid=True)
    assert result_default.is_valid is True
    assert result_default.errors == []
    assert result_default.warnings == []


def test_planning_result_model() -> None:
    """Test PlanningResult model creation and validation."""
    request_id = uuid.uuid4()
    plan = ExecutionPlan(goal_objective="Test plan for result")
    decision = PlanningDecision(reasoning="Final decision")
    validation = ValidationResult(is_valid=False, errors=["Plan invalid"])
    metrics = PlanningMetrics(execution_time_ms=200.0)

    result = PlanningResult(
        request_id=request_id,
        plan=plan,
        final_decision=decision,
        validation_status=validation,
        execution_status=PlanningStatusEnum.COMPLETED,
        metrics=metrics,
    )

    assert result.request_id == request_id
    assert result.plan == plan
    assert result.final_decision == decision
    assert result.validation_status == validation
    assert result.execution_status == PlanningStatusEnum.COMPLETED
    assert result.metrics == metrics

    result_default = PlanningResult(request_id=uuid.uuid4())
    assert result_default.plan is None
    assert result_default.final_decision is None
    assert result_default.validation_status.is_valid is True
    assert result_default.execution_status == PlanningStatusEnum.CREATED
    assert result_default.metrics.execution_time_ms == 0.0
