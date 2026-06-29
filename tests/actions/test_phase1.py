"""Phase 1 tests for the Action Manager (Architecture, Contracts & Models).

Tests all Phase 1 components: enums, models, DTOs, events, exceptions,
interfaces, and their relationships. Validates that all contracts are
correctly defined and behave as expected.
"""

from __future__ import annotations

import uuid
from abc import ABC
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.actions.contracts.events import (
    ActionEvent,
    ActionPlanned,
    ActionReady,
    ActionRequested,
    ActionValidated,
)
from adip.actions.contracts.exceptions import (
    ActionException,
    DependencyException,
    PlanningException,
    ScheduleException,
)
from adip.actions.contracts.models import (
    ActionContext,
    ActionDecision,
    ActionDependency,
    ActionHealth,
    ActionMetadata,
    ActionMetrics,
    ActionPlan,
    ActionPlanStep,
    ActionPostcondition,
    ActionPrecondition,
    ActionRequest,
    ActionSchedule,
    ActionSession,
    ResourceAllocation,
    RollbackPlan,
)
from adip.actions.dtos import ActionPlanDTO, ActionRequestDTO, ActionResponseDTO
from adip.actions.enums import ActionPriority, ActionType, ExecutionReadiness
from adip.actions.interfaces import (
    ActionCoordinator,
    ActionManager,
    ActionPlanner,
    ActionService,
    DependencyResolver,
    ReadinessValidator,
    ResourceAllocator,
    RollbackPlanner,
    SchedulePlanner,
)

# ═══════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════


class TestActionType:
    def test_values(self) -> None:
        assert ActionType.MANUAL.value == "MANUAL"
        assert ActionType.AUTOMATED.value == "AUTOMATED"
        assert ActionType.APPROVAL.value == "APPROVAL"
        assert ActionType.NOTIFICATION.value == "NOTIFICATION"
        assert ActionType.WORKFLOW.value == "WORKFLOW"
        assert ActionType.EXTERNAL_INTEGRATION.value == "EXTERNAL_INTEGRATION"
        assert ActionType.EMERGENCY.value == "EMERGENCY"

    def test_unique_values(self) -> None:
        values = [e.value for e in ActionType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ActionType) == 7


class TestActionPriority:
    def test_values(self) -> None:
        assert ActionPriority.CRITICAL.value == "CRITICAL"
        assert ActionPriority.HIGH.value == "HIGH"
        assert ActionPriority.MEDIUM.value == "MEDIUM"
        assert ActionPriority.LOW.value == "LOW"

    def test_unique_values(self) -> None:
        values = [e.value for e in ActionPriority]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ActionPriority) == 4


class TestExecutionReadiness:
    def test_values(self) -> None:
        assert ExecutionReadiness.READY.value == "READY"
        assert ExecutionReadiness.BLOCKED.value == "BLOCKED"
        assert ExecutionReadiness.WAITING.value == "WAITING"
        assert ExecutionReadiness.SCHEDULED.value == "SCHEDULED"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExecutionReadiness]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ExecutionReadiness) == 4


# ═══════════════════════════════════════════════════════════════════════
# ActionRequest
# ═══════════════════════════════════════════════════════════════════════


class TestActionRequest:
    def test_default_request(self) -> None:
        rev_id = uuid.uuid4()
        req = ActionRequest(review_decision_id=rev_id)
        assert req.request_id is not None
        assert req.review_decision_id == rev_id
        assert req.action_type == ActionType.AUTOMATED
        assert req.priority == ActionPriority.MEDIUM
        assert req.domain == ""
        assert req.target == ""
        assert req.metadata == {}

    def test_request_with_values(self) -> None:
        rev_id = uuid.uuid4()
        req = ActionRequest(
            review_decision_id=rev_id,
            action_type=ActionType.MANUAL,
            priority=ActionPriority.HIGH,
            domain="ENERGY",
            target="turbine-01",
            metadata={"source": "test"},
        )
        assert req.action_type == ActionType.MANUAL
        assert req.priority == ActionPriority.HIGH
        assert req.domain == "ENERGY"
        assert req.target == "turbine-01"
        assert req.metadata["source"] == "test"

    def test_request_requires_review_decision_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionRequest()

    def test_request_unique_ids(self) -> None:
        rev_id = uuid.uuid4()
        r1 = ActionRequest(review_decision_id=rev_id)
        r2 = ActionRequest(review_decision_id=rev_id)
        assert r1.request_id != r2.request_id


# ═══════════════════════════════════════════════════════════════════════
# ActionPlan
# ═══════════════════════════════════════════════════════════════════════


