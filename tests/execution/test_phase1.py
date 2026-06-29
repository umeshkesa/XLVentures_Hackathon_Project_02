"""Phase 1 tests for the Action Engine (Architecture, Contracts & Models).

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

from adip.execution.contracts.events import (
    ExecutionCompleted,
    ExecutionEvent,
    ExecutionRequested,
    ExecutionStarted,
    TaskCompleted,
    TaskFailed,
    TaskStarted,
)
from adip.execution.contracts.exceptions import (
    CompensationException,
    ExecutionException,
    RetryException,
    TaskExecutionException,
)
from adip.execution.contracts.models import (
    CompensationPlan,
    CompensationTask,
    ExecutionAdapter,
    ExecutionContext,
    ExecutionHealth,
    ExecutionMetadata,
    ExecutionMetrics,
    ExecutionPackage,
    ExecutionRequest,
    ExecutionResult,
    ExecutionSandbox,
    ExecutionSchedule,
    ExecutionSession,
    ExecutionTask,
    ExecutionTaskResult,
    RetryPolicy,
)
from adip.execution.dtos import ExecutionRequestDTO, ExecutionResponseDTO, ExecutionResultDTO
from adip.execution.enums import ExecutionMode, ExecutionPriority, ExecutionState
from adip.execution.interfaces import (
    CompensationManager,
    ExecutionCoordinator,
    ExecutionManager,
    ExecutionMonitor,
    ExecutionScheduler,
    ExecutionService,
    RetryManager,
    SandboxExecutor,
    TaskExecutor,
)
from adip.execution.interfaces import (
    ExecutionAdapter as ExecutionAdapterInterface,
)

# ═══════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════


class TestExecutionState:
    def test_values(self) -> None:
        assert ExecutionState.PENDING.value == "PENDING"
        assert ExecutionState.READY.value == "READY"
        assert ExecutionState.RUNNING.value == "RUNNING"
        assert ExecutionState.WAITING.value == "WAITING"
        assert ExecutionState.PAUSED.value == "PAUSED"
        assert ExecutionState.COMPLETED.value == "COMPLETED"
        assert ExecutionState.FAILED.value == "FAILED"
        assert ExecutionState.CANCELLED.value == "CANCELLED"
        assert ExecutionState.ROLLING_BACK.value == "ROLLING_BACK"
        assert ExecutionState.ROLLED_BACK.value == "ROLLED_BACK"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExecutionState]
        assert len(values) == len(set(values))

    def test_ten_states(self) -> None:
        assert len(ExecutionState) == 10


class TestExecutionMode:
    def test_values(self) -> None:
        assert ExecutionMode.LIVE.value == "LIVE"
        assert ExecutionMode.SIMULATION.value == "SIMULATION"
        assert ExecutionMode.DRY_RUN.value == "DRY_RUN"
        assert ExecutionMode.TEST.value == "TEST"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExecutionMode]
        assert len(values) == len(set(values))

    def test_four_modes(self) -> None:
        assert len(ExecutionMode) == 4


class TestExecutionPriority:
    def test_values(self) -> None:
        assert ExecutionPriority.CRITICAL.value == "CRITICAL"
        assert ExecutionPriority.HIGH.value == "HIGH"
        assert ExecutionPriority.MEDIUM.value == "MEDIUM"
        assert ExecutionPriority.LOW.value == "LOW"

    def test_unique_values(self) -> None:
        values = [e.value for e in ExecutionPriority]
        assert len(values) == len(set(values))

    def test_four_priorities(self) -> None:
        assert len(ExecutionPriority) == 4


# ═══════════════════════════════════════════════════════════════════════
# Domain Models
# ═══════════════════════════════════════════════════════════════════════


class TestExecutionRequest:
    def test_default_request(self) -> None:
        req = ExecutionRequest(action_decision_id=uuid.uuid4())
        assert isinstance(req.request_id, uuid.UUID)
        assert req.execution_mode == ExecutionMode.LIVE
        assert req.priority == ExecutionPriority.MEDIUM
        assert req.domain == ""
        assert req.target == ""
        assert req.metadata == {}
        assert isinstance(req.created_at, datetime)

    def test_requires_action_decision_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionRequest()

    def test_with_values(self) -> None:
        decision_id = uuid.uuid4()
        req = ExecutionRequest(
            action_decision_id=decision_id,
            execution_mode=ExecutionMode.SIMULATION,
            priority=ExecutionPriority.HIGH,
            domain="energy",
            target="turbine-42",
            metadata={"env": "test"},
        )
        assert req.action_decision_id == decision_id
        assert req.execution_mode == ExecutionMode.SIMULATION
        assert req.priority == ExecutionPriority.HIGH
        assert req.domain == "energy"
        assert req.target == "turbine-42"
        assert req.metadata == {"env": "test"}


class TestRetryPolicy:
    def test_default_policy(self) -> None:
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.retry_delay_seconds == 30
        assert policy.backoff_multiplier == 2.0
        assert policy.max_delay_seconds == 3600
        assert policy.retry_on_timeout is True
        assert policy.retry_on_error is True
        assert policy.retryable_errors == []

    def test_max_retries_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            RetryPolicy(max_retries=-1)

    def test_max_retries_upper_bound(self) -> None:
        with pytest.raises(ValidationError):
            RetryPolicy(max_retries=101)

    def test_backoff_multiplier_ge_one(self) -> None:
        with pytest.raises(ValidationError):
            RetryPolicy(backoff_multiplier=0.5)

    def test_with_values(self) -> None:
        policy = RetryPolicy(
            max_retries=5,
            retry_delay_seconds=10,
            backoff_multiplier=3.0,
            max_delay_seconds=600,
            retry_on_timeout=False,
            retry_on_error=True,
            retryable_errors=["Timeout", "ConnectionError"],
        )
        assert policy.max_retries == 5
        assert policy.retry_delay_seconds == 10
        assert policy.backoff_multiplier == 3.0
        assert policy.max_delay_seconds == 600
        assert policy.retry_on_timeout is False
        assert policy.retry_on_error is True
        assert policy.retryable_errors == ["Timeout", "ConnectionError"]


class TestCompensationTask:
    def test_default_task(self) -> None:
        task = CompensationTask(original_task_id=uuid.uuid4())
        assert isinstance(task.compensation_task_id, uuid.UUID)
        assert task.name == ""
        assert task.description == ""
        assert task.order == 0
        assert task.parameters == {}
        assert task.metadata == {}

    def test_requires_original_task_id(self) -> None:
        with pytest.raises(ValidationError):
            CompensationTask()

    def test_order_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            CompensationTask(original_task_id=uuid.uuid4(), order=-1)


class TestCompensationPlan:
    def test_default_plan(self) -> None:
        plan = CompensationPlan(package_id=uuid.uuid4())
        assert isinstance(plan.compensation_id, uuid.UUID)
        assert plan.name == ""
        assert plan.description == ""
        assert plan.tasks == []
        assert plan.auto_compensate is True
        assert plan.timeout_seconds == 300

    def test_requires_package_id(self) -> None:
        with pytest.raises(ValidationError):
            CompensationPlan()

    def test_with_tasks(self) -> None:
        task = CompensationTask(original_task_id=uuid.uuid4(), name="Rollback step 1")
        plan = CompensationPlan(
            package_id=uuid.uuid4(),
            name="Rollback",
            description="Rollback the operation",
            tasks=[task],
            auto_compensate=False,
            timeout_seconds=600,
        )
        assert plan.name == "Rollback"
        assert len(plan.tasks) == 1
        assert plan.tasks[0].name == "Rollback step 1"
        assert plan.auto_compensate is False
        assert plan.timeout_seconds == 600


class TestExecutionSchedule:
    def test_default_schedule(self) -> None:
        sched = ExecutionSchedule(package_id=uuid.uuid4())
        assert isinstance(sched.schedule_id, uuid.UUID)
        assert sched.scheduled_start is None
        assert sched.scheduled_end is None
        assert sched.deadline is None
        assert sched.max_duration_minutes == 0

    def test_requires_package_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionSchedule()

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        sched = ExecutionSchedule(
            package_id=uuid.uuid4(),
            scheduled_start=now,
            scheduled_end=now,
            deadline=now,
            max_duration_minutes=120,
        )
        assert sched.scheduled_start == now
        assert sched.max_duration_minutes == 120


class TestExecutionTask:
    def test_default_task(self) -> None:
        task = ExecutionTask(package_id=uuid.uuid4())
        assert isinstance(task.task_id, uuid.UUID)
        assert task.name == ""
        assert task.description == ""
        assert task.order == 0
        assert task.task_type == ""
        assert task.parameters == {}
        assert task.dependencies == []
        assert task.timeout_seconds == 300
        assert task.retry_count == 0
        assert task.state == ExecutionState.PENDING

    def test_requires_package_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionTask()

    def test_order_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionTask(package_id=uuid.uuid4(), order=-1)

    def test_with_values(self) -> None:
        dep_id = uuid.uuid4()
        task = ExecutionTask(
            package_id=uuid.uuid4(),
            name="Check status",
            description="Check system status",
            order=1,
            task_type="script",
            parameters={"cmd": "status"},
            dependencies=[dep_id],
            timeout_seconds=60,
            retry_count=2,
            state=ExecutionState.READY,
        )
        assert task.name == "Check status"
        assert task.order == 1
        assert task.task_type == "script"
        assert task.dependencies == [dep_id]
        assert task.timeout_seconds == 60
        assert task.retry_count == 2
        assert task.state == ExecutionState.READY


class TestExecutionTaskResult:
    def test_default_result(self) -> None:
        result = ExecutionTaskResult(task_id=uuid.uuid4())
        assert isinstance(result.result_id, uuid.UUID)
        assert result.success is False
        assert result.output == ""
        assert result.error_message == ""
        assert result.error_code == ""
        assert result.started_at is None
        assert result.completed_at is None
        assert result.duration_ms == 0
        assert result.retry_attempt == 0

    def test_requires_task_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionTaskResult()

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        result = ExecutionTaskResult(
            task_id=uuid.uuid4(),
            success=True,
            output="OK",
            error_message="",
            error_code="",
            started_at=now,
            completed_at=now,
            duration_ms=1500,
            retry_attempt=1,
        )
        assert result.success is True
        assert result.output == "OK"
        assert result.duration_ms == 1500
        assert result.retry_attempt == 1


class TestExecutionResult:
    def test_default_result(self) -> None:
        result = ExecutionResult(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
        )
        assert isinstance(result.result_id, uuid.UUID)
        assert result.overall_success is False
        assert result.task_results == []
        assert result.error_message == ""
        assert result.started_at is None
        assert result.completed_at is None
        assert result.total_duration_ms == 0

    def test_requires_request_and_session(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionResult()

    def test_with_results(self) -> None:
        task_result = ExecutionTaskResult(task_id=uuid.uuid4(), success=True)
        result = ExecutionResult(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            overall_success=True,
            task_results=[task_result],
            error_message="",
            total_duration_ms=5000,
        )
        assert result.overall_success is True
        assert len(result.task_results) == 1
        assert result.total_duration_ms == 5000


class TestExecutionPackage:
    def test_default_package(self) -> None:
        pkg = ExecutionPackage(action_decision_id=uuid.uuid4())
        assert isinstance(pkg.package_id, uuid.UUID)
        assert pkg.name == ""
        assert pkg.description == ""
        assert pkg.tasks == []
        assert pkg.dependencies == []
        assert pkg.schedule is None
        assert pkg.retry_policy is None
        assert pkg.compensation_plan is None
        assert pkg.state == ExecutionState.PENDING
        assert isinstance(pkg.created_at, datetime)
        assert isinstance(pkg.updated_at, datetime)

    def test_requires_action_decision_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionPackage()

    def test_with_full_data(self) -> None:
        task = ExecutionTask(package_id=uuid.uuid4(), name="Task 1")
        sched = ExecutionSchedule(package_id=uuid.uuid4())
        policy = RetryPolicy(max_retries=2)
        comp = CompensationPlan(package_id=uuid.uuid4())
        pkg = ExecutionPackage(
            action_decision_id=uuid.uuid4(),
            name="Deploy",
            description="Deploy update",
            tasks=[task],
            schedule=sched,
            retry_policy=policy,
            compensation_plan=comp,
            state=ExecutionState.READY,
        )
        assert pkg.name == "Deploy"
        assert len(pkg.tasks) == 1
        assert pkg.schedule is not None
        assert pkg.retry_policy is not None
        assert pkg.compensation_plan is not None
        assert pkg.state == ExecutionState.READY


class TestExecutionSession:
    def test_default_session(self) -> None:
        sess = ExecutionSession(
            request_id=uuid.uuid4(),
            package_id=uuid.uuid4(),
        )
        assert isinstance(sess.session_id, uuid.UUID)
        assert sess.state == ExecutionState.PENDING
        assert sess.execution_mode == ExecutionMode.LIVE
        assert sess.priority == ExecutionPriority.MEDIUM
        assert sess.started_at is None
        assert sess.completed_at is None
        assert sess.task_count == 0
        assert sess.tasks_completed == 0
        assert sess.tasks_failed == 0
        assert sess.tasks_skipped == 0
        assert sess.error_message == ""

    def test_requires_request_and_package(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionSession()

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        sess = ExecutionSession(
            request_id=uuid.uuid4(),
            package_id=uuid.uuid4(),
            state=ExecutionState.RUNNING,
            execution_mode=ExecutionMode.SIMULATION,
            priority=ExecutionPriority.HIGH,
            started_at=now,
            task_count=5,
            tasks_completed=2,
            tasks_failed=0,
            error_message="",
        )
        assert sess.state == ExecutionState.RUNNING
        assert sess.execution_mode == ExecutionMode.SIMULATION
        assert sess.priority == ExecutionPriority.HIGH
        assert sess.task_count == 5
        assert sess.tasks_completed == 2


class TestExecutionContext:
    def test_default_context(self) -> None:
        ctx = ExecutionContext(request_id=uuid.uuid4())
        assert isinstance(ctx.context_id, uuid.UUID)
        assert ctx.asset_id == ""
        assert ctx.machine_id == ""
        assert ctx.facility_id == ""
        assert ctx.workflow_id == ""
        assert ctx.domain == ""
        assert ctx.sandbox is None
        assert ctx.adapter is None

    def test_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionContext()

    def test_with_sandbox_and_adapter(self) -> None:
        sandbox = ExecutionSandbox()
        adapter = ExecutionAdapter()
        ctx = ExecutionContext(
            request_id=uuid.uuid4(),
            asset_id="asset-1",
            machine_id="machine-1",
            domain="energy",
            sandbox=sandbox,
            adapter=adapter,
        )
        assert ctx.asset_id == "asset-1"
        assert ctx.sandbox is not None
        assert ctx.adapter is not None


class TestExecutionSandbox:
    def test_default_sandbox(self) -> None:
        sandbox = ExecutionSandbox()
        assert isinstance(sandbox.sandbox_id, uuid.UUID)
        assert sandbox.name == ""
        assert sandbox.namespace == "default"
        assert sandbox.resource_limits == {}
        assert sandbox.permissions == []
        assert sandbox.enabled is True

    def test_with_values(self) -> None:
        sandbox = ExecutionSandbox(
            name="secure-box",
            namespace="energy-prod",
            resource_limits={"cpu": 2.0, "memory": 1024.0},
            permissions=["read", "write"],
            enabled=True,
        )
        assert sandbox.name == "secure-box"
        assert sandbox.namespace == "energy-prod"
        assert sandbox.resource_limits == {"cpu": 2.0, "memory": 1024.0}
        assert len(sandbox.permissions) == 2


class TestExecutionAdapter:
    def test_default_adapter(self) -> None:
        adapter = ExecutionAdapter()
        assert isinstance(adapter.adapter_id, uuid.UUID)
        assert adapter.name == ""
        assert adapter.adapter_type == ""
        assert adapter.configuration == {}
        assert adapter.enabled is True
        assert adapter.version == "1.0.0"

    def test_with_values(self) -> None:
        adapter = ExecutionAdapter(
            name="MQTT Connector",
            adapter_type="mqtt",
            configuration={"host": "localhost", "port": 1883},
            enabled=True,
            version="2.0.0",
        )
        assert adapter.name == "MQTT Connector"
        assert adapter.adapter_type == "mqtt"
        assert adapter.configuration == {"host": "localhost", "port": 1883}
        assert adapter.version == "2.0.0"


class TestExecutionMetadata:
    def test_default_metadata(self) -> None:
        meta = ExecutionMetadata()
        assert meta.title == ""
        assert meta.description == ""
        assert meta.tags == []
        assert meta.category == ""
        assert meta.source == ""
        assert meta.version == "1.0.0"

    def test_with_values(self) -> None:
        meta = ExecutionMetadata(
            title="Deploy Update",
            description="Deploy version 2.0",
            tags=["deploy", "update"],
            category="operations",
            source="ci-pipeline",
            version="2.0.0",
        )
        assert meta.title == "Deploy Update"
        assert len(meta.tags) == 2
        assert meta.category == "operations"


class TestExecutionHealth:
    def test_default_health(self) -> None:
        health = ExecutionHealth()
        assert health.overall_status == ""
        assert health.coordinator_status == ""
        assert health.executor_status == ""
        assert health.scheduler_status == ""
        assert health.retry_manager_status == ""
        assert health.compensation_manager_status == ""
        assert health.monitor_status == ""
        assert health.sandbox_status == ""
        assert health.session_count == 0
        assert health.active_tasks == 0
        assert health.error_count == 0
        assert isinstance(health.last_check, datetime)

    def test_health_counts_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionHealth(session_count=-1)
        with pytest.raises(ValidationError):
            ExecutionHealth(active_tasks=-1)
        with pytest.raises(ValidationError):
            ExecutionHealth(error_count=-1)

    def test_with_values(self) -> None:
        health = ExecutionHealth(
            overall_status="healthy",
            coordinator_status="up",
            executor_status="up",
            session_count=10,
            active_tasks=3,
            error_count=1,
        )
        assert health.overall_status == "healthy"
        assert health.session_count == 10
        assert health.active_tasks == 3


class TestExecutionMetrics:
    def test_default_metrics(self) -> None:
        metrics = ExecutionMetrics()
        assert metrics.sessions_total == 0
        assert metrics.sessions_completed == 0
        assert metrics.sessions_failed == 0
        assert metrics.tasks_total == 0
        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.tasks_skipped == 0
        assert metrics.retries_total == 0
        assert metrics.compensations_total == 0
        assert metrics.average_task_duration_ms == 0.0
        assert metrics.average_session_duration_ms == 0.0
        assert metrics.success_rate == 0.0
        assert isinstance(metrics.timestamp, datetime)

    def test_metrics_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionMetrics(sessions_total=-1)
        with pytest.raises(ValidationError):
            ExecutionMetrics(tasks_total=-1)
        with pytest.raises(ValidationError):
            ExecutionMetrics(retries_total=-1)

    def test_success_rate_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionMetrics(success_rate=-0.1)
        with pytest.raises(ValidationError):
            ExecutionMetrics(success_rate=1.1)

    def test_with_values(self) -> None:
        metrics = ExecutionMetrics(
            sessions_total=50,
            sessions_completed=45,
            sessions_failed=5,
            tasks_total=200,
            tasks_completed=180,
            tasks_failed=15,
            tasks_skipped=5,
            retries_total=10,
            compensations_total=3,
            average_task_duration_ms=1200.5,
            average_session_duration_ms=30000.0,
            success_rate=0.9,
        )
        assert metrics.sessions_total == 50
        assert metrics.tasks_total == 200
        assert metrics.success_rate == 0.9


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════


class TestExecutionRequestDTO:
    def test_default_dto(self) -> None:
        dto = ExecutionRequestDTO(action_decision_id=uuid.uuid4())
        assert isinstance(dto.request_id, uuid.UUID)
        assert dto.execution_mode == ExecutionMode.LIVE
        assert dto.priority == ExecutionPriority.MEDIUM
        assert dto.domain == ""
        assert dto.target == ""

    def test_requires_action_decision_id(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionRequestDTO()

    def test_with_values(self) -> None:
        dto = ExecutionRequestDTO(
            action_decision_id=uuid.uuid4(),
            execution_mode=ExecutionMode.DRY_RUN,
            priority=ExecutionPriority.CRITICAL,
            domain="energy",
            target="turbine-42",
        )
        assert dto.execution_mode == ExecutionMode.DRY_RUN
        assert dto.priority == ExecutionPriority.CRITICAL


class TestExecutionResponseDTO:
    def test_default_dto(self) -> None:
        dto = ExecutionResponseDTO(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
        )
        assert isinstance(dto.response_id, uuid.UUID)
        assert dto.state == ExecutionState.PENDING
        assert dto.execution_mode == ExecutionMode.LIVE
        assert dto.message == ""
        assert isinstance(dto.timestamp, datetime)

    def test_requires_request_and_session(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionResponseDTO()

    def test_with_values(self) -> None:
        dto = ExecutionResponseDTO(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            state=ExecutionState.RUNNING,
            execution_mode=ExecutionMode.SIMULATION,
            message="Execution started",
        )
        assert dto.state == ExecutionState.RUNNING
        assert dto.execution_mode == ExecutionMode.SIMULATION
        assert dto.message == "Execution started"


class TestExecutionResultDTO:
    def test_default_dto(self) -> None:
        dto = ExecutionResultDTO(
            session_id=uuid.uuid4(),
            request_id=uuid.uuid4(),
        )
        assert isinstance(dto.result_id, uuid.UUID)
        assert dto.overall_success is False
        assert dto.tasks_total == 0
        assert dto.tasks_completed == 0
        assert dto.tasks_failed == 0
        assert dto.error_message == ""
        assert dto.total_duration_ms == 0

    def test_requires_session_and_request(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionResultDTO()

    def test_with_values(self) -> None:
        dto = ExecutionResultDTO(
            session_id=uuid.uuid4(),
            request_id=uuid.uuid4(),
            overall_success=True,
            tasks_total=10,
            tasks_completed=9,
            tasks_failed=1,
            error_message="One task failed",
            total_duration_ms=45000,
        )
        assert dto.overall_success is True
        assert dto.tasks_total == 10
        assert dto.tasks_completed == 9
        assert dto.tasks_failed == 1


# ═══════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════


class TestExecutionEvent:
    def test_base_event(self) -> None:
        event = ExecutionEvent()
        assert isinstance(event.event_id, uuid.UUID)
        assert isinstance(event.timestamp, datetime)
        assert event.correlation_id == ""

    def test_event_inheritance(self) -> None:
        assert issubclass(ExecutionRequested, ExecutionEvent)
        assert issubclass(ExecutionStarted, ExecutionEvent)
        assert issubclass(TaskStarted, ExecutionEvent)
        assert issubclass(TaskCompleted, ExecutionEvent)
        assert issubclass(TaskFailed, ExecutionEvent)
        assert issubclass(ExecutionCompleted, ExecutionEvent)

    def test_event_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionRequested()
        with pytest.raises(ValidationError):
            ExecutionStarted()
        with pytest.raises(ValidationError):
            TaskStarted()
        with pytest.raises(ValidationError):
            TaskCompleted()
        with pytest.raises(ValidationError):
            TaskFailed()
        with pytest.raises(ValidationError):
            ExecutionCompleted()


class TestExecutionRequested:
    def test_with_values(self) -> None:
        event = ExecutionRequested(
            request_id=uuid.uuid4(),
            action_decision_id=uuid.uuid4(),
            execution_mode=ExecutionMode.LIVE,
            priority=ExecutionPriority.HIGH,
        )
        assert event.execution_mode == ExecutionMode.LIVE
        assert event.priority == ExecutionPriority.HIGH


class TestExecutionStarted:
    def test_with_values(self) -> None:
        event = ExecutionStarted(
            session_id=uuid.uuid4(),
            package_id=uuid.uuid4(),
            task_count=5,
        )
        assert event.task_count == 5


class TestTaskStarted:
    def test_with_values(self) -> None:
        event = TaskStarted(
            task_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            task_name="Check status",
        )
        assert event.task_name == "Check status"


class TestTaskCompleted:
    def test_with_values(self) -> None:
        event = TaskCompleted(
            task_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            success=True,
            duration_ms=1500,
        )
        assert event.success is True
        assert event.duration_ms == 1500

    def test_duration_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            TaskCompleted(
                task_id=uuid.uuid4(),
                session_id=uuid.uuid4(),
                duration_ms=-1,
            )


class TestTaskFailed:
    def test_with_values(self) -> None:
        event = TaskFailed(
            task_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            error_message="Connection timeout",
            error_code="TIMEOUT",
            retry_attempt=2,
        )
        assert event.error_message == "Connection timeout"
        assert event.error_code == "TIMEOUT"
        assert event.retry_attempt == 2


class TestExecutionCompleted:
    def test_with_values(self) -> None:
        event = ExecutionCompleted(
            session_id=uuid.uuid4(),
            overall_success=True,
            state=ExecutionState.COMPLETED,
            total_duration_ms=30000,
            tasks_completed=5,
            tasks_failed=0,
        )
        assert event.overall_success is True
        assert event.state == ExecutionState.COMPLETED
        assert event.total_duration_ms == 30000
        assert event.tasks_completed == 5


# ═══════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════


class TestExecutionException:
    def test_base_exception(self) -> None:
        exc = ExecutionException()
        assert isinstance(exc, Exception)
        assert exc.message == "Execution error occurred"
        assert exc.code == "EXECUTION_ERROR"
        assert exc.details == {}

    def test_default_messages(self) -> None:
        assert TaskExecutionException().message == "Task execution error occurred"
        assert TaskExecutionException().code == "TASK_EXECUTION_ERROR"
        assert RetryException().message == "Retry error occurred"
        assert RetryException().code == "RETRY_ERROR"
        assert CompensationException().message == "Compensation error occurred"
        assert CompensationException().code == "COMPENSATION_ERROR"

    def test_exception_hierarchy(self) -> None:
        assert issubclass(TaskExecutionException, ExecutionException)
        assert issubclass(RetryException, ExecutionException)
        assert issubclass(CompensationException, ExecutionException)

    def test_details(self) -> None:
        exc = ExecutionException(
            message="Custom error",
            code="CUSTOM_CODE",
            details={"task_id": "abc-123"},
        )
        assert exc.message == "Custom error"
        assert exc.code == "CUSTOM_CODE"
        assert exc.details == {"task_id": "abc-123"}


# ═══════════════════════════════════════════════════════════════════════
# Interfaces
# ═══════════════════════════════════════════════════════════════════════


class TestInterfacesAreAbstract:
    def test_execution_service_is_abstract(self) -> None:
        assert issubclass(ExecutionService, ABC)

    def test_execution_manager_is_abstract(self) -> None:
        assert issubclass(ExecutionManager, ABC)

    def test_execution_coordinator_is_abstract(self) -> None:
        assert issubclass(ExecutionCoordinator, ABC)

    def test_task_executor_is_abstract(self) -> None:
        assert issubclass(TaskExecutor, ABC)

    def test_retry_manager_is_abstract(self) -> None:
        assert issubclass(RetryManager, ABC)

    def test_compensation_manager_is_abstract(self) -> None:
        assert issubclass(CompensationManager, ABC)

    def test_execution_monitor_is_abstract(self) -> None:
        assert issubclass(ExecutionMonitor, ABC)

    def test_execution_scheduler_is_abstract(self) -> None:
        assert issubclass(ExecutionScheduler, ABC)

    def test_sandbox_executor_is_abstract(self) -> None:
        assert issubclass(SandboxExecutor, ABC)

    def test_execution_adapter_is_abstract(self) -> None:
        assert issubclass(ExecutionAdapterInterface, ABC)


class TestServiceInterfaceMethods:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "start_execution",
            "get_session",
            "get_result",
            "get_package",
            "cancel_execution",
            "get_health",
            "get_metrics",
        ]
        for method in methods:
            assert hasattr(ExecutionService, method)
            assert callable(getattr(ExecutionService, method))

    def test_service_returns_dto(self) -> None:
        import inspect

        sig = inspect.signature(ExecutionService.start_execution)
        hint = sig.return_annotation
        # Python 3.11 returns string, 3.12+ returns type
        assert hint is not inspect.Parameter.empty


class TestManagerInterfaceMethods:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "start_execution",
            "get_session",
            "get_result",
            "get_package",
            "cancel_execution",
            "get_health",
            "get_metrics",
        ]
        for method in methods:
            assert hasattr(ExecutionManager, method)
            assert callable(getattr(ExecutionManager, method))


class TestCoordinatorInterfaceMethods:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "execute",
            "get_session",
            "get_result",
            "get_package",
            "cancel",
            "health",
            "metrics",
        ]
        for method in methods:
            assert hasattr(ExecutionCoordinator, method)
            assert callable(getattr(ExecutionCoordinator, method))


class TestTaskExecutorInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(TaskExecutor, "execute_task")
        assert hasattr(TaskExecutor, "validate_task")


class TestRetryManagerInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(RetryManager, "should_retry")
        assert hasattr(RetryManager, "get_delay")


class TestCompensationManagerInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(CompensationManager, "execute_compensation")
        assert hasattr(CompensationManager, "validate_compensation")


class TestExecutionMonitorInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(ExecutionMonitor, "get_session_state")
        assert hasattr(ExecutionMonitor, "get_active_sessions")


class TestExecutionSchedulerInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(ExecutionScheduler, "schedule_execution")
        assert hasattr(ExecutionScheduler, "cancel_scheduled")


class TestSandboxExecutorInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(SandboxExecutor, "execute_in_sandbox")
        assert hasattr(SandboxExecutor, "validate_sandbox")


class TestExecutionAdapterInterface:
    def test_has_required_methods(self) -> None:
        assert hasattr(ExecutionAdapterInterface, "execute")
        assert hasattr(ExecutionAdapterInterface, "validate")
        assert hasattr(ExecutionAdapterInterface, "get_capabilities")


# ═══════════════════════════════════════════════════════════════════════
# Module Import
# ═══════════════════════════════════════════════════════════════════════


class TestModuleImport:
    def test_import_enums(self) -> None:
        from adip.execution.enums import (
            ExecutionMode,
            ExecutionPriority,
            ExecutionState,
        )

        assert ExecutionState is not None
        assert ExecutionMode is not None
        assert ExecutionPriority is not None

    def test_import_models(self) -> None:
        from adip.execution.contracts.models import (
            CompensationPlan,
            ExecutionPackage,
            ExecutionRequest,
            ExecutionResult,
            ExecutionTask,
            RetryPolicy,
        )

        assert ExecutionRequest is not None
        assert ExecutionPackage is not None
        assert ExecutionTask is not None
        assert RetryPolicy is not None
        assert CompensationPlan is not None
        assert ExecutionResult is not None

    def test_import_events(self) -> None:
        from adip.execution.contracts.events import (
            ExecutionEvent,
            ExecutionRequested,
        )

        assert ExecutionEvent is not None
        assert ExecutionRequested is not None

    def test_import_exceptions(self) -> None:
        from adip.execution.contracts.exceptions import (
            ExecutionException,
        )

        assert ExecutionException is not None

    def test_import_interfaces(self) -> None:
        from adip.execution.interfaces import (
            ExecutionCoordinator,
            ExecutionService,
        )

        assert ExecutionService is not None
        assert ExecutionCoordinator is not None

    def test_import_dtos(self) -> None:
        from adip.execution.dtos import (
            ExecutionRequestDTO,
        )

        assert ExecutionRequestDTO is not None

    def test_package_import(self) -> None:
        from adip import execution

        assert execution.ExecutionService is not None
        assert execution.ExecutionState is not None
        assert execution.ExecutionMode is not None
        assert execution.ExecutionPriority is not None
        assert execution.execution_models is not None

    def test_package_all(self) -> None:
        from adip.execution import __all__

        assert "ExecutionService" in __all__
        assert "ExecutionState" in __all__
        assert "ExecutionMode" in __all__
        assert "ExecutionRequestDTO" in __all__
        assert "ExecutionResponseDTO" in __all__
        assert "ExecutionResultDTO" in __all__
