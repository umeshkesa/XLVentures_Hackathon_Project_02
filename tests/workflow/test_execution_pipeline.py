"""Comprehensive tests for Workflow Engine Phase 2 execution pipeline."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from adip.planner.contracts.models import (
    ExecutionPlan,
    PlanningGoal,
    PlanningTask,
)
from adip.planner.enums import TaskStatusEnum
from adip.workflow.contracts.exceptions import (
    WorkflowValidationException,
)
from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowContext,
    WorkflowGraph,
    WorkflowRequest,
    WorkflowTask,
)
from adip.workflow.enums import (
    RetryPolicy,
    TaskExecutionStatus,
)
from adip.workflow.execution.agent_executor import PlaceholderExecutor
from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
from adip.workflow.execution.dispatcher import PlaceholderDispatcher
from adip.workflow.execution.execution_dispatcher import (
    DefaultExecutionDispatcher,
)
from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
from adip.workflow.execution.graph_builder import DefaultGraphBuilder
from adip.workflow.execution.retry_manager import DefaultRetryManager
from adip.workflow.execution.scheduler import DefaultScheduler
from adip.workflow.execution.strategy import SequentialStrategy
from adip.workflow.execution.trace import WorkflowTrace
from adip.workflow.interfaces import GraphBuilder, TaskScheduler

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_plan() -> ExecutionPlan:
    goal = PlanningGoal(objective="Test execution pipeline")
    tasks = [
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task A",
            description="First task with no dependencies",
            dependencies=[],
            inputs={"cmd": "echo A"},
            status=TaskStatusEnum.PENDING,
        ),
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task B",
            description="Second task depends on A",
            dependencies=[],  # will set below
            inputs={"cmd": "echo B"},
            status=TaskStatusEnum.PENDING,
        ),
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task C",
            description="Third task depends on B",
            dependencies=[],  # will set below
            inputs={"cmd": "echo C"},
            status=TaskStatusEnum.PENDING,
        ),
    ]
    # Wire dependencies: A → B → C
    tasks[1].dependencies = [tasks[0].task_id]
    tasks[2].dependencies = [tasks[1].task_id]
    return ExecutionPlan(goal=goal, tasks=tasks)


@pytest.fixture
def sample_request(sample_plan: ExecutionPlan) -> WorkflowRequest:
    return WorkflowRequest(
        execution_plan=sample_plan,
        workflow_context=WorkflowContext(),
        metadata={"source": "test"},
    )


@pytest.fixture
def graph_builder() -> DefaultGraphBuilder:
    return DefaultGraphBuilder()


@pytest.fixture
def scheduler() -> DefaultScheduler:
    return DefaultScheduler()


@pytest.fixture
def dispatcher() -> PlaceholderDispatcher:
    return PlaceholderDispatcher()


@pytest.fixture
def executor() -> PlaceholderExecutor:
    return PlaceholderExecutor()


@pytest.fixture
def monitor() -> DefaultExecutionMonitor:
    return DefaultExecutionMonitor()


@pytest.fixture
def retry_manager() -> DefaultRetryManager:
    return DefaultRetryManager()


@pytest.fixture
def approval_manager() -> PlaceholderApprovalManager:
    return PlaceholderApprovalManager()


@pytest.fixture
def execution_dispatcher(
    dispatcher: PlaceholderDispatcher,
    executor: PlaceholderExecutor,
    monitor: DefaultExecutionMonitor,
    retry_manager: DefaultRetryManager,
    approval_manager: PlaceholderApprovalManager,
) -> DefaultExecutionDispatcher:
    return DefaultExecutionDispatcher(
        task_dispatcher=dispatcher,
        agent_executor=executor,
        execution_monitor=monitor,
        retry_manager=retry_manager,
        approval_manager=approval_manager,
    )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowTrace
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowTrace:
    def test_default_creation(self) -> None:
        trace = WorkflowTrace(stage_name="test_stage")
        assert trace.stage_name == "test_stage"
        assert trace.success is True
        assert trace.warnings == []
        assert trace.duration_ms is None
        assert trace.workflow_version == "0.1.0"

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        trace = WorkflowTrace(
            stage_name="custom",
            started_at=now,
            completed_at=now,
            duration_ms=42.5,
            input_summary={"key": "val"},
            output_summary={"result": "ok"},
            success=False,
            warnings=["warning 1"],
            workflow_version="0.2.0",
            correlation_id="corr-123",
        )
        assert trace.duration_ms == 42.5
        assert trace.success is False
        assert trace.correlation_id == "corr-123"
        assert trace.workflow_version == "0.2.0"

    def test_mirrors_planning_trace_structure(self) -> None:
        """WorkflowTrace should have the same core fields as PlanningTrace."""
        wf = WorkflowTrace(stage_name="x")
        assert hasattr(wf, "stage_name")
        assert hasattr(wf, "started_at")
        assert hasattr(wf, "completed_at")
        assert hasattr(wf, "duration_ms")
        assert hasattr(wf, "input_summary")
        assert hasattr(wf, "output_summary")
        assert hasattr(wf, "success")
        assert hasattr(wf, "warnings")
        assert hasattr(wf, "correlation_id")


# ─────────────────────────────────────────────────────────────────────────────
# ExecutionStrategy / SequentialStrategy
# ─────────────────────────────────────────────────────────────────────────────


class TestExecutionStrategy:
    @pytest.mark.asyncio
    async def test_sequential_strategy_returns_one_task_per_wave(
        self,
    ) -> None:
        strategy = SequentialStrategy()
        tasks = [
            WorkflowTask(task_id=uuid.uuid4(), task_name="A", dependencies=[]),
            WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[uuid.uuid4()]),
        ]
        tasks[1].dependencies = [tasks[0].task_id]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        schedule = await strategy.create_schedule(graph)
        assert len(schedule) == 2  # A, B each in own wave
        for wave in schedule:
            assert len(wave) == 1  # each wave has exactly one task

    @pytest.mark.asyncio
    async def test_sequential_follows_topological_order(self) -> None:
        strategy = SequentialStrategy()
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        c_id = uuid.uuid4()
        tasks = [
            WorkflowTask(task_id=a_id, task_name="A", dependencies=[b_id]),
            WorkflowTask(task_id=b_id, task_name="B", dependencies=[c_id]),
            WorkflowTask(task_id=c_id, task_name="C", dependencies=[]),
        ]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        schedule = await strategy.create_schedule(graph)
        # C must come before B before A
        ids = [wave[0] for wave in schedule]
        assert ids == [c_id, b_id, a_id]


# ─────────────────────────────────────────────────────────────────────────────
# Graph Builder
# ─────────────────────────────────────────────────────────────────────────────


class TestGraphBuilder:
    @pytest.mark.asyncio
    async def test_build_creates_correct_nodes(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        graph = await graph_builder.build(sample_request)
        assert len(graph.nodes) == 3
        for pt in sample_request.execution_plan.tasks:
            assert pt.task_id in graph.nodes

    @pytest.mark.asyncio
    async def test_build_preserves_dependencies(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        graph = await graph_builder.build(sample_request)
        for pt in sample_request.execution_plan.tasks:
            wt = graph.nodes[pt.task_id]
            assert list(wt.dependencies) == list(pt.dependencies)

    @pytest.mark.asyncio
    async def test_detects_duplicate_nodes(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        dup_id = sample_request.execution_plan.tasks[0].task_id
        sample_request.execution_plan.tasks.append(
            PlanningTask(
                task_id=dup_id,
                description="Duplicate",
            ),
        )
        with pytest.raises(WorkflowValidationException, match="Duplicate"):
            await graph_builder.build(sample_request)

    @pytest.mark.asyncio
    async def test_detects_missing_dependency(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        # Add a task that references a nonexistent dependency
        bad_id = uuid.uuid4()
        sample_request.execution_plan.tasks.append(
            PlanningTask(
                task_id=uuid.uuid4(),
                task_name="Orphan",
                description="Has missing dependency",
                dependencies=[bad_id],
            ),
        )
        with pytest.raises(WorkflowValidationException, match="missing"):
            await graph_builder.build(sample_request)

    @pytest.mark.asyncio
    async def test_detects_cycles(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        tasks = sample_request.execution_plan.tasks
        # A ← C (creates cycle: A → B → C → A)
        tasks[0].dependencies.append(tasks[2].task_id)
        with pytest.raises(WorkflowValidationException, match="cycle"):
            await graph_builder.build(sample_request)

    @pytest.mark.asyncio
    async def test_preserves_task_metadata(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        graph = await graph_builder.build(sample_request)
        for pt in sample_request.execution_plan.tasks:
            wt = graph.nodes[pt.task_id]
            assert wt.execution_metadata["requires_human_approval"] == pt.requires_human_approval
            assert wt.execution_metadata["parallelizable"] == pt.parallelizable

    @pytest.mark.asyncio
    async def test_acyclic_graph_passes(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        graph = await graph_builder.build(sample_request)
        assert graph.detect_cycles() == []

    @pytest.mark.asyncio
    async def test_root_nodes_identified(
        self, graph_builder: DefaultGraphBuilder, sample_request: WorkflowRequest,
    ) -> None:
        graph = await graph_builder.build(sample_request)
        roots = graph.get_root_nodes()
        root_ids = {t.task_id for t in roots}
        first_id = sample_request.execution_plan.tasks[0].task_id
        assert first_id in root_ids
        assert len(roots) == 1  # Only the first task has no deps


# ─────────────────────────────────────────────────────────────────────────────
# Task Scheduler
# ─────────────────────────────────────────────────────────────────────────────


class TestScheduler:
    @pytest.mark.asyncio
    async def test_schedule_returns_root_tasks(
        self, scheduler: DefaultScheduler,
    ) -> None:
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        tasks = [
            WorkflowTask(task_id=a_id, task_name="A", dependencies=[]),
            WorkflowTask(task_id=b_id, task_name="B", dependencies=[a_id]),
        ]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        result = await scheduler.schedule(graph)
        assert len(result) == 1
        assert result[0].task_id == a_id

    @pytest.mark.asyncio
    async def test_schedule_skips_completed_tasks(
        self, scheduler: DefaultScheduler,
    ) -> None:
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        tasks = [
            WorkflowTask(
                task_id=a_id, task_name="A", dependencies=[],
                runtime_status=TaskExecutionStatus.COMPLETED,
            ),
            WorkflowTask(
                task_id=b_id, task_name="B", dependencies=[a_id],
            ),
        ]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        result = await scheduler.schedule(graph)
        assert len(result) == 1
        assert result[0].task_id == b_id

    @pytest.mark.asyncio
    async def test_schedule_returns_empty_when_all_complete(
        self, scheduler: DefaultScheduler,
    ) -> None:
        a_id = uuid.uuid4()
        tasks = [
            WorkflowTask(
                task_id=a_id, task_name="A", dependencies=[],
                runtime_status=TaskExecutionStatus.COMPLETED,
            ),
        ]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        result = await scheduler.schedule(graph)
        assert result == []

    @pytest.mark.asyncio
    async def test_schedule_respects_strategy(
        self, scheduler: DefaultScheduler,
    ) -> None:
        a_id = uuid.uuid4()
        tasks = [
            WorkflowTask(task_id=a_id, task_name="A", dependencies=[]),
        ]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        result = await scheduler.schedule(graph)
        assert len(result) == 1
        assert result[0].task_name == "A"

    @pytest.mark.asyncio
    async def test_schedule_handles_parallel_roots(
        self, scheduler: DefaultScheduler,
    ) -> None:
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        tasks = [
            WorkflowTask(task_id=a_id, task_name="A", dependencies=[]),
            WorkflowTask(task_id=b_id, task_name="B", dependencies=[]),
        ]
        graph = WorkflowGraph.from_workflow_tasks(tasks)
        result = await scheduler.schedule(graph)
        # With SequentialStrategy, only the first topological task is returned
        assert len(result) == 1
        assert result[0].task_id in (a_id, b_id)


# ─────────────────────────────────────────────────────────────────────────────
# Task Dispatcher
# ─────────────────────────────────────────────────────────────────────────────


class TestDispatcher:
    @pytest.mark.asyncio
    async def test_dispatcher_assigns_executor(
        self, dispatcher: PlaceholderDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Test",
            execution_metadata={"required_capability": "data_search"},
        )
        result = await dispatcher.dispatch(task)
        assert result.assigned_executor == "search_agent"

    @pytest.mark.asyncio
    async def test_dispatcher_default_executor(
        self, dispatcher: PlaceholderDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Test",
        )
        result = await dispatcher.dispatch(task)
        assert result.assigned_executor == "default_agent"

    @pytest.mark.asyncio
    async def test_dispatcher_maps_all_known_capabilities(
        self, dispatcher: PlaceholderDispatcher,
    ) -> None:
        known = {
            "data_search": "search_agent",
            "computation": "compute_agent",
            "analytics": "analytics_agent",
            "summarization": "summary_agent",
            "translation": "translate_agent",
            "database": "db_agent",
            "api_call": "api_agent",
        }
        for capability, expected_executor in known.items():
            task = WorkflowTask(
                task_id=uuid.uuid4(),
                task_name=capability,
                execution_metadata={"required_capability": capability},
            )
            result = await dispatcher.dispatch(task)
            assert result.assigned_executor == expected_executor


# ─────────────────────────────────────────────────────────────────────────────
# Agent Executor
# ─────────────────────────────────────────────────────────────────────────────


class TestAgentExecutor:
    @pytest.mark.asyncio
    async def test_executor_returns_success_result(
        self, executor: PlaceholderExecutor,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Test Task",
            assigned_executor="default_agent",
        )
        result = await executor.execute(task)
        assert result.success is True
        assert result.execution_time is not None
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_executor_sets_outputs(
        self, executor: PlaceholderExecutor,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="My Task",
            assigned_executor="search_agent",
        )
        result = await executor.execute(task)
        assert "result" in result.outputs
        assert "My Task completed" in result.outputs["result"]
        assert result.outputs["executor"] == "search_agent"

    @pytest.mark.asyncio
    async def test_executor_fixed_duration(
        self, executor: PlaceholderExecutor,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Duration Test",
        )
        result = await executor.execute(task)
        assert result.execution_time == 0.01  # 10ms fixed
        assert result.metadata["strategy"] == "placeholder"


# ─────────────────────────────────────────────────────────────────────────────
# Execution Monitor
# ─────────────────────────────────────────────────────────────────────────────


class TestExecutionMonitor:
    @pytest.mark.asyncio
    async def test_initial_metrics(self, monitor: DefaultExecutionMonitor) -> None:
        metrics = monitor.get_metrics()
        assert metrics.scheduled_tasks == 0
        assert metrics.executed_tasks == 0
        assert metrics.successful_tasks == 0
        assert metrics.failed_tasks == 0

    @pytest.mark.asyncio
    async def test_tracks_task_states(self, monitor: DefaultExecutionMonitor) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="A")

        monitor.record_task_pending(task)
        monitor.record_task_ready(task)
        monitor.record_task_running(task)

        summary = monitor.get_status_summary()
        assert summary["PENDING"] >= 1
        assert summary["READY"] >= 1
        assert summary["RUNNING"] >= 1

    @pytest.mark.asyncio
    async def test_on_task_completed(
        self, monitor: DefaultExecutionMonitor,
    ) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        result = TaskResult(success=True)
        graph = WorkflowGraph()

        monitor.record_task_pending(task)
        await monitor.on_task_completed(task, result, graph)

        metrics = monitor.get_metrics()
        assert metrics.successful_tasks == 1
        assert metrics.executed_tasks >= 1

    @pytest.mark.asyncio
    async def test_on_task_failed(
        self, monitor: DefaultExecutionMonitor,
    ) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        result = TaskResult(success=False, errors=["Something went wrong"])
        graph = WorkflowGraph()

        monitor.record_task_pending(task)
        await monitor.on_task_failed(task, result, graph)

        metrics = monitor.get_metrics()
        assert metrics.failed_tasks == 1

    @pytest.mark.asyncio
    async def test_reset_clears_state(self, monitor: DefaultExecutionMonitor) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        monitor.record_task_pending(task)
        assert monitor.get_metrics().scheduled_tasks > 0
        monitor.reset()
        assert monitor.get_metrics().scheduled_tasks == 0

    @pytest.mark.asyncio
    async def test_get_status_summary_returns_all_states(
        self, monitor: DefaultExecutionMonitor,
    ) -> None:
        summary = monitor.get_status_summary()
        for status in TaskExecutionStatus:
            assert status.value in summary
            assert summary[status.value] >= 0


# ─────────────────────────────────────────────────────────────────────────────
# Retry Manager
# ─────────────────────────────────────────────────────────────────────────────


class TestRetryManager:
    @pytest.mark.asyncio
    async def test_never_retry(self, retry_manager: DefaultRetryManager) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.NEVER,
            retry_count=0,
        )
        assert await retry_manager.should_retry(task) is False

    @pytest.mark.asyncio
    async def test_immediate_retry(self, retry_manager: DefaultRetryManager) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.IMMEDIATE,
            retry_count=0,
        )
        assert await retry_manager.should_retry(task) is True

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, retry_manager: DefaultRetryManager) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.IMMEDIATE,
            retry_count=3,
        )
        # IMMEDIATE max retries = 3, retry_count = 3 means exhausted
        assert await retry_manager.should_retry(task) is False

    @pytest.mark.asyncio
    async def test_backoff_immediate(self, retry_manager: DefaultRetryManager) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.IMMEDIATE,
        )
        backoff = await retry_manager.get_backoff(task)
        assert backoff == 0.0

    @pytest.mark.asyncio
    async def test_backoff_fixed_delay(
        self, retry_manager: DefaultRetryManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.FIXED_DELAY,
        )
        backoff = await retry_manager.get_backoff(task)
        assert backoff == 1.0

    @pytest.mark.asyncio
    async def test_backoff_exponential(
        self, retry_manager: DefaultRetryManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.EXPONENTIAL_BACKOFF,
            retry_count=1,
        )
        backoff = await retry_manager.get_backoff(task)
        assert backoff == 1.0  # 1.0 * 2^(1-1) = 1.0

    @pytest.mark.asyncio
    async def test_backoff_exponential_capped(
        self, retry_manager: DefaultRetryManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.EXPONENTIAL_BACKOFF,
            retry_count=10,
        )
        backoff = await retry_manager.get_backoff(task)
        assert backoff == 60.0  # capped at max_backoff

    @pytest.mark.asyncio
    async def test_retry_tracks_count(
        self, retry_manager: DefaultRetryManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            retry_policy=RetryPolicy.EXPONENTIAL_BACKOFF,
            retry_count=0,
        )
        assert await retry_manager.should_retry(task) is True
        task.retry_count = 1
        assert await retry_manager.should_retry(task) is True
        task.retry_count = 5
        # EXPONENTIAL max retries = 5
        assert await retry_manager.should_retry(task) is False


# ─────────────────────────────────────────────────────────────────────────────
# Approval Manager
# ─────────────────────────────────────────────────────────────────────────────


class TestApprovalManager:
    @pytest.mark.asyncio
    async def test_auto_approve(
        self, approval_manager: PlaceholderApprovalManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Auto",
            execution_metadata={"requires_human_approval": False},
        )
        assert await approval_manager.request_approval(task) is True

    @pytest.mark.asyncio
    async def test_approval_required(
        self, approval_manager: PlaceholderApprovalManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Requires Approval",
            execution_metadata={"requires_human_approval": True},
        )
        assert await approval_manager.request_approval(task) is False

    @pytest.mark.asyncio
    async def test_default_no_approval(
        self, approval_manager: PlaceholderApprovalManager,
    ) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="Default")
        assert await approval_manager.request_approval(task) is True

    @pytest.mark.asyncio
    async def test_approval_skipped_for_internal_tasks(
        self, approval_manager: PlaceholderApprovalManager,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Internal",
            execution_metadata={},
        )
        assert await approval_manager.request_approval(task) is True


# ─────────────────────────────────────────────────────────────────────────────
# Execution Dispatcher
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.usefixtures("monitor")
class TestExecutionDispatcher:
    @pytest.mark.asyncio
    async def test_execute_task_success(
        self,
        execution_dispatcher: DefaultExecutionDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Success Task",
            execution_metadata={"requires_human_approval": False},
        )
        graph = WorkflowGraph()
        graph.add_node(task)
        result, traces = await execution_dispatcher.execute(task, graph)
        assert result.success is True
        assert len(traces) == 2  # dispatcher + approval

    @pytest.mark.asyncio
    async def test_execute_dispatches_and_runs(
        self,
        execution_dispatcher: DefaultExecutionDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Runnable",
            execution_metadata={
                "requires_human_approval": False,
                "required_capability": "database",
            },
        )
        graph = WorkflowGraph()
        graph.add_node(task)
        result, traces = await execution_dispatcher.execute(task, graph)
        assert result.success is True
        assert task.assigned_executor == "db_agent"
        assert task.runtime_status == TaskExecutionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_approval_required_raises(
        self,
        execution_dispatcher: DefaultExecutionDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Needs Approval",
            execution_metadata={"requires_human_approval": True},
        )
        graph = WorkflowGraph()
        graph.add_node(task)
        with pytest.raises(Exception, match="approval"):
            await execution_dispatcher.execute(task, graph)
        assert task.runtime_status == TaskExecutionStatus.WAITING

    @pytest.mark.asyncio
    async def test_traces_recorded(
        self,
        execution_dispatcher: DefaultExecutionDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Traced Task",
            execution_metadata={"requires_human_approval": False},
        )
        graph = WorkflowGraph()
        graph.add_node(task)
        _result, traces = await execution_dispatcher.execute(task, graph)
        assert len(traces) >= 2
        stage_names = [t.stage_name for t in traces]
        assert "task_dispatcher" in stage_names
        assert "approval_manager" in stage_names

    @pytest.mark.asyncio
    async def test_traces_have_duration(
        self,
        execution_dispatcher: DefaultExecutionDispatcher,
    ) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Duration",
            execution_metadata={"requires_human_approval": False},
        )
        graph = WorkflowGraph()
        graph.add_node(task)
        _result, traces = await execution_dispatcher.execute(task, graph)
        for trace in traces:
            assert trace.duration_ms is not None
            assert trace.duration_ms >= 0


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowMetrics (expanded)
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowMetrics:
    def test_new_fields_exist(self) -> None:
        from adip.workflow.contracts.models import WorkflowMetrics as WM

        metrics = WM()
        assert hasattr(metrics, "scheduled_tasks")
        assert hasattr(metrics, "executed_tasks")
        assert hasattr(metrics, "retry_attempts")
        assert hasattr(metrics, "parallel_groups")
        assert hasattr(metrics, "waiting_tasks")
        assert hasattr(metrics, "approval_requests")
        assert hasattr(metrics, "total_runtime")

    def test_default_values(self) -> None:
        from adip.workflow.contracts.models import WorkflowMetrics as WM

        metrics = WM()
        assert metrics.scheduled_tasks == 0
        assert metrics.executed_tasks == 0
        assert metrics.retry_attempts == 0
        assert metrics.parallel_groups == 0
        assert metrics.waiting_tasks == 0
        assert metrics.approval_requests == 0
        assert metrics.total_runtime == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Interface compliance (all components implement their interfaces)
# ─────────────────────────────────────────────────────────────────────────────


class TestInterfaceCompliance:
    def test_graph_builder_is_instance(self) -> None:
        assert isinstance(DefaultGraphBuilder(), GraphBuilder)

    def test_scheduler_is_instance(self) -> None:
        assert isinstance(DefaultScheduler(), TaskScheduler)

    def test_dispatcher_is_instance(self) -> None:
        assert isinstance(PlaceholderDispatcher(), object)

    def test_retry_manager_is_instance(self) -> None:
        retry = DefaultRetryManager()
        from adip.workflow.interfaces import RetryManager
        assert isinstance(retry, RetryManager)

    def test_approval_manager_is_instance(self) -> None:
        ap = PlaceholderApprovalManager()
        from adip.workflow.interfaces import ApprovalManager
        assert isinstance(ap, ApprovalManager)

    def test_executor_conforms_to_protocol(self) -> None:
        from adip.workflow.interfaces import AgentExecutor
        executor = PlaceholderExecutor()
        assert isinstance(executor, AgentExecutor)