class TestActionPlan:
    def test_default_plan(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        p = ActionPlan(request_id=req_id, review_decision_id=rev_id)
        assert p.plan_id is not None
        assert p.request_id == req_id
        assert p.review_decision_id == rev_id
        assert p.name == ""
        assert p.description == ""
        assert p.steps == []
        assert p.rollback_plan is None
        assert p.dependencies == []
        assert p.resource_allocation is None
        assert p.schedule is None
        assert p.is_primary is True
        assert p.status == "DRAFT"

    def test_plan_with_values(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        p = ActionPlan(
            request_id=req_id,
            review_decision_id=rev_id,
            name="Replace Turbine Blade",
            description="Planned replacement of turbine blade #3",
            is_primary=True,
            status="PLANNED",
        )
        assert p.name == "Replace Turbine Blade"
        assert p.is_primary is True
        assert p.status == "PLANNED"

    def test_plan_requires_request_id(self) -> None:
        rev_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlan(review_decision_id=rev_id)

    def test_plan_requires_review_decision_id(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlan(request_id=req_id)

    def test_plan_unique_ids(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        p1 = ActionPlan(request_id=req_id, review_decision_id=rev_id)
        p2 = ActionPlan(request_id=req_id, review_decision_id=rev_id)
        assert p1.plan_id != p2.plan_id


# ═══════════════════════════════════════════════════════════════════════
# ActionPlanStep
# ═══════════════════════════════════════════════════════════════════════


class TestActionPlanStep:
    def test_default_step(self) -> None:
        plan_id = uuid.uuid4()
        s = ActionPlanStep(plan_id=plan_id, action_type=ActionType.AUTOMATED)
        assert s.step_id is not None
        assert s.plan_id == plan_id
        assert s.action_type == ActionType.AUTOMATED
        assert s.name == ""
        assert s.description == ""
        assert s.priority == ActionPriority.MEDIUM
        assert s.order == 0
        assert s.parameters == {}
        assert s.dependencies == []
        assert s.preconditions == []
        assert s.postconditions == []
        assert s.rollback_step_id is None
        assert s.timeout_seconds == 300
        assert s.retry_count == 0

    def test_step_with_values(self) -> None:
        plan_id = uuid.uuid4()
        s = ActionPlanStep(
            plan_id=plan_id,
            action_type=ActionType.MANUAL,
            name="Inspect blade",
            description="Visual inspection of turbine blade",
            priority=ActionPriority.HIGH,
            order=1,
            parameters={"location": "north-face"},
            timeout_seconds=600,
            retry_count=2,
        )
        assert s.name == "Inspect blade"
        assert s.priority == ActionPriority.HIGH
        assert s.order == 1
        assert s.timeout_seconds == 600
        assert s.retry_count == 2

    def test_step_requires_plan_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionPlanStep(action_type=ActionType.AUTOMATED)

    def test_step_requires_action_type(self) -> None:
        plan_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlanStep(plan_id=plan_id)

    def test_step_unique_ids(self) -> None:
        plan_id = uuid.uuid4()
        s1 = ActionPlanStep(plan_id=plan_id, action_type=ActionType.AUTOMATED)
        s2 = ActionPlanStep(plan_id=plan_id, action_type=ActionType.AUTOMATED)
        assert s1.step_id != s2.step_id

    def test_step_timeout_non_negative(self) -> None:
        plan_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlanStep(plan_id=plan_id, action_type=ActionType.AUTOMATED, timeout_seconds=-1)

    def test_step_order_non_negative(self) -> None:
        plan_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlanStep(plan_id=plan_id, action_type=ActionType.AUTOMATED, order=-1)


# ═══════════════════════════════════════════════════════════════════════
# ActionDecision
# ═══════════════════════════════════════════════════════════════════════


class TestActionDecision:
    def test_default_decision(self) -> None:
        req_id = uuid.uuid4()
        d = ActionDecision(request_id=req_id)
        assert d.decision_id is not None
        assert d.request_id == req_id
        assert d.plan is None
        assert d.readiness == ExecutionReadiness.WAITING
        assert d.readiness_reason == ""
        assert d.is_ready is False
        assert d.issues == []
        assert d.warnings == []

    def test_decision_with_values(self) -> None:
        req_id = uuid.uuid4()
        d = ActionDecision(
            request_id=req_id,
            readiness=ExecutionReadiness.READY,
            readiness_reason="All dependencies satisfied",
            is_ready=True,
            issues=["Minor warning"],
            warnings=["Schedule tight"],
        )
        assert d.readiness == ExecutionReadiness.READY
        assert d.is_ready is True
        assert len(d.issues) == 1
        assert len(d.warnings) == 1

    def test_decision_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionDecision()

    def test_decision_unique_ids(self) -> None:
        req_id = uuid.uuid4()
        d1 = ActionDecision(request_id=req_id)
        d2 = ActionDecision(request_id=req_id)
        assert d1.decision_id != d2.decision_id


# ═══════════════════════════════════════════════════════════════════════
# ActionSession
# ═══════════════════════════════════════════════════════════════════════


class TestActionSession:
    def test_default_session(self) -> None:
        req_id = uuid.uuid4()
        s = ActionSession(request_id=req_id)
        assert s.session_id is not None
        assert s.request_id == req_id
        assert s.plan_id is None
        assert s.status == "INITIALIZED"
        assert s.completed_at is None
        assert s.action_type == ActionType.AUTOMATED
        assert s.priority == ActionPriority.MEDIUM
        assert s.statistics == {}

    def test_session_with_values(self) -> None:
        req_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        s = ActionSession(
            request_id=req_id,
            plan_id=plan_id,
            status="PLANNING",
            action_type=ActionType.MANUAL,
            priority=ActionPriority.HIGH,
            statistics={"duration_ms": 150},
        )
        assert s.plan_id == plan_id
        assert s.status == "PLANNING"
        assert s.action_type == ActionType.MANUAL
        assert s.priority == ActionPriority.HIGH
        assert s.statistics["duration_ms"] == 150

    def test_session_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionSession()


# ═══════════════════════════════════════════════════════════════════════
# ActionContext
# ═══════════════════════════════════════════════════════════════════════


class TestActionContext:
    def test_default_context(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        c = ActionContext(request_id=req_id, review_decision_id=rev_id)
        assert c.context_id is not None
        assert c.request_id == req_id
        assert c.review_decision_id == rev_id
        assert c.asset_id == ""
        assert c.machine_id == ""
        assert c.facility_id == ""
        assert c.workflow_id == ""
        assert c.domain == ""

    def test_context_with_values(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        c = ActionContext(
            request_id=req_id,
            review_decision_id=rev_id,
            asset_id="asset-1",
            machine_id="machine-1",
            facility_id="facility-1",
            workflow_id="workflow-1",
            domain="ENERGY",
        )
        assert c.asset_id == "asset-1"
        assert c.machine_id == "machine-1"
        assert c.facility_id == "facility-1"
        assert c.workflow_id == "workflow-1"
        assert c.domain == "ENERGY"

    def test_context_requires_request_id(self) -> None:
        rev_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionContext(review_decision_id=rev_id)

    def test_context_requires_review_decision_id(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionContext(request_id=req_id)

    def test_context_unique_ids(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        c1 = ActionContext(request_id=req_id, review_decision_id=rev_id)
        c2 = ActionContext(request_id=req_id, review_decision_id=rev_id)
        assert c1.context_id != c2.context_id


# ═══════════════════════════════════════════════════════════════════════
# ActionDependency
# ═══════════════════════════════════════════════════════════════════════


class TestActionDependency:
    def test_default_dependency(self) -> None:
        plan_id = uuid.uuid4()
        d = ActionDependency(plan_id=plan_id)
        assert d.dependency_id is not None
        assert d.plan_id == plan_id
        assert d.name == ""
        assert d.description == ""
        assert d.dependency_type == ""
        assert d.required is True
        assert d.satisfied is False

    def test_dependency_with_values(self) -> None:
        plan_id = uuid.uuid4()
        d = ActionDependency(
            plan_id=plan_id,
            name="Parts Available",
            description="Replacement parts must be in inventory",
            dependency_type="resource",
            required=True,
            satisfied=True,
        )
        assert d.name == "Parts Available"
        assert d.dependency_type == "resource"
        assert d.satisfied is True

    def test_dependency_requires_plan_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionDependency()

    def test_dependency_unique_ids(self) -> None:
        plan_id = uuid.uuid4()
        d1 = ActionDependency(plan_id=plan_id)
        d2 = ActionDependency(plan_id=plan_id)
        assert d1.dependency_id != d2.dependency_id


# ═══════════════════════════════════════════════════════════════════════
# ActionPrecondition
# ═══════════════════════════════════════════════════════════════════════


class TestActionPrecondition:
    def test_default_precondition(self) -> None:
        step_id = uuid.uuid4()
        p = ActionPrecondition(step_id=step_id)
        assert p.precondition_id is not None
        assert p.step_id == step_id
        assert p.name == ""
        assert p.description == ""
        assert p.condition == ""
        assert p.met is False

    def test_precondition_with_values(self) -> None:
        step_id = uuid.uuid4()
        p = ActionPrecondition(
            step_id=step_id,
            name="Machine Offline",
            description="Machine must be in offline state",
            condition="machine.status == 'OFFLINE'",
            met=True,
        )
        assert p.name == "Machine Offline"
        assert p.condition == "machine.status == 'OFFLINE'"
        assert p.met is True

    def test_precondition_requires_step_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionPrecondition()

    def test_precondition_unique_ids(self) -> None:
        step_id = uuid.uuid4()
        p1 = ActionPrecondition(step_id=step_id)
        p2 = ActionPrecondition(step_id=step_id)
        assert p1.precondition_id != p2.precondition_id


# ═══════════════════════════════════════════════════════════════════════
# ActionPostcondition
# ═══════════════════════════════════════════════════════════════════════


class TestActionPostcondition:
    def test_default_postcondition(self) -> None:
        step_id = uuid.uuid4()
        p = ActionPostcondition(step_id=step_id)
        assert p.postcondition_id is not None
        assert p.step_id == step_id
        assert p.name == ""
        assert p.description == ""
        assert p.condition == ""
        assert p.verified is False

    def test_postcondition_with_values(self) -> None:
        step_id = uuid.uuid4()
        p = ActionPostcondition(
            step_id=step_id,
            name="Blade Replaced",
            description="New blade must be installed and secured",
            condition="blade.status == 'INSTALLED'",
            verified=True,
        )
        assert p.name == "Blade Replaced"
        assert p.condition == "blade.status == 'INSTALLED'"
        assert p.verified is True

    def test_postcondition_requires_step_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionPostcondition()

    def test_postcondition_unique_ids(self) -> None:
        step_id = uuid.uuid4()
        p1 = ActionPostcondition(step_id=step_id)
        p2 = ActionPostcondition(step_id=step_id)
        assert p1.postcondition_id != p2.postcondition_id


# ═══════════════════════════════════════════════════════════════════════
# RollbackPlan
# ═══════════════════════════════════════════════════════════════════════


class TestRollbackPlan:
    def test_default_rollback(self) -> None:
        plan_id = uuid.uuid4()
        r = RollbackPlan(plan_id=plan_id)
        assert r.rollback_id is not None
        assert r.plan_id == plan_id
        assert r.name == ""
        assert r.description == ""
        assert r.steps == []
        assert r.dependencies == []
        assert r.resource_allocation is None
        assert r.schedule is None
        assert r.auto_rollback is True

    def test_rollback_with_values(self) -> None:
        plan_id = uuid.uuid4()
        r = RollbackPlan(
            plan_id=plan_id,
            name="Rollback replacement",
            description="Revert to original blade",
            auto_rollback=False,
        )
        assert r.name == "Rollback replacement"
        assert r.auto_rollback is False

    def test_rollback_requires_plan_id(self) -> None:
        with pytest.raises(ValidationError):
            RollbackPlan()

    def test_rollback_unique_ids(self) -> None:
        plan_id = uuid.uuid4()
        r1 = RollbackPlan(plan_id=plan_id)
        r2 = RollbackPlan(plan_id=plan_id)
        assert r1.rollback_id != r2.rollback_id


# ═══════════════════════════════════════════════════════════════════════
# ResourceAllocation
# ═══════════════════════════════════════════════════════════════════════


class TestResourceAllocation:
    def test_default_allocation(self) -> None:
        plan_id = uuid.uuid4()
        a = ResourceAllocation(plan_id=plan_id)
        assert a.allocation_id is not None
        assert a.plan_id == plan_id
        assert a.personnel == []
        assert a.equipment == []
        assert a.materials == []
        assert a.estimated_duration_minutes == 0
        assert a.cost_estimate == 0.0

    def test_allocation_with_values(self) -> None:
        plan_id = uuid.uuid4()
        a = ResourceAllocation(
            plan_id=plan_id,
            personnel=["engineer-1", "technician-2"],
            equipment=["crane-01", "toolkit-03"],
            materials=["blade-part-xyz"],
            estimated_duration_minutes=120,
            cost_estimate=5000.0,
        )
        assert len(a.personnel) == 2
        assert len(a.equipment) == 2
        assert len(a.materials) == 1
        assert a.estimated_duration_minutes == 120
        assert a.cost_estimate == 5000.0

    def test_allocation_requires_plan_id(self) -> None:
        with pytest.raises(ValidationError):
            ResourceAllocation()

    def test_allocation_unique_ids(self) -> None:
        plan_id = uuid.uuid4()
        a1 = ResourceAllocation(plan_id=plan_id)
        a2 = ResourceAllocation(plan_id=plan_id)
        assert a1.allocation_id != a2.allocation_id

    def test_allocation_non_negative_duration(self) -> None:
        plan_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ResourceAllocation(plan_id=plan_id, estimated_duration_minutes=-1)

    def test_allocation_non_negative_cost(self) -> None:
        plan_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ResourceAllocation(plan_id=plan_id, cost_estimate=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# ActionSchedule
# ═══════════════════════════════════════════════════════════════════════


class TestActionSchedule:
    def test_default_schedule(self) -> None:
        plan_id = uuid.uuid4()
        s = ActionSchedule(plan_id=plan_id)
        assert s.schedule_id is not None
        assert s.plan_id == plan_id
        assert s.scheduled_start is None
        assert s.scheduled_end is None
        assert s.deadline is None
        assert s.max_duration_minutes == 0
        assert s.schedule_window == ""

    def test_schedule_with_values(self) -> None:
        plan_id = uuid.uuid4()
        now = datetime.now(UTC)
        s = ActionSchedule(
            plan_id=plan_id,
            scheduled_start=now,
            scheduled_end=now,
            deadline=now,
            max_duration_minutes=240,
            schedule_window="off-hours",
        )
        assert s.scheduled_start == now
        assert s.scheduled_end == now
        assert s.deadline == now
        assert s.max_duration_minutes == 240
        assert s.schedule_window == "off-hours"

    def test_schedule_requires_plan_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionSchedule()

    def test_schedule_unique_ids(self) -> None:
        plan_id = uuid.uuid4()
        s1 = ActionSchedule(plan_id=plan_id)
        s2 = ActionSchedule(plan_id=plan_id)
        assert s1.schedule_id != s2.schedule_id

    def test_schedule_max_duration_non_negative(self) -> None:
        plan_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionSchedule(plan_id=plan_id, max_duration_minutes=-1)


# ═══════════════════════════════════════════════════════════════════════
# ActionMetadata
# ═══════════════════════════════════════════════════════════════════════


class TestActionMetadata:
    def test_default_metadata(self) -> None:
        m = ActionMetadata()
        assert m.title == ""
        assert m.tags == []
        assert m.version == "1.0.0"
        assert m.category == ""
        assert m.source == ""

    def test_metadata_with_values(self) -> None:
        m = ActionMetadata(
            title="Replace Turbine Blade",
            description="Planned maintenance action",
            tags=["maintenance", "turbine"],
            category="maintenance",
            source="review-decision",
        )
        assert m.title == "Replace Turbine Blade"
        assert len(m.tags) == 2
        assert m.source == "review-decision"


# ═══════════════════════════════════════════════════════════════════════
# ActionHealth
# ═══════════════════════════════════════════════════════════════════════


class TestActionHealth:
    def test_default_health(self) -> None:
        h = ActionHealth()
        assert h.overall_status == ""
        assert h.plan_count == 0
        assert h.error_count == 0
        assert h.average_planning_time_ms == 0.0
        assert h.service_status == ""
        assert h.manager_status == ""

    def test_health_with_values(self) -> None:
        h = ActionHealth(
            overall_status="HEALTHY",
            service_status="HEALTHY",
            coordinator_status="HEALTHY",
            planner_status="DEGRADED",
            plan_count=10,
            error_count=2,
            average_planning_time_ms=150.5,
        )
        assert h.overall_status == "HEALTHY"
        assert h.planner_status == "DEGRADED"
        assert h.plan_count == 10
        assert h.average_planning_time_ms == 150.5

    def test_health_counts_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ActionHealth(error_count=-1)
        with pytest.raises(ValidationError):
            ActionHealth(plan_count=-1)
        with pytest.raises(ValidationError):
            ActionHealth(average_planning_time_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# ActionMetrics
# ═══════════════════════════════════════════════════════════════════════


class TestActionMetrics:
    def test_default_metrics(self) -> None:
        m = ActionMetrics()
        assert m.plans_total == 0
        assert m.plans_ready == 0
        assert m.plans_blocked == 0
        assert m.plans_waiting == 0
        assert m.plans_scheduled == 0
        assert m.plans_with_rollback == 0
        assert m.average_steps_per_plan == 0.0
        assert m.average_planning_time_ms == 0.0

    def test_metrics_with_values(self) -> None:
        m = ActionMetrics(
            plans_total=100,
            plans_ready=60,
            plans_blocked=10,
            plans_waiting=20,
            plans_scheduled=10,
            plans_with_rollback=80,
            average_steps_per_plan=5.5,
            average_planning_time_ms=250.0,
            plans_per_action_type={"AUTOMATED": 50},
            plans_per_priority={"HIGH": 40},
            plans_per_domain={"ENERGY": 60},
        )
        assert m.plans_total == 100
        assert m.plans_ready == 60
        assert m.plans_with_rollback == 80
        assert m.average_steps_per_plan == 5.5
        assert m.plans_per_action_type["AUTOMATED"] == 50
        assert m.plans_per_priority["HIGH"] == 40

    def test_metrics_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ActionMetrics(plans_total=-1)
        with pytest.raises(ValidationError):
            ActionMetrics(plans_ready=-1)
        with pytest.raises(ValidationError):
            ActionMetrics(plans_blocked=-1)
        with pytest.raises(ValidationError):
            ActionMetrics(plans_waiting=-1)
        with pytest.raises(ValidationError):
            ActionMetrics(plans_scheduled=-1)
        with pytest.raises(ValidationError):
            ActionMetrics(plans_with_rollback=-1)
        with pytest.raises(ValidationError):
            ActionMetrics(average_steps_per_plan=-1.0)
        with pytest.raises(ValidationError):
            ActionMetrics(average_planning_time_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════


class TestActionRequestDTO:
    def test_default_request_dto(self) -> None:
        rev_id = uuid.uuid4()
        dto = ActionRequestDTO(review_decision_id=rev_id)
        assert dto.request_id is not None
        assert dto.review_decision_id == rev_id
        assert dto.action_type == ActionType.AUTOMATED
        assert dto.priority == ActionPriority.MEDIUM
        assert dto.domain == ""
        assert dto.target == ""
        assert dto.metadata == {}

    def test_request_dto_with_values(self) -> None:
        rev_id = uuid.uuid4()
        dto = ActionRequestDTO(
            review_decision_id=rev_id,
            action_type=ActionType.MANUAL,
            priority=ActionPriority.HIGH,
            domain="ENERGY",
            target="turbine-01",
            metadata={"source": "test"},
        )
        assert dto.action_type == ActionType.MANUAL
        assert dto.priority == ActionPriority.HIGH
        assert dto.domain == "ENERGY"
        assert dto.target == "turbine-01"
        assert dto.metadata["source"] == "test"

    def test_request_dto_requires_review_decision_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionRequestDTO()


class TestActionPlanDTO:
    def test_default_plan_dto(self) -> None:
        req_id = uuid.uuid4()
        dto = ActionPlanDTO(request_id=req_id)
        assert dto.plan_id is not None
        assert dto.request_id == req_id
        assert dto.name == ""
        assert dto.step_count == 0
        assert dto.has_rollback is False
        assert dto.status == "DRAFT"
        assert dto.readiness == ExecutionReadiness.WAITING

    def test_plan_dto_with_values(self) -> None:
        req_id = uuid.uuid4()
        dto = ActionPlanDTO(
            request_id=req_id,
            name="Replace Blade",
            step_count=3,
            has_rollback=True,
            status="READY",
            readiness=ExecutionReadiness.READY,
        )
        assert dto.name == "Replace Blade"
        assert dto.step_count == 3
        assert dto.has_rollback is True
        assert dto.status == "READY"
        assert dto.readiness == ExecutionReadiness.READY

    def test_plan_dto_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ActionPlanDTO()

    def test_plan_dto_step_count_non_negative(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlanDTO(request_id=req_id, step_count=-1)


class TestActionResponseDTO:
    def test_default_response_dto(self) -> None:
        req_id = uuid.uuid4()
        sess_id = uuid.uuid4()
        dto = ActionResponseDTO(request_id=req_id, session_id=sess_id)
        assert dto.response_id is not None
        assert dto.request_id == req_id
        assert dto.session_id == sess_id
        assert dto.decision is None
        assert dto.status == "INITIALIZED"
        assert dto.message == ""

    def test_response_dto_with_values(self) -> None:
        req_id = uuid.uuid4()
        sess_id = uuid.uuid4()
        dto = ActionResponseDTO(
            request_id=req_id,
            session_id=sess_id,
            status="PLANNED",
            message="Action plan generated successfully",
        )
        assert dto.status == "PLANNED"
        assert dto.message == "Action plan generated successfully"

    def test_response_dto_requires_request_id(self) -> None:
        sess_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionResponseDTO(session_id=sess_id)

    def test_response_dto_requires_session_id(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionResponseDTO(request_id=req_id)


# ═══════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════


class TestActionEvent:
    def test_base_event(self) -> None:
        e = ActionEvent()
        assert e.event_id is not None
        assert e.timestamp is not None
        assert e.correlation_id == ""

    def test_action_requested(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        e = ActionRequested(
            request_id=req_id,
            review_decision_id=rev_id,
            action_type=ActionType.MANUAL,
        )
        assert e.request_id == req_id
        assert e.review_decision_id == rev_id
        assert e.action_type == ActionType.MANUAL
        assert isinstance(e, ActionEvent)

    def test_action_planned(self) -> None:
        plan_id = uuid.uuid4()
        req_id = uuid.uuid4()
        e = ActionPlanned(
            plan_id=plan_id,
            request_id=req_id,
            step_count=3,
            has_rollback=True,
        )
        assert e.plan_id == plan_id
        assert e.request_id == req_id
        assert e.step_count == 3
        assert e.has_rollback is True
        assert isinstance(e, ActionEvent)

    def test_action_validated(self) -> None:
        plan_id = uuid.uuid4()
        e = ActionValidated(
            plan_id=plan_id,
            is_valid=True,
            issues=[],
        )
        assert e.plan_id == plan_id
        assert e.is_valid is True
        assert e.issues == []
        assert isinstance(e, ActionEvent)

    def test_action_ready(self) -> None:
        plan_id = uuid.uuid4()
        e = ActionReady(
            plan_id=plan_id,
            readiness=ExecutionReadiness.READY,
            reason="All checks passed",
        )
        assert e.plan_id == plan_id
        assert e.readiness == ExecutionReadiness.READY
        assert e.reason == "All checks passed"
        assert isinstance(e, ActionEvent)

    def test_event_inheritance(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        e = ActionRequested(request_id=req_id, review_decision_id=rev_id)
        assert isinstance(e, ActionEvent)
        assert e.timestamp is not None

    def test_event_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            ActionRequested()

    def test_planned_step_count_non_negative(self) -> None:
        plan_id = uuid.uuid4()
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ActionPlanned(plan_id=plan_id, request_id=req_id, step_count=-1)


# ═══════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════


class TestActionException:
    def test_base_exception(self) -> None:
        e = ActionException("action error")
        assert str(e) == "action error"
        assert isinstance(e, Exception)

    def test_planning_exception(self) -> None:
        e = PlanningException("planning error")
        assert str(e) == "planning error"
        assert isinstance(e, ActionException)

    def test_dependency_exception(self) -> None:
        e = DependencyException("dependency error")
        assert str(e) == "dependency error"
        assert isinstance(e, ActionException)

    def test_schedule_exception(self) -> None:
        e = ScheduleException("schedule error")
        assert str(e) == "schedule error"
        assert isinstance(e, ActionException)

    def test_default_messages(self) -> None:
        assert "Action error occurred" in str(ActionException())
        assert "Planning error occurred" in str(PlanningException())
        assert "Dependency error occurred" in str(DependencyException())
        assert "Schedule error occurred" in str(ScheduleException())

    def test_exception_hierarchy(self) -> None:
        assert issubclass(PlanningException, ActionException)
        assert issubclass(DependencyException, ActionException)
        assert issubclass(ScheduleException, ActionException)

    def test_default_code_values(self) -> None:
        assert ActionException().code == "ACTION_ERROR"
        assert PlanningException().code == "PLANNING_ERROR"
        assert DependencyException().code == "DEPENDENCY_ERROR"
        assert ScheduleException().code == "SCHEDULE_ERROR"

    def test_details(self) -> None:
        e = ActionException("error", details={"key": "value"})
        assert e.details["key"] == "value"


# ═══════════════════════════════════════════════════════════════════════
# Interfaces
# ═══════════════════════════════════════════════════════════════════════


class TestInterfaces:
    def test_action_service_is_abstract(self) -> None:
        assert issubclass(ActionService, ABC)

    def test_action_manager_is_abstract(self) -> None:
        assert issubclass(ActionManager, ABC)

    def test_action_coordinator_is_abstract(self) -> None:
        assert issubclass(ActionCoordinator, ABC)

    def test_action_planner_is_abstract(self) -> None:
        assert issubclass(ActionPlanner, ABC)

    def test_dependency_resolver_is_abstract(self) -> None:
        assert issubclass(DependencyResolver, ABC)

    def test_resource_allocator_is_abstract(self) -> None:
        assert issubclass(ResourceAllocator, ABC)

    def test_schedule_planner_is_abstract(self) -> None:
        assert issubclass(SchedulePlanner, ABC)

    def test_rollback_planner_is_abstract(self) -> None:
        assert issubclass(RollbackPlanner, ABC)

    def test_readiness_validator_is_abstract(self) -> None:
        assert issubclass(ReadinessValidator, ABC)

    def test_interface_count(self) -> None:
        interfaces = [
            ActionService,
            ActionManager,
            ActionCoordinator,
            ActionPlanner,
            DependencyResolver,
            ResourceAllocator,
            SchedulePlanner,
            RollbackPlanner,
            ReadinessValidator,
        ]
        assert len(interfaces) == 9

    def test_action_service_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(ActionService)
        assert hasattr(ActionService, "plan_action")
        assert hasattr(ActionService, "get_decision")
        assert hasattr(ActionService, "get_plan")
        assert hasattr(ActionService, "get_session")
        assert hasattr(ActionService, "get_health")
        assert hasattr(ActionService, "get_metrics")

    def test_action_manager_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(ActionManager)
        assert hasattr(ActionManager, "start_planning")
        assert hasattr(ActionManager, "get_decision")
        assert hasattr(ActionManager, "get_plan")
        assert hasattr(ActionManager, "get_session")
        assert hasattr(ActionManager, "get_health")
        assert hasattr(ActionManager, "get_metrics")

    def test_action_coordinator_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(ActionCoordinator)
        assert hasattr(ActionCoordinator, "plan")
        assert hasattr(ActionCoordinator, "get_decision")
        assert hasattr(ActionCoordinator, "get_plan")
        assert hasattr(ActionCoordinator, "health")
        assert hasattr(ActionCoordinator, "metrics")

    def test_action_planner_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(ActionPlanner)
        assert hasattr(ActionPlanner, "generate_plan")
        assert hasattr(ActionPlanner, "validate_plan")

    def test_dependency_resolver_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(DependencyResolver)
        assert hasattr(DependencyResolver, "resolve_dependencies")
        assert hasattr(DependencyResolver, "validate_dependencies")

    def test_resource_allocator_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(ResourceAllocator)
        assert hasattr(ResourceAllocator, "allocate_resources")
        assert hasattr(ResourceAllocator, "validate_resources")

    def test_schedule_planner_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(SchedulePlanner)
        assert hasattr(SchedulePlanner, "create_schedule")
        assert hasattr(SchedulePlanner, "validate_schedule")

    def test_rollback_planner_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(RollbackPlanner)
        assert hasattr(RollbackPlanner, "create_rollback")
        assert hasattr(RollbackPlanner, "validate_rollback")

    def test_readiness_validator_has_abstract_methods(self) -> None:
        from inspect import isabstract
        assert isabstract(ReadinessValidator)
        assert hasattr(ReadinessValidator, "check_readiness")
        assert hasattr(ReadinessValidator, "validate_readiness")


# ═══════════════════════════════════════════════════════════════════════
# Model Relationships
# ═══════════════════════════════════════════════════════════════════════


class TestModelRelationships:
    def test_plan_has_steps(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        step = ActionPlanStep(plan_id=plan_id, action_type=ActionType.AUTOMATED)
        p = ActionPlan(
            request_id=req_id,
            review_decision_id=rev_id,
            steps=[step],
        )
        assert len(p.steps) == 1
        assert p.steps[0].action_type == ActionType.AUTOMATED

    def test_plan_has_dependencies(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        dep = ActionDependency(plan_id=plan_id, name="Inspection Complete")
        p = ActionPlan(
            request_id=req_id,
            review_decision_id=rev_id,
            dependencies=[dep],
        )
        assert len(p.dependencies) == 1
        assert p.dependencies[0].name == "Inspection Complete"

    def test_plan_has_rollback(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        rollback = RollbackPlan(plan_id=plan_id, name="Revert action")
        p = ActionPlan(
            request_id=req_id,
            review_decision_id=rev_id,
            rollback_plan=rollback,
        )
        assert p.rollback_plan is not None
        assert p.rollback_plan.name == "Revert action"

    def test_plan_has_resource_allocation(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        alloc = ResourceAllocation(
            plan_id=plan_id,
            personnel=["engineer-1"],
        )
        p = ActionPlan(
            request_id=req_id,
            review_decision_id=rev_id,
            resource_allocation=alloc,
        )
        assert p.resource_allocation is not None
        assert len(p.resource_allocation.personnel) == 1

    def test_plan_has_schedule(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        sched = ActionSchedule(plan_id=plan_id, schedule_window="off-hours")
        p = ActionPlan(
            request_id=req_id,
            review_decision_id=rev_id,
            schedule=sched,
        )
        assert p.schedule is not None
        assert p.schedule.schedule_window == "off-hours"

    def test_decision_has_plan(self) -> None:
        req_id = uuid.uuid4()
        rev_id = uuid.uuid4()
        plan = ActionPlan(request_id=req_id, review_decision_id=rev_id)
        d = ActionDecision(request_id=req_id, plan=plan)
        assert d.plan is not None
        assert d.plan.plan_id == plan.plan_id

    def test_step_has_preconditions(self) -> None:
        plan_id = uuid.uuid4()
        step_id = uuid.uuid4()
        pre = ActionPrecondition(step_id=step_id, name="Safety Check")
        s = ActionPlanStep(
            plan_id=plan_id,
            action_type=ActionType.AUTOMATED,
            preconditions=[pre],
        )
        assert len(s.preconditions) == 1
        assert s.preconditions[0].name == "Safety Check"

    def test_step_has_postconditions(self) -> None:
        plan_id = uuid.uuid4()
        step_id = uuid.uuid4()
        post = ActionPostcondition(step_id=step_id, name="Verified Complete")
        s = ActionPlanStep(
            plan_id=plan_id,
            action_type=ActionType.AUTOMATED,
            postconditions=[post],
        )
        assert len(s.postconditions) == 1
        assert s.postconditions[0].name == "Verified Complete"

    def test_session_has_plan(self) -> None:
        req_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        s = ActionSession(request_id=req_id, plan_id=plan_id)
        assert s.plan_id == plan_id


# ═══════════════════════════════════════════════════════════════════════
# Module Exports
# ═══════════════════════════════════════════════════════════════════════


class TestModuleExports:
    def test_enums_exported(self) -> None:
        from adip.actions import ActionPriority, ActionType, ExecutionReadiness
        assert ActionType is not None
        assert ActionPriority is not None
        assert ExecutionReadiness is not None

    def test_dtos_exported(self) -> None:
        from adip.actions import ActionPlanDTO, ActionRequestDTO, ActionResponseDTO
        assert ActionRequestDTO is not None
        assert ActionPlanDTO is not None
        assert ActionResponseDTO is not None

    def test_interfaces_exported(self) -> None:
        from adip.actions import (
            ActionCoordinator,
            ActionManager,
            ActionPlanner,
            ActionService,
            DependencyResolver,
            ReadinessValidator,
            ResourceAllocator,
            RollbackPlanner,
            SchedulePlanner,
        )
        assert ActionService is not None
        assert ActionManager is not None
        assert ActionCoordinator is not None
        assert ActionPlanner is not None
        assert DependencyResolver is not None
        assert ResourceAllocator is not None
        assert SchedulePlanner is not None
        assert RollbackPlanner is not None
        assert ReadinessValidator is not None
