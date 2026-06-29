"""Comprehensive tests for Workflow Engine Phase 3.5 — Enterprise Refinement.

Covers: WorkflowPolicy, WorkflowDecision, WorkflowGraph enhancements,
new strategy placeholders, enhanced Trace/Metrics/Events, extension
point hooks, and backward compatibility.
"""

from __future__ import annotations

import uuid

import pytest

from adip.planner.contracts.models import ExecutionPlan, PlanningGoal, PlanningTask
from adip.workflow.contracts.events import (
    EVENT_VERSION,
    ExecutionStarted,
    GraphBuilt,
    TaskCompleted,
    WorkflowCompleted,
    WorkflowFailed,
    WorkflowStarted,
)
from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowDecision,
    WorkflowGraph,
    WorkflowMetrics,
    WorkflowPolicy,
    WorkflowRequest,
    WorkflowResult,
    WorkflowTask,
    WorkflowTrace,
)
from adip.workflow.execution.engine import DefaultWorkflowEngine
from adip.workflow.execution.service import DefaultWorkflowService
from adip.workflow.execution.strategy import (
    ConditionalStrategy,
    EmergencyStrategy,
    ExecutionStrategy,
    ParallelStrategy,
    SequentialStrategy,
)
from adip.workflow.interfaces import (
    ActionEngineHook,
    DecisionReviewLayerHook,
    EvidenceFusionHook,
    KnowledgeManagerHook,
    MemoryManagerHook,
    RuleManagerHook,
)

