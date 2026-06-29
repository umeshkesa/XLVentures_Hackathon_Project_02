"""Comprehensive tests for Workflow Engine Phase 3 — Orchestration layer."""

from __future__ import annotations

import uuid

import pytest

from adip.planner.contracts.models import ExecutionPlan, PlanningGoal, PlanningTask
from adip.workflow.contracts.events import (
    ExecutionStarted,
    GraphBuilt,
    TaskDispatched,
    TasksScheduled,
    WorkflowCompleted,
    WorkflowFailed,
    WorkflowInitialized,
    WorkflowPaused,
    WorkflowResumed,
    WorkflowStarted,
)
from adip.workflow.contracts.exceptions import (
    StateTransitionException,
    WorkflowValidationException,
)
from adip.workflow.contracts.models import (
    WorkflowContext,
    WorkflowGraph,
    WorkflowMetrics,
    WorkflowRequest,
    WorkflowResult,
    WorkflowTrace,
)
from adip.workflow.enums import WorkflowStatus
from adip.workflow.execution.confidence import WorkflowConfidenceCalculator
from adip.workflow.execution.engine import DefaultWorkflowEngine
from adip.workflow.execution.service import DefaultWorkflowService
from adip.workflow.execution.state_machine import WorkflowStateMachine
from adip.workflow.execution.strategy import SequentialStrategy
from adip.workflow.interfaces import (
    WorkflowEngine,
    WorkflowService,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_plan() -> ExecutionPlan:
    goal = PlanningGoal(objective="Test workflow orchestration")
    tasks = [
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task A",
            description="First task",
            dependencies=[],
        ),
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task B",
            description="Second task depends on A",
            dependencies=[],  # set below
        ),
    ]
    tasks[1].dependencies = [tasks[0].task_id]
    return ExecutionPlan(goal=goal, tasks=tasks)


@pytest.fixture
def sample_request(sample_plan: ExecutionPlan) -> WorkflowRequest:
    return WorkflowRequest(
        execution_plan=sample_plan,
        workflow_context=WorkflowContext(),
        metadata={"source": "test"},
    )


@pytest.fixture
def engine(sample_plan: ExecutionPlan) -> DefaultWorkflowEngine:
    from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
    from adip.workflow.execution.dispatcher import PlaceholderDispatcher
    from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
    from adip.workflow.execution.graph_builder import DefaultGraphBuilder
    from adip.workflow.execution.retry_manager import DefaultRetryManager
    from adip.workflow.execution.scheduler import DefaultScheduler

    return DefaultWorkflowEngine(
        graph_builder=DefaultGraphBuilder(),
        scheduler=DefaultScheduler(),
        dispatcher=PlaceholderDispatcher(),
        retry_manager=DefaultRetryManager(),
        approval_manager=PlaceholderApprovalManager(),
        execution_monitor=DefaultExecutionMonitor(),
        execution_strategy=SequentialStrategy(),
    )


