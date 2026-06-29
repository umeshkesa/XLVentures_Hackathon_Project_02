"""Validation tests for the Planner Phase 1 contracts and interfaces."""

from __future__ import annotations

import inspect
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from adip.api.planner import PlannerRequestDTO, PlannerResponseDTO
from adip.core.exceptions import PlannerException
from adip.core.planner import (
    CapabilityMatch,
    CapabilityMatcher,
    CapabilityMatchingException,
    ConfidenceLevel,
    ContextAnalyzer,
    ExecutionDispatcher,
    ExecutionPlan,
    GoalAnalyzer,
    PlanGenerator,
    PlannerInterface,
    PlannerStatus,
    PlanningContext,
    PlanningDecision,
    PlanningGoal,
    PlanningMetrics,
    PlanningRequest,
    PlanningResult,
    PlanningStrategy,
    PlanningTask,
    PlanOptimizer,
    PlanValidator,
    Priority,
    Replanner,
    TaskDecomposer,
    TaskStatus,
    ValidationResult,
)


def make_goal(**overrides: object) -> PlanningGoal:
    values: dict[str, object] = {
        "statement": "Find relevant documents",
        "success_criteria": ("Documents are returned",),
        "desired_outputs": {"documents"},
    }
    values.update(overrides)
    return PlanningGoal.model_validate(values)


def make_match(**overrides: object) -> CapabilityMatch:
    values: dict[str, object] = {
        "capability_id": uuid.uuid4(),
        "capability_name": "Document Search",
        "category": "tool",
        "score": 0.9,
        "matched_inputs": {"query"},
        "matched_outputs": {"documents"},
    }
    values.update(overrides)
    return CapabilityMatch.model_validate(values)


def make_task(goal: PlanningGoal, **overrides: object) -> PlanningTask:
    values: dict[str, object] = {
        "goal_id": goal.id,
        "name": "Search documents",
        "capability": make_match(),
        "expected_outputs": {"documents"},
    }
    values.update(overrides)
    return PlanningTask.model_validate(values)


def make_plan(**overrides: object) -> ExecutionPlan:
    goal = overrides.pop("goal", make_goal())
    assert isinstance(goal, PlanningGoal)
    values: dict[str, object] = {
        "request_id": uuid.uuid4(),
        "goal": goal,
        "tasks": (make_task(goal),),
        "strategy": PlanningStrategy.ADAPTIVE,
    }
    values.update(overrides)
    return ExecutionPlan.model_validate(values)


class TestPlanningContext:
    def test_accepts_domain_neutral_json_context(self) -> None:
        context = PlanningContext(
            user_id="user-1",
            available_inputs={"query"},
            variables={"threshold": 0.75, "enabled": True},
        )

        assert context.user_id == "user-1"
        assert context.variables["threshold"] == 0.75

    def test_rejects_unknown_fields_and_blank_identifier(self) -> None:
        with pytest.raises(ValidationError):
            PlanningContext.model_validate({"unknown": "value"})
        with pytest.raises(ValidationError):
            PlanningContext(user_id="   ")