# ─────────────────────────────────────────────────────────────────────────────
# WorkflowPolicy
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowPolicy:
    def test_default_policy(self) -> None:
        p = WorkflowPolicy()
        assert p.max_parallel_tasks == 1
        assert p.retry_limit == 3
        assert p.timeout_policy == "fail"
        assert p.approval_policy == "auto_approve"
        assert p.failure_policy == "continue"
        assert p.execution_mode == "sequential"
        assert p.compensation_enabled is False

    def test_custom_policy(self) -> None:
        p = WorkflowPolicy(
            max_parallel_tasks=5,
            retry_limit=10,
            timeout_policy="retry",
            approval_policy="require_approval",
            failure_policy="abort",
            execution_mode="parallel",
            compensation_enabled=True,
        )
        assert p.max_parallel_tasks == 5
        assert p.retry_limit == 10
        assert p.timeout_policy == "retry"
        assert p.approval_policy == "require_approval"
        assert p.failure_policy == "abort"
        assert p.execution_mode == "parallel"
        assert p.compensation_enabled is True

    def test_policy_validation_max_parallel_ge_1(self) -> None:
        with pytest.raises(ValueError):
            WorkflowPolicy(max_parallel_tasks=0)

    def test_policy_validation_retry_limit_ge_0(self) -> None:
        p = WorkflowPolicy(retry_limit=0)
        assert p.retry_limit == 0

    def test_policy_serialisation(self) -> None:
        p = WorkflowPolicy(retry_limit=5, failure_policy="abort")
        data = p.model_dump()
        assert data["retry_limit"] == 5
        assert data["failure_policy"] == "abort"

    def test_policy_deserialisation(self) -> None:
        data = {"max_parallel_tasks": 3, "retry_limit": 2}
        p = WorkflowPolicy(**data)
        assert p.max_parallel_tasks == 3
        assert p.retry_limit == 2

    def test_policy_in_request(self) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="test"),
            tasks=[PlanningTask(task_id=uuid.uuid4(), task_name="T", description="")],
        )
        policy = WorkflowPolicy(failure_policy="abort")
        req = WorkflowRequest(execution_plan=plan, policy=policy)
        assert req.policy.failure_policy == "abort"

    def test_policy_default_in_request(self) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="test"),
            tasks=[PlanningTask(task_id=uuid.uuid4(), task_name="T", description="")],
        )
        req = WorkflowRequest(execution_plan=plan)
        assert isinstance(req.policy, WorkflowPolicy)
        assert req.policy.retry_limit == 3


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowDecision
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowDecision:
    def test_decision_creation(self) -> None:
        d = WorkflowDecision(
            decision_type="strategy",
            reason="Selected SequentialStrategy for linear graph",
            evidence={"graph_size": 3},
            selected_strategy="SequentialStrategy",
            alternatives=["ParallelStrategy"],
        )
        assert d.decision_type == "strategy"
        assert "SequentialStrategy" in d.reason
        assert d.evidence["graph_size"] == 3
        assert d.selected_strategy == "SequentialStrategy"
        assert "ParallelStrategy" in d.alternatives

    def test_decision_defaults(self) -> None:
        d = WorkflowDecision(decision_type="retry")
        assert d.reason == ""
        assert d.evidence == {}
        assert d.selected_strategy is None
        assert d.alternatives == []

    def test_decision_id_unique(self) -> None:
        d1 = WorkflowDecision(decision_type="a")
        d2 = WorkflowDecision(decision_type="a")
        assert d1.decision_id != d2.decision_id

    def test_decision_timestamp_set(self) -> None:
        d = WorkflowDecision(decision_type="skip")
        assert d.timestamp is not None

    def test_decision_in_result(self) -> None:
        d = WorkflowDecision(decision_type="approval", reason="Auto-approved")
        result = WorkflowResult(decisions=[d])
        assert len(result.decisions) == 1
        assert result.decisions[0].decision_type == "approval"


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowGraph enhancements (validate, detect_orphans, get_critical_path,
# get_leaf_nodes)
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowGraphValidate:
    def test_valid_linear_graph(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        assert graph.validate() == []

    def test_missing_dependency(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        missing = uuid.uuid4()
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[missing])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        errors = graph.validate()
        assert any("missing" in e for e in errors)

    def test_cycle_detected(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        t1.dependencies = [t2.task_id]
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        errors = graph.validate()
        assert any("cycle" in e for e in errors)

    def test_orphan_detected(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="Orphan")
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        errors = graph.validate()
        assert any("orphan" in e for e in errors)

    def test_empty_graph_valid(self) -> None:
        graph = WorkflowGraph()
        assert graph.validate() == []

    def test_single_node_is_orphan(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Only")
        graph = WorkflowGraph.from_workflow_tasks([t1])
        errors = graph.validate()
        assert any("orphan" in e for e in errors)


class TestWorkflowGraphDetectOrphans:
    def test_no_orphans_in_linear_graph(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        assert graph.detect_orphans() == []

    def test_single_orphan(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Connected")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="Orphan")
        t1.dependencies = []  # root
        graph = WorkflowGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge(t2.task_id, t1.task_id)  # t2 depends on t1
        # Now t1 has a dependent, t2 has a dep — both connected
        # Let's make a real orphan: a node that has no deps and no dependents
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="RealOrphan")
        graph.add_node(t3)
        orphans = graph.detect_orphans()
        assert t3.task_id in orphans

    def test_all_connected_no_orphans(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t2.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3])
        assert graph.detect_orphans() == []


class TestWorkflowGraphCriticalPath:
    def test_linear_critical_path(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t2.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3])
        path = graph.get_critical_path()
        assert len(path) == 3
        assert path[0].task_id == t1.task_id
        assert path[-1].task_id == t3.task_id

    def test_diamond_critical_path(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Root")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="Left", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="Right", dependencies=[t1.task_id])
        t4 = WorkflowTask(
            task_id=uuid.uuid4(), task_name="Merge",
            dependencies=[t2.task_id, t3.task_id],
        )
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3, t4])
        path = graph.get_critical_path()
        assert len(path) >= 3
        assert path[0].task_id == t1.task_id
        assert path[-1].task_id == t4.task_id

    def test_empty_graph_critical_path(self) -> None:
        graph = WorkflowGraph()
        assert graph.get_critical_path() == []

    def test_single_node_critical_path(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Only")
        graph = WorkflowGraph.from_workflow_tasks([t1])
        path = graph.get_critical_path()
        assert len(path) == 1
        assert path[0].task_id == t1.task_id


class TestWorkflowGraphLeafNodes:
    def test_single_leaf(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        leaves = graph.get_leaf_nodes()
        assert len(leaves) == 1
        assert leaves[0].task_id == t2.task_id

    def test_multiple_leaves(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Root")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="A", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3])
        leaves = graph.get_leaf_nodes()
        assert len(leaves) == 2

    def test_empty_graph_leaves(self) -> None:
        graph = WorkflowGraph()
        assert graph.get_leaf_nodes() == []


# ─────────────────────────────────────────────────────────────────────────────
# ExecutionStrategy placeholders
# ─────────────────────────────────────────────────────────────────────────────


class TestSequentialStrategy:
    @pytest.mark.asyncio
    async def test_linear_schedule(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t2.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3])
        strategy = SequentialStrategy()
        schedule = await strategy.create_schedule(graph)
        assert len(schedule) == 3
        for wave in schedule:
            assert len(wave) == 1

    @pytest.mark.asyncio
    async def test_empty_graph(self) -> None:
        strategy = SequentialStrategy()
        schedule = await strategy.create_schedule(WorkflowGraph())
        assert schedule == []


class TestParallelStrategy:
    @pytest.mark.asyncio
    async def test_parallel_levels(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Root")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="A", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        t4 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3, t4])
        strategy = ParallelStrategy()
        schedule = await strategy.create_schedule(graph)
        assert len(schedule) == 2
        assert len(schedule[0]) == 1  # Root alone
        assert len(schedule[1]) == 3  # A, B, C in one wave

    @pytest.mark.asyncio
    async def test_is_execution_strategy(self) -> None:
        assert isinstance(ParallelStrategy(), ExecutionStrategy)


class TestConditionalStrategy:
    @pytest.mark.asyncio
    async def test_placeholder_returns_sequential(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        strategy = ConditionalStrategy()
        schedule = await strategy.create_schedule(graph)
        assert len(schedule) == 2

    @pytest.mark.asyncio
    async def test_is_execution_strategy(self) -> None:
        assert isinstance(ConditionalStrategy(), ExecutionStrategy)


class TestEmergencyStrategy:
    @pytest.mark.asyncio
    async def test_critical_path_only(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t2.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3])
        strategy = EmergencyStrategy()
        schedule = await strategy.create_schedule(graph)
        assert len(schedule) == 3

    @pytest.mark.asyncio
    async def test_is_execution_strategy(self) -> None:
        assert isinstance(EmergencyStrategy(), ExecutionStrategy)

    @pytest.mark.asyncio
    async def test_empty_graph(self) -> None:
        strategy = EmergencyStrategy()
        schedule = await strategy.create_schedule(WorkflowGraph())
        assert schedule == []


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced WorkflowTrace
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowTraceEnhanced:
    def test_workflow_state_field(self) -> None:
        trace = WorkflowTrace(
            stage_name="test",
            workflow_state="RUNNING",
        )
        assert trace.workflow_state == "RUNNING"

    def test_workflow_state_default(self) -> None:
        trace = WorkflowTrace(stage_name="test")
        assert trace.workflow_state is None

    def test_errors_field(self) -> None:
        trace = WorkflowTrace(stage_name="test", errors=["err1", "err2"], success=False)
        assert len(trace.errors) == 2
        assert not trace.success

    def test_backward_compatible(self) -> None:
        trace = WorkflowTrace(stage_name="legacy")
        assert trace.stage_name == "legacy"
        assert trace.success is True
        assert trace.warnings == []
        assert trace.errors == []


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced WorkflowMetrics
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowMetricsEnhanced:
    def test_scheduling_time(self) -> None:
        m = WorkflowMetrics(scheduling_time=12.5)
        assert m.scheduling_time == 12.5

    def test_retry_time(self) -> None:
        m = WorkflowMetrics(retry_time=5.0)
        assert m.retry_time == 5.0

    def test_idle_time(self) -> None:
        m = WorkflowMetrics(idle_time=3.0)
        assert m.idle_time == 3.0

    def test_execution_efficiency(self) -> None:
        m = WorkflowMetrics(execution_efficiency=85.5)
        assert m.execution_efficiency == 85.5

    def test_workflow_confidence(self) -> None:
        m = WorkflowMetrics(workflow_confidence=92.0)
        assert m.workflow_confidence == 92.0

    def test_new_fields_default_zero(self) -> None:
        m = WorkflowMetrics()
        assert m.scheduling_time == 0.0
        assert m.retry_time == 0.0
        assert m.idle_time == 0.0
        assert m.execution_efficiency == 0.0
        assert m.workflow_confidence == 0.0

    def test_backward_compatible_existing_fields(self) -> None:
        m = WorkflowMetrics(total_execution_time=100.0, executed_tasks=5, successful_tasks=4)
        assert m.total_execution_time == 100.0
        assert m.executed_tasks == 5
        assert m.successful_tasks == 4
        assert m.scheduling_time == 0.0  # new field default

    def test_serialisation_roundtrip(self) -> None:
        original = WorkflowMetrics(
            scheduling_time=1.0,
            retry_time=2.0,
            execution_efficiency=90.0,
            workflow_confidence=95.0,
        )
        data = original.model_dump()
        restored = WorkflowMetrics(**data)
        assert restored.scheduling_time == 1.0
        assert restored.retry_time == 2.0
        assert restored.execution_efficiency == 90.0
        assert restored.workflow_confidence == 95.0


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced Events (execution_plan_id, planner_plan_id, event_version)
# ─────────────────────────────────────────────────────────────────────────────


class TestEnhancedEvents:
    def test_workflow_started_has_plan_id(self) -> None:
        event = WorkflowStarted(
            workflow_id=uuid.uuid4(),
            execution_plan_id="plan-123",
        )
        assert event.execution_plan_id == "plan-123"

    def test_workflow_started_has_event_version(self) -> None:
        event = WorkflowStarted(workflow_id=uuid.uuid4())
        assert event.event_version == EVENT_VERSION

    def test_graph_built_has_plan_id(self) -> None:
        event = GraphBuilt(
            workflow_id=uuid.uuid4(),
            execution_plan_id="plan-456",
        )
        assert event.execution_plan_id == "plan-456"
        assert event.node_count == 0

    def test_task_completed_has_plan_id(self) -> None:
        event = TaskCompleted(
            workflow_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            execution_plan_id="plan-789",
        )
        assert event.execution_plan_id == "plan-789"

    def test_workflow_completed_defaults(self) -> None:
        event = WorkflowCompleted(workflow_id=uuid.uuid4())
        assert event.execution_plan_id == ""
        assert event.event_version == EVENT_VERSION

    def test_workflow_failed_defaults(self) -> None:
        event = WorkflowFailed(workflow_id=uuid.uuid4())
        assert event.execution_plan_id == ""
        assert event.error == ""

    def test_execution_started_new_fields(self) -> None:
        event = ExecutionStarted(
            workflow_id=uuid.uuid4(),
            execution_plan_id="plan-101",
            total_tasks=3,
        )
        assert event.execution_plan_id == "plan-101"
        assert event.total_tasks == 3
        assert event.event_version == EVENT_VERSION

    def test_event_serialisation_roundtrip(self) -> None:
        original = WorkflowStarted(
            workflow_id=uuid.uuid4(),
            execution_plan_id="plan-x",
            planner_plan_id="planner-y",
        )
        data = original.model_dump()
        restored = WorkflowStarted(**data)
        assert restored.execution_plan_id == "plan-x"
        assert restored.planner_plan_id == "planner-y"


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowTask decision_reason
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowTaskDecisionReason:
    def test_decision_reason_field(self) -> None:
        task = WorkflowTask(
            task_id=uuid.uuid4(),
            task_name="Test",
            decision_reason="Scheduled via SequentialStrategy",
        )
        assert task.decision_reason == "Scheduled via SequentialStrategy"

    def test_decision_reason_default_none(self) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="Test")
        assert task.decision_reason is None

    def test_decision_reason_updated(self) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="Test")
        task.decision_reason = "Retry attempt 2/3"
        assert task.decision_reason == "Retry attempt 2/3"


# ─────────────────────────────────────────────────────────────────────────────
# Extension Point Hooks (Protocol compliance)
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryManagerHook:
    @pytest.mark.asyncio
    async def test_concrete_hook(self) -> None:
        class ConcreteHook(MemoryManagerHook):
            async def on_before_task(self, task: WorkflowTask) -> WorkflowTask:
                return task

            async def on_after_task(self, task: WorkflowTask, result: TaskResult) -> None:
                pass

        hook = ConcreteHook()
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="T")
        result = await hook.on_before_task(task)
        assert result.task_id == task.task_id


class TestKnowledgeManagerHook:
    @pytest.mark.asyncio
    async def test_concrete_hook(self) -> None:
        class ConcreteHook(KnowledgeManagerHook):
            async def enrich_context(self, task: WorkflowTask) -> WorkflowTask:
                task.inputs["knowledge"] = "enriched"
                return task

        hook = ConcreteHook()
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="T")
        result = await hook.enrich_context(task)
        assert result.inputs["knowledge"] == "enriched"


class TestRuleManagerHook:
    @pytest.mark.asyncio
    async def test_preconditions(self) -> None:
        class ConcreteHook(RuleManagerHook):
            async def evaluate_preconditions(self, task: WorkflowTask) -> bool:
                return "required_input" in task.inputs

            async def evaluate_postconditions(
                self, task: WorkflowTask, result: TaskResult,
            ) -> bool:
                return result.success

        hook = ConcreteHook()
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="T", inputs={"required_input": "x"})
        assert await hook.evaluate_preconditions(task) is True
        task2 = WorkflowTask(task_id=uuid.uuid4(), task_name="T2")
        assert await hook.evaluate_preconditions(task2) is False