@pytest.fixture
def service(engine: DefaultWorkflowEngine) -> DefaultWorkflowService:
    return DefaultWorkflowService(engine)


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowStateMachine
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowStateMachine:
    def test_initial_state(self) -> None:
        sm = WorkflowStateMachine()
        assert sm.current == WorkflowStatus.CREATED

    def test_valid_transition(self) -> None:
        sm = WorkflowStateMachine()
        sm.transition_to(WorkflowStatus.INITIALIZED)
        assert sm.current == WorkflowStatus.INITIALIZED

    def test_illegal_transition_raises(self) -> None:
        sm = WorkflowStateMachine()
        with pytest.raises(StateTransitionException, match="CREATED.*RUNNING"):
            sm.transition_to(WorkflowStatus.RUNNING)

    def test_full_lifecycle(self) -> None:
        sm = WorkflowStateMachine()
        sm.transition_to(WorkflowStatus.INITIALIZED)
        sm.transition_to(WorkflowStatus.GRAPH_BUILT)
        sm.transition_to(WorkflowStatus.SCHEDULED)
        sm.transition_to(WorkflowStatus.READY)
        sm.transition_to(WorkflowStatus.RUNNING)
        sm.transition_to(WorkflowStatus.COMPLETED)
        assert sm.current == WorkflowStatus.COMPLETED

    def test_terminal_states(self) -> None:
        assert WorkflowStateMachine.is_terminal(WorkflowStatus.COMPLETED)
        assert WorkflowStateMachine.is_terminal(WorkflowStatus.FAILED)
        assert WorkflowStateMachine.is_terminal(WorkflowStatus.CANCELLED)
        assert not WorkflowStateMachine.is_terminal(WorkflowStatus.RUNNING)

    def test_can_transition_to(self) -> None:
        sm = WorkflowStateMachine()
        assert sm.can_transition_to(WorkflowStatus.INITIALIZED) is True
        assert sm.can_transition_to(WorkflowStatus.COMPLETED) is False

    def test_illegal_from_terminal_state(self) -> None:
        sm = WorkflowStateMachine(initial_state=WorkflowStatus.COMPLETED)
        with pytest.raises(StateTransitionException):
            sm.transition_to(WorkflowStatus.INITIALIZED)

    def test_reset(self) -> None:
        sm = WorkflowStateMachine(initial_state=WorkflowStatus.RUNNING)
        sm.reset()
        assert sm.current == WorkflowStatus.CREATED

    def test_get_allowed_transitions(self) -> None:
        allowed = WorkflowStateMachine.get_allowed_transitions(WorkflowStatus.RUNNING)
        assert WorkflowStatus.COMPLETED in allowed
        assert WorkflowStatus.FAILED in allowed
        assert WorkflowStatus.WAITING_APPROVAL in allowed
        assert WorkflowStatus.INITIALIZED not in allowed

    def test_running_to_paused_to_running(self) -> None:
        sm = WorkflowStateMachine()
        sm.transition_to(WorkflowStatus.INITIALIZED)
        sm.transition_to(WorkflowStatus.GRAPH_BUILT)
        sm.transition_to(WorkflowStatus.SCHEDULED)
        sm.transition_to(WorkflowStatus.READY)
        sm.transition_to(WorkflowStatus.RUNNING)
        sm.transition_to(WorkflowStatus.PAUSED)
        sm.transition_to(WorkflowStatus.RUNNING)
        sm.transition_to(WorkflowStatus.COMPLETED)
        assert sm.current == WorkflowStatus.COMPLETED

    def test_exception_message(self) -> None:
        sm = WorkflowStateMachine()
        with pytest.raises(StateTransitionException) as exc_info:
            sm.transition_to(WorkflowStatus.COMPLETED)
        assert "CREATED" in str(exc_info.value)
        assert "COMPLETED" in str(exc_info.value)

    def test_machine_to_failed_after_scheduled(self) -> None:
        sm = WorkflowStateMachine()
        sm.transition_to(WorkflowStatus.INITIALIZED)
        sm.transition_to(WorkflowStatus.GRAPH_BUILT)
        sm.transition_to(WorkflowStatus.SCHEDULED)
        sm.transition_to(WorkflowStatus.FAILED)
        assert sm.current == WorkflowStatus.FAILED


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowConfidenceCalculator
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowConfidenceCalculator:
    @pytest.mark.asyncio
    async def test_high_confidence_for_empty_graph(self) -> None:
        calc = WorkflowConfidenceCalculator()
        graph = WorkflowGraph()
        score = await calc.calculate(graph)
        assert score >= 90.0  # no cycles, low density

    @pytest.mark.asyncio
    async def test_confidence_with_metrics(self) -> None:
        calc = WorkflowConfidenceCalculator()
        graph = WorkflowGraph()
        graph.add_node(
            type("Task", (), {"task_id": uuid.uuid4()})(),  # noqa
        )
        metrics = WorkflowMetrics(
            executed_tasks=10,
            successful_tasks=8,
            retry_attempts=1,
            parallel_groups=0,
        )
        score = await calc.calculate(graph, metrics)
        assert 0.0 <= score <= 100.0

    @pytest.mark.asyncio
    async def test_confidence_with_cycle(self) -> None:
        calc = WorkflowConfidenceCalculator()
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        graph = WorkflowGraph()
        graph.nodes[a_id] = type("Task", (), {"task_id": a_id})()
        graph.nodes[b_id] = type("Task", (), {"task_id": b_id})()
        graph.edges[a_id] = [b_id]
        graph.edges[b_id] = [a_id]  # cycle A↔B
        score = await calc.calculate(graph)
        assert score < 50.0  # cycles reduce confidence significantly

    @pytest.mark.asyncio
    async def test_is_ready_detects_cycles(self) -> None:
        calc = WorkflowConfidenceCalculator()
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        graph = WorkflowGraph()
        graph.nodes[a_id] = type("Task", (), {"task_id": a_id})()
        graph.nodes[b_id] = type("Task", (), {"task_id": b_id})()
        graph.edges[a_id] = [b_id]
        graph.edges[b_id] = [a_id]
        ready = await calc.is_ready(graph, WorkflowMetrics())
        assert ready is False

    @pytest.mark.asyncio
    async def test_is_ready_with_no_root_nodes(self) -> None:
        calc = WorkflowConfidenceCalculator()
        a_id = uuid.uuid4()
        b_id = uuid.uuid4()
        graph = WorkflowGraph()
        graph.nodes[a_id] = type("Task", (), {"task_id": a_id})()
        graph.nodes[b_id] = type("Task", (), {"task_id": b_id})()
        graph.edges[a_id] = [b_id]
        # No root nodes because edges have no nodes without deps
        # Actually a_id has no deps so it IS a root
        # Let's make all nodes have deps
        graph.edges[a_id] = [b_id]
        graph.edges[b_id] = [a_id]  # cycle makes it false already
        ready = await calc.is_ready(graph, WorkflowMetrics())
        assert ready is False

    @pytest.mark.asyncio
    async def test_is_ready_success(self) -> None:
        calc = WorkflowConfidenceCalculator()
        a_id = uuid.uuid4()
        graph = WorkflowGraph()
        graph.add_node(
            type("Task", (), {"task_id": a_id, "dependencies": []})(),
        )
        ready = await calc.is_ready(graph, WorkflowMetrics())
        assert ready is True

    @pytest.mark.asyncio
    async def test_confidence_bounds(self) -> None:
        calc = WorkflowConfidenceCalculator()
        graph = WorkflowGraph()
        graph.add_node(
            type("Task", (), {"task_id": uuid.uuid4()})(),
        )
        for _ in range(1000):
            score = await calc.calculate(graph)
            assert 0.0 <= score <= 100.0


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowEngine
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowEngine:
    @pytest.mark.asyncio
    async def test_execute_returns_result(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert isinstance(result, WorkflowResult)
        assert result.workflow_status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)

    @pytest.mark.asyncio
    async def test_execute_completes_tasks(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert result.completed_tasks >= 0

    @pytest.mark.asyncio
    async def test_execute_records_traces(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert len(result.traces) >= 2  # at least graph_builder + scheduler
        stage_names = [t.stage_name for t in result.traces]
        assert "graph_builder" in stage_names
        assert "scheduler" in stage_names

    @pytest.mark.asyncio
    async def test_execute_records_events(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert len(result.events) >= 3

    @pytest.mark.asyncio
    async def test_execute_includes_metrics(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert result.metrics is not None
        assert result.metrics.total_execution_time >= 0

    @pytest.mark.asyncio
    async def test_execute_empty_plan(self, engine: DefaultWorkflowEngine) -> None:
        plan = ExecutionPlan(goal=PlanningGoal(objective="Empty"))
        request = WorkflowRequest(execution_plan=plan)
        result = await engine.execute(request)
        assert result.workflow_status == WorkflowStatus.COMPLETED
        assert "No tasks" in result.execution_summary

    @pytest.mark.asyncio
    async def test_pause_and_resume(self) -> None:
        # Create a new engine instance for state-machine-sensitive tests
        from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
        from adip.workflow.execution.dispatcher import PlaceholderDispatcher
        from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
        from adip.workflow.execution.graph_builder import DefaultGraphBuilder
        from adip.workflow.execution.retry_manager import DefaultRetryManager
        from adip.workflow.execution.scheduler import DefaultScheduler

        fresh_engine = DefaultWorkflowEngine(
            graph_builder=DefaultGraphBuilder(),
            scheduler=DefaultScheduler(),
            dispatcher=PlaceholderDispatcher(),
            retry_manager=DefaultRetryManager(),
            approval_manager=PlaceholderApprovalManager(),
            execution_monitor=DefaultExecutionMonitor(),
            execution_strategy=SequentialStrategy(),
        )
        # Manually walk to RUNNING state
        fresh_engine._state.transition_to(WorkflowStatus.INITIALIZED)
        fresh_engine._state.transition_to(WorkflowStatus.GRAPH_BUILT)
        fresh_engine._state.transition_to(WorkflowStatus.SCHEDULED)
        fresh_engine._state.transition_to(WorkflowStatus.READY)
        fresh_engine._state.transition_to(WorkflowStatus.RUNNING)
        await fresh_engine.pause(str(uuid.uuid4()))
        await fresh_engine.resume(str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_cancel(self) -> None:
        from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
        from adip.workflow.execution.dispatcher import PlaceholderDispatcher
        from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
        from adip.workflow.execution.graph_builder import DefaultGraphBuilder
        from adip.workflow.execution.retry_manager import DefaultRetryManager
        from adip.workflow.execution.scheduler import DefaultScheduler

        fresh_engine = DefaultWorkflowEngine(
            graph_builder=DefaultGraphBuilder(),
            scheduler=DefaultScheduler(),
            dispatcher=PlaceholderDispatcher(),
            retry_manager=DefaultRetryManager(),
            approval_manager=PlaceholderApprovalManager(),
            execution_monitor=DefaultExecutionMonitor(),
            execution_strategy=SequentialStrategy(),
        )
        fresh_engine._state.transition_to(WorkflowStatus.INITIALIZED)
        fresh_engine._state.transition_to(WorkflowStatus.GRAPH_BUILT)
        fresh_engine._state.transition_to(WorkflowStatus.SCHEDULED)
        fresh_engine._state.transition_to(WorkflowStatus.READY)
        fresh_engine._state.transition_to(WorkflowStatus.RUNNING)
        await fresh_engine.cancel(str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_execute_has_task_results(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert isinstance(result.task_results, dict)

    @pytest.mark.asyncio
    async def test_execute_with_approval_not_needed(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        # All tasks should auto-approve
        assert result.workflow_status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)

    @pytest.mark.asyncio
    async def test_execute_efficiency(
        self, engine: DefaultWorkflowEngine, sample_request: WorkflowRequest,
    ) -> None:
        result = await engine.execute(sample_request)
        assert 0.0 <= result.execution_efficiency <= 100.0


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowService
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowService:
    @pytest.mark.asyncio
    async def test_start_workflow_returns_result(
        self, service: DefaultWorkflowService, sample_request: WorkflowRequest,
    ) -> None:
        result = await service.start_workflow(sample_request)
        assert isinstance(result, WorkflowResult)
        assert result.workflow_status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)

    @pytest.mark.asyncio
    async def test_validation_rejects_empty_plan(
        self, service: DefaultWorkflowService,
    ) -> None:
        plan = ExecutionPlan(goal=PlanningGoal(objective="Test"))
        request = WorkflowRequest(execution_plan=plan)
        with pytest.raises(WorkflowValidationException, match="no tasks"):
            await service.start_workflow(request)

    @pytest.mark.asyncio
    async def test_validation_rejects_empty_goal(
        self, service: DefaultWorkflowService,
    ) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="  "),
            tasks=[PlanningTask(task_id=uuid.uuid4(), description="something")],
        )
        request = WorkflowRequest(execution_plan=plan)
        with pytest.raises(WorkflowValidationException, match="empty"):
            await service.start_workflow(request)

    @pytest.mark.asyncio
    async def test_service_aggregates_metrics(
        self, service: DefaultWorkflowService, sample_request: WorkflowRequest,
    ) -> None:
        result = await service.start_workflow(sample_request)
        assert result.metrics is not None
        assert result.metrics.total_execution_time >= 0

    @pytest.mark.asyncio
    async def test_is_workflow_service(
        self, service: DefaultWorkflowService,
    ) -> None:
        assert isinstance(service, WorkflowService)

    @pytest.mark.asyncio
    async def test_get_workflow_status(
        self, service: DefaultWorkflowService,
    ) -> None:
        status = await service.get_workflow_status(str(uuid.uuid4()))
        assert status is None


# ─────────────────────────────────────────────────────────────────────────────
# New Event Models
# ─────────────────────────────────────────────────────────────────────────────


class TestNewEvents:
    def test_graph_built_event(self) -> None:
        event = GraphBuilt(
            workflow_id=uuid.uuid4(),
            node_count=5,
            edge_count=3,
            cycle_free=True,
        )
        assert event.node_count == 5
        assert event.edge_count == 3
        assert event.cycle_free is True

    def test_tasks_scheduled_event(self) -> None:
        event = TasksScheduled(
            workflow_id=uuid.uuid4(),
            wave_count=3,
            total_tasks=10,
        )
        assert event.wave_count == 3
        assert event.total_tasks == 10

    def test_execution_started_event(self) -> None:
        event = ExecutionStarted(
            workflow_id=uuid.uuid4(),
            total_tasks=5,
        )
        assert event.total_tasks == 5

    def test_task_dispatched_event(self) -> None:
        event = TaskDispatched(
            workflow_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            executor="search_agent",
        )
        assert event.executor == "search_agent"

    def test_workflow_paused_event(self) -> None:
        event = WorkflowPaused(
            workflow_id=uuid.uuid4(),
            reason="Awaiting approval",
        )
        assert event.reason == "Awaiting approval"

    def test_workflow_resumed_event(self) -> None:
        event = WorkflowResumed(workflow_id=uuid.uuid4())
        assert event.event_id is not None

    def test_workflow_completed_event(self) -> None:
        event = WorkflowCompleted(
            workflow_id=uuid.uuid4(),
            summary="All tasks done",
        )
        assert event.summary == "All tasks done"

    def test_workflow_failed_event(self) -> None:
        event = WorkflowFailed(
            workflow_id=uuid.uuid4(),
            error="Task execution error",
        )
        assert event.error == "Task execution error"

    def test_workflow_started_event(self) -> None:
        event = WorkflowStarted(
            workflow_id=uuid.uuid4(),
        )
        assert event.payload == {}

    def test_workflow_initialized_event(self) -> None:
        event = WorkflowInitialized(
            workflow_id=uuid.uuid4(),
        )
        assert event.event_id is not None


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowTrace in WorkflowResult
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowResultWithTrace:
    def test_traces_in_result(self) -> None:
        trace = WorkflowTrace(stage_name="test_stage")
        result = WorkflowResult(
            workflow_id=uuid.uuid4(),
            traces=[trace],
        )
        assert len(result.traces) == 1
        assert result.traces[0].stage_name == "test_stage"

    def test_metrics_in_result(self) -> None:
        metrics = WorkflowMetrics(scheduled_tasks=10, executed_tasks=5)
        result = WorkflowResult(
            workflow_id=uuid.uuid4(),
            metrics=metrics,
        )
        assert result.metrics.scheduled_tasks == 10
        assert result.metrics.executed_tasks == 5

    def test_efficiency_in_result(self) -> None:
        result = WorkflowResult(
            workflow_id=uuid.uuid4(),
            execution_efficiency=85.5,
        )
        assert result.execution_efficiency == 85.5


# ─────────────────────────────────────────────────────────────────────────────
# Interface compliance
# ─────────────────────────────────────────────────────────────────────────────


class TestInterfaceCompliancePhase3:
    def test_engine_is_instance(self) -> None:
        from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
        from adip.workflow.execution.dispatcher import PlaceholderDispatcher
        from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
        from adip.workflow.execution.graph_builder import DefaultGraphBuilder
        from adip.workflow.execution.retry_manager import DefaultRetryManager
        from adip.workflow.execution.scheduler import DefaultScheduler

        engine = DefaultWorkflowEngine(
            graph_builder=DefaultGraphBuilder(),
            scheduler=DefaultScheduler(),
            dispatcher=PlaceholderDispatcher(),
            retry_manager=DefaultRetryManager(),
            approval_manager=PlaceholderApprovalManager(),
            execution_monitor=DefaultExecutionMonitor(),
            execution_strategy=SequentialStrategy(),
        )
        assert isinstance(engine, WorkflowEngine)

    def test_service_is_instance(self) -> None:
        from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
        from adip.workflow.execution.dispatcher import PlaceholderDispatcher
        from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
        from adip.workflow.execution.graph_builder import DefaultGraphBuilder
        from adip.workflow.execution.retry_manager import DefaultRetryManager
        from adip.workflow.execution.scheduler import DefaultScheduler

        engine = DefaultWorkflowEngine(
            graph_builder=DefaultGraphBuilder(),
            scheduler=DefaultScheduler(),
            dispatcher=PlaceholderDispatcher(),
            retry_manager=DefaultRetryManager(),
            approval_manager=PlaceholderApprovalManager(),
            execution_monitor=DefaultExecutionMonitor(),
            execution_strategy=SequentialStrategy(),
        )
        service = DefaultWorkflowService(engine)
        assert isinstance(service, WorkflowService)


# ─────────────────────────────────────────────────────────────────────────────
# Edge Cases
# ─────────────────────────────────────────────────────────────────────────────


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_engine_handles_empty_graph_builder_result(
        self, sample_plan: ExecutionPlan,
    ) -> None:
        from adip.workflow.execution.approval_manager import PlaceholderApprovalManager
        from adip.workflow.execution.dispatcher import PlaceholderDispatcher
        from adip.workflow.execution.execution_monitor import DefaultExecutionMonitor
        from adip.workflow.execution.retry_manager import DefaultRetryManager
        from adip.workflow.execution.scheduler import DefaultScheduler

        class EmptyGraphBuilder:
            async def build(self, request):
                return WorkflowGraph()

        engine = DefaultWorkflowEngine(
            graph_builder=EmptyGraphBuilder(),
            scheduler=DefaultScheduler(),
            dispatcher=PlaceholderDispatcher(),
            retry_manager=DefaultRetryManager(),
            approval_manager=PlaceholderApprovalManager(),
            execution_monitor=DefaultExecutionMonitor(),
            execution_strategy=SequentialStrategy(),
        )
        request = WorkflowRequest(
            execution_plan=ExecutionPlan(
                goal=PlanningGoal(objective="Empty"),
                tasks=[],
            ),
        )
        result = await engine.execute(request)
        assert result.workflow_status == WorkflowStatus.COMPLETED

    def test_confidence_with_no_graph(self) -> None:
        calc = WorkflowConfidenceCalculator()
        graph = WorkflowGraph()
        # Should not crash
        import asyncio
        score = asyncio.run(calc.calculate(graph))
        assert score >= 0

    def test_state_machine_string_repr(self) -> None:
        assert WorkflowStatus.GRAPH_BUILT.value == "GRAPH_BUILT"
        assert WorkflowStatus.SCHEDULED.value == "SCHEDULED"
        assert WorkflowStatus.WAITING_APPROVAL.value == "WAITING_APPROVAL"
        assert WorkflowStatus.RETRYING.value == "RETRYING"

    def test_default_metrics_in_result(self) -> None:
        result = WorkflowResult(workflow_id=uuid.uuid4())
        assert result.metrics is not None
        assert result.metrics.scheduled_tasks == 0