class TestPlanningRequest:
    def test_defaults_are_valid_and_timezone_aware(self) -> None:
        request = PlanningRequest(goal="Analyze this request")

        assert request.priority is Priority.NORMAL
        assert request.strategy is PlanningStrategy.ADAPTIVE
        assert request.requested_at.tzinfo is not None

    def test_rejects_blank_goal_and_invalid_deadline(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            PlanningRequest(goal="   ")
        with pytest.raises(ValidationError, match="after requested_at"):
            PlanningRequest(goal="Goal", requested_at=now, deadline=now - timedelta(seconds=1))
        with pytest.raises(ValidationError, match="timezone-aware"):
            PlanningRequest(goal="Goal", requested_at=datetime.now())


class TestPlanningGoal:
    def test_requires_success_criteria(self) -> None:
        with pytest.raises(ValidationError):
            make_goal(success_criteria=())

    def test_rejects_self_parent(self) -> None:
        goal_id = uuid.uuid4()
        with pytest.raises(ValidationError, match="own parent"):
            make_goal(id=goal_id, parent_goal_id=goal_id)


class TestCapabilityMatch:
    @pytest.mark.parametrize("score", [-0.01, 1.01])
    def test_score_must_be_normalized(self, score: float) -> None:
        with pytest.raises(ValidationError):
            make_match(score=score)

    def test_requires_registry_identity(self) -> None:
        with pytest.raises(ValidationError):
            CapabilityMatch(capability_name="Search", category="tool", score=0.5)


class TestPlanningTask:
    def test_rejects_self_dependency(self) -> None:
        goal = make_goal()
        task_id = uuid.uuid4()
        with pytest.raises(ValidationError, match="depend on itself"):
            make_task(goal, id=task_id, dependencies={task_id})

    def test_validates_runtime_bounds(self) -> None:
        goal = make_goal()
        with pytest.raises(ValidationError):
            make_task(goal, timeout_seconds=0)
        with pytest.raises(ValidationError):
            make_task(goal, retry_limit=-1)


class TestExecutionPlan:
    def test_accepts_dependencies_inside_plan(self) -> None:
        goal = make_goal()
        first = make_task(goal, name="First")
        second = make_task(goal, name="Second", dependencies={first.id})

        plan = make_plan(goal=goal, tasks=(first, second))

        assert plan.tasks == (first, second)

    def test_rejects_duplicate_task_ids(self) -> None:
        goal = make_goal()
        task = make_task(goal)
        with pytest.raises(ValidationError, match="must be unique"):
            make_plan(goal=goal, tasks=(task, task))

    def test_rejects_external_dependency(self) -> None:
        goal = make_goal()
        task = make_task(goal, dependencies={uuid.uuid4()})
        with pytest.raises(ValidationError, match="outside the plan"):
            make_plan(goal=goal, tasks=(task,))

    def test_rejects_task_for_different_goal(self) -> None:
        goal = make_goal()
        task = make_task(make_goal())
        with pytest.raises(ValidationError, match="does not belong"):
            make_plan(goal=goal, tasks=(task,))


class TestPlanningDecision:
    def test_valid_decision_is_auditable(self) -> None:
        decision = PlanningDecision(
            plan_id=uuid.uuid4(),
            decision_type="strategy_selection",
            rationale="Independent work can run concurrently",
            confidence=ConfidenceLevel.HIGH,
        )

        assert decision.created_at.tzinfo is not None

    def test_rejects_blank_rationale_and_naive_timestamp(self) -> None:
        with pytest.raises(ValidationError):
            PlanningDecision(plan_id=uuid.uuid4(), decision_type="choice", rationale="   ")
        with pytest.raises(ValidationError, match="timezone-aware"):
            PlanningDecision(
                plan_id=uuid.uuid4(),
                decision_type="choice",
                rationale="Reason",
                created_at=datetime.now(),
            )


class TestPlanningMetrics:
    def test_defaults_are_zero(self) -> None:
        assert PlanningMetrics().task_count == 0

    def test_rejects_negative_measurements(self) -> None:
        with pytest.raises(ValidationError):
            PlanningMetrics(planning_duration_ms=-0.1)
        with pytest.raises(ValidationError):
            PlanningMetrics(task_count=-1)


class TestValidationResult:
    def test_accepts_consistent_results(self) -> None:
        assert ValidationResult(is_valid=True).is_valid
        assert not ValidationResult(is_valid=False, errors=("Invalid dependency",)).is_valid

    def test_rejects_inconsistent_results(self) -> None:
        with pytest.raises(ValidationError, match="valid result"):
            ValidationResult(is_valid=True, errors=("Unexpected",))
        with pytest.raises(ValidationError, match="at least one error"):
            ValidationResult(is_valid=False)


class TestPlanningResult:
    @pytest.mark.parametrize(
        "status", [PlannerStatus.READY, PlannerStatus.DISPATCHED, PlannerStatus.COMPLETED]
    )
    def test_plan_statuses_require_plan(self, status: PlannerStatus) -> None:
        with pytest.raises(ValidationError, match="requires an execution plan"):
            PlanningResult(request_id=uuid.uuid4(), status=status)

    def test_clarification_and_failure_require_details(self) -> None:
        with pytest.raises(ValidationError, match="requires a question"):
            PlanningResult(request_id=uuid.uuid4(), status=PlannerStatus.NEEDS_CLARIFICATION)
        with pytest.raises(ValidationError, match="requires an error message"):
            PlanningResult(request_id=uuid.uuid4(), status=PlannerStatus.FAILED)

    def test_complete_result_serializes(self) -> None:
        plan = make_plan()
        result = PlanningResult(
            request_id=plan.request_id,
            status=PlannerStatus.COMPLETED,
            plan=plan,
            validation=ValidationResult(is_valid=True),
        )

        assert result.model_dump(mode="json")["status"] == "completed"


class TestPlannerDTOs:
    def test_request_and_response_validate(self) -> None:
        request = PlannerRequestDTO(goal="Create a plan", context={"source": "api"})
        response = PlannerResponseDTO(
            request_id=uuid.uuid4(),
            status=PlannerStatus.PENDING,
        )

        assert request.strategy is PlanningStrategy.ADAPTIVE
        assert response.errors == ()

    def test_request_rejects_blank_goal_and_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            PlannerRequestDTO(goal="   ")
        with pytest.raises(ValidationError):
            PlannerRequestDTO.model_validate({"goal": "Valid", "unexpected": True})


def test_all_pipeline_components_are_abstract_contracts() -> None:
    interfaces = (
        GoalAnalyzer,
        ContextAnalyzer,
        CapabilityMatcher,
        TaskDecomposer,
        PlanGenerator,
        PlanValidator,
        PlanOptimizer,
        Replanner,
        ExecutionDispatcher,
        PlannerInterface,
    )

    assert all(inspect.isabstract(interface) for interface in interfaces)


def test_planner_enums_have_stable_transport_values() -> None:
    assert Priority.CRITICAL.value == "critical"
    assert PlanningStrategy.PARALLEL.value == "parallel"
    assert PlannerStatus.NEEDS_CLARIFICATION.value == "needs_clarification"
    assert TaskStatus.BLOCKED.value == "blocked"
    assert ConfidenceLevel.HIGH.value == 0.85


def test_planner_exceptions_extend_application_exception_hierarchy() -> None:
    error = CapabilityMatchingException("No matching capability")

    assert isinstance(error, PlannerException)
    assert error.code == "planner_capability_matching_error"