class TestActionEngineHook:
    @pytest.mark.asyncio
    async def test_concrete_hook(self) -> None:
        class ConcreteHook(ActionEngineHook):
            async def execute_action(self, task: WorkflowTask) -> TaskResult:
                return TaskResult(success=True, outputs={"done": True})

        hook = ConcreteHook()
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="T")
        result = await hook.execute_action(task)
        assert result.success is True
        assert result.outputs["done"] is True


class TestDecisionReviewLayerHook:
    @pytest.mark.asyncio
    async def test_concrete_hook(self) -> None:
        class ConcreteHook(DecisionReviewLayerHook):
            async def review_decision(
                self, decision: WorkflowDecision,
            ) -> WorkflowDecision:
                decision.reason = f"Reviewed: {decision.reason}"
                return decision

        hook = ConcreteHook()
        d = WorkflowDecision(decision_type="strategy", reason="original")
        result = await hook.review_decision(d)
        assert "Reviewed: original" in result.reason


class TestEvidenceFusionHook:
    @pytest.mark.asyncio
    async def test_concrete_hook(self) -> None:
        class ConcreteHook(EvidenceFusionHook):
            async def fuse_evidence(self, task: WorkflowTask) -> WorkflowTask:
                task.inputs["fused"] = True
                return task

        hook = ConcreteHook()
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="T")
        result = await hook.fuse_evidence(task)
        assert result.inputs["fused"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility
# ─────────────────────────────────────────────────────────────────────────────


class TestBackwardCompatibility:
    def test_workflow_result_accepts_decisions(self) -> None:
        result = WorkflowResult()
        assert result.decisions == []

    def test_workflow_result_accepts_traces(self) -> None:
        result = WorkflowResult()
        assert result.traces == []

    def test_workflow_result_accepts_events(self) -> None:
        result = WorkflowResult()
        assert result.events == []

    def test_workflow_trace_importable_from_execution(self) -> None:
        from adip.workflow.contracts.models import WorkflowTrace as TraceFromModels
        from adip.workflow.execution.trace import WorkflowTrace as TraceFromExecution
        assert TraceFromExecution is TraceFromModels

    def test_workflow_request_backward_compat(self) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="test"),
            tasks=[PlanningTask(task_id=uuid.uuid4(), task_name="T", description="")],
        )
        req = WorkflowRequest(execution_plan=plan)
        assert req.policy is not None

    def test_old_event_deserialisation_still_works(self) -> None:
        old_data = {
            "event_id": str(uuid.uuid4()),
            "workflow_id": str(uuid.uuid4()),
            "timestamp": "2025-01-01T00:00:00",
            "correlation_id": "",
            "payload": {},
        }
        event = WorkflowStarted(**old_data)
        assert event.execution_plan_id == ""
        assert event.event_version == EVENT_VERSION

    def test_metrics_old_fields_still_work(self) -> None:
        m = WorkflowMetrics(total_execution_time=50.0, executed_tasks=3)
        assert m.total_execution_time == 50.0
        assert m.executed_tasks == 3
        assert isinstance(m.scheduling_time, float)  # new field exists


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowEngine — policy integration
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_plan() -> ExecutionPlan:
    goal = PlanningGoal(objective="Test policy integration")
    tasks = [
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task A",
            description="",
            dependencies=[],
        ),
        PlanningTask(
            task_id=uuid.uuid4(),
            task_name="Task B",
            description="",
            dependencies=[],
        ),
    ]
    tasks[1].dependencies = [tasks[0].task_id]
    return ExecutionPlan(goal=goal, tasks=tasks)


@pytest.fixture
def engine() -> DefaultWorkflowEngine:
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


class TestWorkflowEnginePolicyIntegration:
    @pytest.mark.asyncio
    async def test_custom_policy_accepted(
        self, engine: DefaultWorkflowEngine, sample_plan: ExecutionPlan,
    ) -> None:
        policy = WorkflowPolicy(retry_limit=1, failure_policy="continue")
        request = WorkflowRequest(
            execution_plan=sample_plan,
            policy=policy,
        )
        result = await engine.execute(request)
        assert result.metrics is not None
        assert isinstance(result.metrics.workflow_confidence, float)

    @pytest.mark.asyncio
    async def test_default_policy_used(
        self, engine: DefaultWorkflowEngine, sample_plan: ExecutionPlan,
    ) -> None:
        request = WorkflowRequest(execution_plan=sample_plan)
        result = await engine.execute(request)
        assert result.metrics is not None
        assert result.metrics.executed_tasks >= 1

    @pytest.mark.asyncio
    async def test_trace_recorded_in_result(
        self, engine: DefaultWorkflowEngine, sample_plan: ExecutionPlan,
    ) -> None:
        request = WorkflowRequest(execution_plan=sample_plan)
        result = await engine.execute(request)
        assert len(result.traces) >= 2

    @pytest.mark.asyncio
    async def test_efficiency_metrics_computed(
        self, engine: DefaultWorkflowEngine, sample_plan: ExecutionPlan,
    ) -> None:
        request = WorkflowRequest(execution_plan=sample_plan)
        result = await engine.execute(request)
        assert result.execution_efficiency >= 0.0
        assert result.execution_efficiency <= 100.0

    @pytest.mark.asyncio
    async def test_scheduling_time_recorded(
        self, engine: DefaultWorkflowEngine, sample_plan: ExecutionPlan,
    ) -> None:
        request = WorkflowRequest(execution_plan=sample_plan)
        result = await engine.execute(request)
        if result.metrics is not None:
            assert result.metrics.scheduling_time >= 0.0

    @pytest.mark.asyncio
    async def test_service_policy_passthrough(
        self, engine: DefaultWorkflowEngine, sample_plan: ExecutionPlan,
    ) -> None:
        service = DefaultWorkflowService(engine)
        policy = WorkflowPolicy(compensation_enabled=True)
        request = WorkflowRequest(
            execution_plan=sample_plan,
            policy=policy,
        )
        result = await service.start_workflow(request)
        assert result.metrics is not None
        assert result.metrics.execution_efficiency >= 0.0
