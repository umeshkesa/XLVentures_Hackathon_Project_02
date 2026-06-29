"""Phase 2 tests for the Action Engine (Execution Runtime & Monitoring Pipeline).

Tests all 18 execution components with deterministic placeholder
implementations.
"""

from __future__ import annotations

from adip.execution.enums import ExecutionState
from adip.execution.execution.audit_trail import AuditTrail
from adip.execution.execution.checkpoint_manager import CheckpointManager
from adip.execution.execution.compensation_manager import CompensationManager
from adip.execution.execution.event_bus import RuntimeEventBus
from adip.execution.execution.execution_graph import ExecutionGraph
from adip.execution.execution.failure_classifier import FailureClassifier
from adip.execution.execution.metrics import ExecutionMetricsCollector
from adip.execution.execution.monitor import ExecutionMonitor
from adip.execution.execution.parallel_executor import ParallelTaskExecutor
from adip.execution.execution.policy_engine import ExecutionPolicyEngine
from adip.execution.execution.progress_tracker import ExecutionProgressTracker
from adip.execution.execution.report import ExecutionReportGenerator
from adip.execution.execution.resource_monitor import ResourceMonitor
from adip.execution.execution.retry_manager import RetryManager
from adip.execution.execution.scheduler import ExecutionScheduler
from adip.execution.execution.state_machine import ExecutionStateMachine
from adip.execution.execution.telemetry import ExecutionTelemetry
from adip.execution.execution.trace import ExecutionTrace

# ═════════════════════════════════════════════════════════════════════════════
# ExecutionGraph
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionGraph:
    def test_build_graph_no_deps(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(
            package_id="pkg-1",
            task_ids=["t1", "t2", "t3"],
        )
        assert g.package_id == "pkg-1"
        assert len(g.nodes) == 3
        assert len(g.edges) == 0
        assert g.has_cycle is False
        assert g.is_dag is True
        assert len(g.topological_order) == 3

    def test_build_graph_with_deps(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(
            package_id="pkg-1",
            task_ids=["t1", "t2", "t3"],
            dependencies=[("t1", "t2", "hard"), ("t2", "t3", "hard")],
        )
        assert len(g.nodes) == 3
        assert len(g.edges) == 2
        assert g.has_cycle is False
        assert g.topological_order == ["t1", "t2", "t3"]

    def test_cycle_detection(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(
            package_id="pkg-1",
            task_ids=["t1", "t2", "t3"],
            dependencies=[("t1", "t2", "hard"), ("t2", "t3", "hard"), ("t3", "t1", "hard")],
        )
        assert g.has_cycle is True
        assert g.is_dag is False
        assert g.topological_order == []

    def test_parallel_groups(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(
            package_id="pkg-1",
            task_ids=["t1", "t2", "t3", "t4"],
            dependencies=[("t1", "t3", "hard"), ("t2", "t3", "hard"), ("t3", "t4", "hard")],
        )
        assert g.has_cycle is False
        assert g.topological_order[0] in ["t1", "t2"]
        assert g.topological_order[1] in ["t1", "t2"]
        assert g.topological_order[2] == "t3"
        assert g.topological_order[3] == "t4"

    def test_validate_graph_valid(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(package_id="pkg-1", task_ids=["t1", "t2"])
        issues = graph.validate_graph(g)
        assert issues == []

    def test_validate_graph_with_cycle(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(
            package_id="pkg-1",
            task_ids=["t1", "t2"],
            dependencies=[("t1", "t2", "hard"), ("t2", "t1", "hard")],
        )
        issues = graph.validate_graph(g)
        assert len(issues) > 0
        assert any("cycle" in i.lower() for i in issues)

    def test_validate_graph_empty(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(package_id="pkg-1", task_ids=[])
        issues = graph.validate_graph(g)
        assert any("no nodes" in i.lower() for i in issues)

    def test_get_ready_tasks(self) -> None:
        graph = ExecutionGraph()
        g = graph.build_graph(
            package_id="pkg-1",
            task_ids=["t1", "t2", "t3"],
            dependencies=[("t1", "t3", "hard"), ("t2", "t3", "hard")],
        )
        ready = graph.get_ready_tasks(g, set())
        assert "t1" in ready
        assert "t2" in ready
        assert "t3" not in ready


# ═════════════════════════════════════════════════════════════════════════════
# ParallelTaskExecutor
# ═════════════════════════════════════════════════════════════════════════════


class TestParallelTaskExecutor:
    def test_execute_parallel_group(self) -> None:
        executor = ParallelTaskExecutor()
        results = executor.execute_parallel_group(
            task_ids=["t1", "t2", "t3"],
            session_id="sess-1",
        )
        assert len(results) == 3
        for tid, r in results.items():
            assert r["success"] is True
            assert r["state"] == ExecutionState.COMPLETED

    def test_execute_sequentially(self) -> None:
        executor = ParallelTaskExecutor()
        results = executor.execute_sequentially(
            task_ids=["t1", "t2"],
            session_id="sess-1",
        )
        assert len(results) == 2

    def test_simulate_task_failure(self) -> None:
        executor = ParallelTaskExecutor()
        result = executor.simulate_task_failure("t1", session_id="sess-1")
        assert result["success"] is False
        assert result["state"] == ExecutionState.FAILED

    def test_get_completed_tasks(self) -> None:
        executor = ParallelTaskExecutor()
        executor.execute_parallel_group(["t1"], session_id="sess-1")
        completed = executor.get_completed_tasks()
        assert "t1" in completed

    def test_reset(self) -> None:
        executor = ParallelTaskExecutor()
        executor.execute_parallel_group(["t1"], session_id="sess-1")
        executor.reset()
        assert executor.get_completed_tasks() == {}


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionPolicyEngine
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionPolicyEngine:
    def test_validate_safety_allowed(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_safety(task_type="AUTOMATED", domain="ENERGY")
        assert result.is_allowed is True
        assert result.violations == []

    def test_validate_safety_violation(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_safety(task_type="MANUAL", domain="ENERGY")
        assert result.is_allowed is False
        assert len(result.violations) > 0

    def test_validate_governance_allowed(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_governance(priority="LOW")
        assert result.is_allowed is True

    def test_validate_governance_violation(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_governance(priority="HIGH")
        assert result.is_allowed is False

    def test_validate_maintenance_window(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_maintenance_window(domain="ENERGY")
        assert result.is_allowed is False

    def test_validate_resources_allowed(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_resources(task_count=5)
        assert result.is_allowed is True

    def test_validate_resources_violation(self) -> None:
        engine = ExecutionPolicyEngine()
        result = engine.validate_resources(task_count=25)
        assert result.is_allowed is False

    def test_validate_all(self) -> None:
        engine = ExecutionPolicyEngine()
        results = engine.validate_all(
            task_type="MANUAL",
            domain="ENERGY",
            priority="HIGH",
            task_count=25,
        )
        assert len(results) == 4
        total_violations = sum(len(r.violations) for r in results)
        assert total_violations > 0


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionScheduler
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionScheduler:
    def test_schedule_immediate(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_immediate(package_id="pkg-1")
        assert se.schedule_type == "immediate"
        assert se.executed is False

    def test_schedule_delayed(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_delayed(package_id="pkg-1", delay_seconds=60)
        assert se.schedule_type == "delayed"

    def test_schedule_maintenance_window(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_maintenance_window(package_id="pkg-1")
        assert se.schedule_type == "maintenance_window"

    def test_schedule_retry(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_retry(package_id="pkg-1", attempt=1, delay_seconds=30)
        assert se.schedule_type == "retry"

    def test_get_schedule(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_immediate(package_id="pkg-1")
        assert sched.get_schedule(se.schedule_id) is not None

    def test_get_all_schedules(self) -> None:
        sched = ExecutionScheduler()
        sched.schedule_immediate(package_id="pkg-1")
        sched.schedule_delayed(package_id="pkg-2")
        assert len(sched.get_all_schedules()) == 2

    def test_mark_executed(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_immediate(package_id="pkg-1")
        assert sched.mark_executed(se.schedule_id) is True
        assert sched.get_schedule(se.schedule_id).executed is True

    def test_cancel(self) -> None:
        sched = ExecutionScheduler()
        se = sched.schedule_immediate(package_id="pkg-1")
        assert sched.cancel(se.schedule_id) is True
        assert sched.get_schedule(se.schedule_id) is None

    def test_cancel_not_found(self) -> None:
        sched = ExecutionScheduler()
        assert sched.cancel("nonexistent") is False


# ═════════════════════════════════════════════════════════════════════════════
# CheckpointManager
# ═════════════════════════════════════════════════════════════════════════════


class TestCheckpointManager:
    def test_create_checkpoint(self) -> None:
        mgr = CheckpointManager()
        cp = mgr.create_checkpoint(
            session_id="sess-1",
            package_id="pkg-1",
            completed_task_ids=["t1", "t2"],
            state=ExecutionState.RUNNING,
        )
        assert cp.session_id == "sess-1"
        assert cp.completed_task_ids == ["t1", "t2"]
        assert cp.state == ExecutionState.RUNNING

    def test_get_checkpoint(self) -> None:
        mgr = CheckpointManager()
        cp = mgr.create_checkpoint(session_id="sess-1", package_id="pkg-1")
        assert mgr.get_checkpoint(str(cp.checkpoint_id)) is not None

    def test_get_checkpoint_not_found(self) -> None:
        mgr = CheckpointManager()
        assert mgr.get_checkpoint("nonexistent") is None

    def test_restore_checkpoint(self) -> None:
        mgr = CheckpointManager()
        cp = mgr.create_checkpoint(session_id="sess-1", package_id="pkg-1")
        restored = mgr.restore_checkpoint(str(cp.checkpoint_id))
        assert restored is not None
        assert restored.session_id == "sess-1"

    def test_latest_for_session(self) -> None:
        import time
        mgr = CheckpointManager()
        mgr.create_checkpoint(session_id="sess-1", package_id="pkg-1")
        time.sleep(0.01)
        cp2 = mgr.create_checkpoint(session_id="sess-1", package_id="pkg-1")
        latest = mgr.get_latest_for_session("sess-1")
        assert latest.checkpoint_id == cp2.checkpoint_id

    def test_delete_checkpoint(self) -> None:
        mgr = CheckpointManager()
        cp = mgr.create_checkpoint(session_id="sess-1", package_id="pkg-1")
        assert mgr.delete_checkpoint(str(cp.checkpoint_id)) is True
        assert mgr.get_checkpoint(str(cp.checkpoint_id)) is None

    def test_resume_from_checkpoint(self) -> None:
        mgr = CheckpointManager()
        cp = mgr.create_checkpoint(
            session_id="sess-1",
            package_id="pkg-1",
            completed_task_ids=["t1", "t2"],
            pending_task_ids=["t3"],
            state=ExecutionState.RUNNING,
        )
        plan = mgr.resume_from_checkpoint(cp)
        assert "t1" in plan["completed"]
        assert "t2" in plan["completed"]
        assert "t3" in plan["pending"]


# ═════════════════════════════════════════════════════════════════════════════
# RetryManager
# ═════════════════════════════════════════════════════════════════════════════


class TestRetryManager:
    def test_should_retry_yes(self) -> None:
        mgr = RetryManager()
        assert mgr.should_retry(task_id="t1", attempt=0, max_retries=3) is True

    def test_should_retry_no_exceeded(self) -> None:
        mgr = RetryManager()
        assert mgr.should_retry(task_id="t1", attempt=3, max_retries=3) is False

    def test_should_retry_no_timeout(self) -> None:
        mgr = RetryManager()
        assert mgr.should_retry(task_id="t1", attempt=0, retry_on_timeout=False, error="timeout") is False

    def test_should_retry_no_error(self) -> None:
        mgr = RetryManager()
        assert mgr.should_retry(task_id="t1", attempt=0, retry_on_error=False, error="error") is False

    def test_get_delay(self) -> None:
        mgr = RetryManager()
        delay = mgr.get_delay(attempt=0, base_delay_seconds=30)
        assert delay == 30

    def test_get_delay_exponential(self) -> None:
        mgr = RetryManager()
        delay = mgr.get_delay(attempt=2, base_delay_seconds=10, backoff_multiplier=2.0)
        assert delay == 40

    def test_get_delay_max(self) -> None:
        mgr = RetryManager()
        delay = mgr.get_delay(attempt=10, base_delay_seconds=30, backoff_multiplier=2.0, max_delay_seconds=100)
        assert delay <= 100

    def test_record_and_get_retries(self) -> None:
        mgr = RetryManager()
        mgr.record_retry(task_id="t1", attempt=0, error="timeout", success=False)
        assert mgr.get_retry_count("t1") == 1
        assert len(mgr.get_retries("t1")) == 1

    def test_get_total_retries(self) -> None:
        mgr = RetryManager()
        mgr.record_retry(task_id="t1", attempt=0)
        mgr.record_retry(task_id="t2", attempt=0)
        assert mgr.get_total_retries() == 2


# ═════════════════════════════════════════════════════════════════════════════
# CompensationManager
# ═════════════════════════════════════════════════════════════════════════════


class TestCompensationManager:
    def test_compensate(self) -> None:
        mgr = CompensationManager()
        action = mgr.compensate(task_id="t1", session_id="sess-1", reason="failure")
        assert action.action_type == "compensation"
        assert action.success is True

    def test_rollback(self) -> None:
        mgr = CompensationManager()
        action = mgr.rollback(task_id="t1", session_id="sess-1", reason="failure")
        assert action.action_type == "rollback"
        assert action.success is True

    def test_manual_recovery(self) -> None:
        mgr = CompensationManager()
        action = mgr.manual_recovery(task_id="t1", session_id="sess-1")
        assert action.action_type == "manual_recovery"
        assert len(action.details["recovery_steps"]) > 0

    def test_alternative_action(self) -> None:
        mgr = CompensationManager()
        action = mgr.alternative_action(task_id="t1", session_id="sess-1", alternative="Use backup")
        assert action.action_type == "alternative_action"

    def test_get_actions(self) -> None:
        mgr = CompensationManager()
        mgr.compensate(task_id="t1", session_id="sess-1")
        assert len(mgr.get_actions()) == 1

    def test_clear(self) -> None:
        mgr = CompensationManager()
        mgr.compensate(task_id="t1", session_id="sess-1")
        mgr.clear()
        assert mgr.get_total_actions() == 0


# ═════════════════════════════════════════════════════════════════════════════
# FailureClassifier
# ═════════════════════════════════════════════════════════════════════════════


class TestFailureClassifier:
    def test_classify_transient(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="connection refused")
        assert result.failure_type == "transient"
        assert result.is_retryable is True

    def test_classify_timeout(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="request timeout")
        assert result.failure_type == "timeout"
        assert result.is_retryable is True

    def test_classify_infrastructure(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="disk full")
        assert result.failure_type == "infrastructure"
        assert result.is_retryable is False

    def test_classify_permanent(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="not found")
        assert result.failure_type == "permanent"
        assert result.is_retryable is False
        assert result.requires_compensation is True

    def test_classify_policy(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="policy violation")
        assert result.failure_type == "policy"
        assert result.is_retryable is False

    def test_classify_dependency(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="missing dependency")
        assert result.failure_type == "dependency"

    def test_classify_default(self) -> None:
        classifier = FailureClassifier()
        result = classifier.classify(task_id="t1", error_message="unknown error")
        assert result.failure_type == "transient"


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionProgressTracker
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionProgressTracker:
    def test_get_progress(self) -> None:
        tracker = ExecutionProgressTracker()
        report = tracker.get_progress(
            session_id="sess-1",
            total_tasks=10,
            completed_tasks=5,
            failed_tasks=0,
            state=ExecutionState.RUNNING,
        )
        assert report.total_tasks == 10
        assert report.completed_tasks == 5
        assert report.overall_progress == 0.5

    def test_get_progress_full(self) -> None:
        tracker = ExecutionProgressTracker()
        report = tracker.get_progress(
            session_id="sess-1",
            total_tasks=10,
            completed_tasks=10,
            state=ExecutionState.COMPLETED,
        )
        assert report.overall_progress == 1.0

    def test_update_task_completed(self) -> None:
        tracker = ExecutionProgressTracker()
        tracker.get_progress(session_id="sess-1", total_tasks=5, completed_tasks=2)
        updated = tracker.update_task_completed(session_id="sess-1")
        assert updated.completed_tasks == 3

    def test_update_task_failed(self) -> None:
        tracker = ExecutionProgressTracker()
        tracker.get_progress(session_id="sess-1", total_tasks=5, completed_tasks=2)
        updated = tracker.update_task_failed(session_id="sess-1")
        assert updated.failed_tasks == 1

    def test_get_report(self) -> None:
        tracker = ExecutionProgressTracker()
        tracker.get_progress(session_id="sess-1", total_tasks=5)
        assert tracker.get_report("sess-1") is not None

    def test_get_report_not_found(self) -> None:
        tracker = ExecutionProgressTracker()
        assert tracker.get_report("nonexistent") is None


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionMonitor
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionMonitor:
    def test_register_session(self) -> None:
        monitor = ExecutionMonitor()
        monitor.register_session(session_id="sess-1", package_id="pkg-1", task_ids=["t1", "t2"])
        status = monitor.get_session_status("sess-1")
        assert status is not None
        assert status["package_id"] == "pkg-1"

    def test_update_task_state(self) -> None:
        monitor = ExecutionMonitor()
        monitor.register_session(session_id="sess-1", package_id="pkg-1", task_ids=["t1"])
        assert monitor.update_task_state("sess-1", "t1", ExecutionState.RUNNING) is True

    def test_record_failure(self) -> None:
        monitor = ExecutionMonitor()
        monitor.register_session(session_id="sess-1", package_id="pkg-1", task_ids=["t1"])
        assert monitor.record_failure("sess-1", "t1", "error") is True
        assert monitor.get_total_failures() == 1

    def test_get_session_status_not_found(self) -> None:
        monitor = ExecutionMonitor()
        assert monitor.get_session_status("nonexistent") is None

    def test_get_active_sessions(self) -> None:
        monitor = ExecutionMonitor()
        monitor.register_session(session_id="sess-1", package_id="pkg-1", task_ids=["t1"])
        assert len(monitor.get_active_sessions()) == 1

    def test_get_all_sessions(self) -> None:
        monitor = ExecutionMonitor()
        monitor.register_session(session_id="sess-1", package_id="pkg-1")
        monitor.register_session(session_id="sess-2", package_id="pkg-2")
        assert len(monitor.get_all_sessions()) == 2


# ═════════════════════════════════════════════════════════════════════════════
# AuditTrail
# ═════════════════════════════════════════════════════════════════════════════


class TestAuditTrail:
    def test_record_event(self) -> None:
        trail = AuditTrail()
        record = trail.record_event(session_id="sess-1", event_type="task_started", task_id="t1")
        assert record.event_type == "task_started"
        assert record.session_id == "sess-1"

    def test_record_checkpoint(self) -> None:
        trail = AuditTrail()
        record = trail.record_checkpoint(session_id="sess-1", checkpoint_id="cp-1")
        assert record.event_type == "checkpoint"

    def test_record_retry(self) -> None:
        trail = AuditTrail()
        record = trail.record_retry(session_id="sess-1", task_id="t1", attempt=1)
        assert record.event_type == "retry"

    def test_record_rollback(self) -> None:
        trail = AuditTrail()
        record = trail.record_rollback(session_id="sess-1", task_id="t1", reason="failure")
        assert record.event_type == "rollback"

    def test_get_records_filtered(self) -> None:
        trail = AuditTrail()
        trail.record_event(session_id="sess-1", event_type="task_started", task_id="t1")
        trail.record_event(session_id="sess-1", event_type="task_completed", task_id="t1")
        records = trail.get_records(session_id="sess-1", event_type="task_started")
        assert len(records) == 1

    def test_clear(self) -> None:
        trail = AuditTrail()
        trail.record_event(session_id="sess-1", event_type="task_started")
        trail.clear()
        assert len(trail.get_all_records()) == 0


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionTelemetry
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionTelemetry:
    def test_record_metric(self) -> None:
        telemetry = ExecutionTelemetry()
        record = telemetry.record_metric(session_id="sess-1", metric_name="cpu", metric_value=50.0)
        assert record.metric_name == "cpu"
        assert record.metric_value == 50.0

    def test_record_event(self) -> None:
        telemetry = ExecutionTelemetry()
        record = telemetry.record_event(session_id="sess-1", event_name="task_started")
        assert record.unit == "count"

    def test_record_timing(self) -> None:
        telemetry = ExecutionTelemetry()
        record = telemetry.record_timing(session_id="sess-1", operation="execute", duration_ms=150.0)
        assert record.unit == "ms"

    def test_get_records_filtered(self) -> None:
        telemetry = ExecutionTelemetry()
        telemetry.record_metric(session_id="sess-1", metric_name="cpu", metric_value=50.0)
        telemetry.record_metric(session_id="sess-2", metric_name="cpu", metric_value=80.0)
        assert len(telemetry.get_records(session_id="sess-1")) == 1

    def test_get_average_timing(self) -> None:
        telemetry = ExecutionTelemetry()
        telemetry.record_timing(session_id="sess-1", operation="execute", duration_ms=100.0)
        telemetry.record_timing(session_id="sess-1", operation="execute", duration_ms=200.0)
        avg = telemetry.get_average_timing("execute", "sess-1")
        assert avg == 150.0


# ═════════════════════════════════════════════════════════════════════════════
# ResourceMonitor
# ═════════════════════════════════════════════════════════════════════════════


class TestResourceMonitor:
    def test_acquire_worker(self) -> None:
        monitor = ResourceMonitor(max_workers=5)
        assert monitor.acquire_worker(session_id="sess-1") is True
        assert monitor.get_active_workers() == 1

    def test_acquire_worker_at_capacity(self) -> None:
        monitor = ResourceMonitor(max_workers=1)
        monitor.acquire_worker()
        assert monitor.acquire_worker() is False

    def test_release_worker(self) -> None:
        monitor = ResourceMonitor(max_workers=5)
        monitor.acquire_worker()
        monitor.release_worker()
        assert monitor.get_active_workers() == 0

    def test_snapshot(self) -> None:
        monitor = ResourceMonitor(max_workers=10)
        monitor.acquire_worker(session_id="sess-1")
        usage = monitor.snapshot(session_id="sess-1", runtime_seconds=60.0)
        assert usage.active_workers == 1
        assert usage.runtime_seconds == 60.0

    def test_get_available_workers(self) -> None:
        monitor = ResourceMonitor(max_workers=10)
        monitor.acquire_worker()
        assert monitor.get_available_workers() == 9

    def test_max_workers_setter(self) -> None:
        monitor = ResourceMonitor(max_workers=10)
        monitor.max_workers = 20
        assert monitor.max_workers == 20


# ═════════════════════════════════════════════════════════════════════════════
# RuntimeEventBus
# ═════════════════════════════════════════════════════════════════════════════


class TestRuntimeEventBus:
    def test_publish_and_subscribe(self) -> None:
        bus = RuntimeEventBus()
        received: list[str] = []

        def handler(msg) -> None:
            received.append(msg.event_type)

        bus.subscribe("task", handler)
        bus.publish_task_event("started", session_id="sess-1", task_id="t1")
        assert len(received) == 1
        assert received[0] == "started"

    def test_unsubscribe(self) -> None:
        bus = RuntimeEventBus()
        def handler(msg) -> None: pass
        bus.subscribe("task", handler)
        assert bus.unsubscribe("task", handler) is True
        assert bus.unsubscribe("task", handler) is False

    def test_publish_execution_event(self) -> None:
        bus = RuntimeEventBus()
        msg = bus.publish_execution_event("completed", session_id="sess-1")
        assert msg.topic == "execution"
        assert msg.event_type == "completed"

    def test_get_messages(self) -> None:
        bus = RuntimeEventBus()
        bus.publish_execution_event("started", session_id="sess-1")
        bus.publish_task_event("started", session_id="sess-1")
        assert len(bus.get_messages(topic="execution")) == 1

    def test_handler_exception_isolation(self) -> None:
        bus = RuntimeEventBus()
        def failing_handler(msg) -> None:
            raise ValueError("handler error")
        bus.subscribe("task", failing_handler)
        bus.publish_task_event("started", session_id="sess-1")
        assert len(bus.get_messages(topic="task")) == 1


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionStateMachine
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionStateMachine:
    def test_initial_state(self) -> None:
        sm = ExecutionStateMachine()
        assert sm.get_current_state("entity-1") == ExecutionState.PENDING

    def test_valid_transition(self) -> None:
        sm = ExecutionStateMachine()
        success, msg = sm.transition("entity-1", ExecutionState.READY)
        assert success is True
        assert sm.get_current_state("entity-1") == ExecutionState.READY

    def test_invalid_transition(self) -> None:
        sm = ExecutionStateMachine()
        success, msg = sm.transition("entity-1", ExecutionState.COMPLETED)
        assert success is False

    def test_full_lifecycle(self) -> None:
        sm = ExecutionStateMachine()
        sm.transition("e1", ExecutionState.READY)
        sm.transition("e1", ExecutionState.RUNNING)
        sm.transition("e1", ExecutionState.COMPLETED)
        assert sm.get_current_state("e1") == ExecutionState.COMPLETED
        assert sm.is_terminal("e1") is True

    def test_is_terminal(self) -> None:
        sm = ExecutionStateMachine()
        sm.transition("e1", ExecutionState.READY)
        assert sm.is_terminal("e1") is False
        sm.transition("e1", ExecutionState.RUNNING)
        sm.transition("e1", ExecutionState.FAILED)
        assert sm.is_terminal("e1") is True

    def test_is_active(self) -> None:
        sm = ExecutionStateMachine()
        sm.transition("e1", ExecutionState.READY)
        sm.transition("e1", ExecutionState.RUNNING)
        assert sm.is_active("e1") is True
        sm.transition("e1", ExecutionState.COMPLETED)
        assert sm.is_active("e1") is False

    def test_reset(self) -> None:
        sm = ExecutionStateMachine()
        sm.transition("e1", ExecutionState.READY)
        sm.reset("e1")
        assert sm.get_current_state("e1") == ExecutionState.PENDING

    def test_is_transition_allowed(self) -> None:
        sm = ExecutionStateMachine()
        assert sm.is_transition_allowed(ExecutionState.PENDING, ExecutionState.READY) is True
        assert sm.is_transition_allowed(ExecutionState.PENDING, ExecutionState.COMPLETED) is False

    def test_get_allowed_transitions(self) -> None:
        sm = ExecutionStateMachine()
        allowed = sm.get_allowed_transitions(ExecutionState.PENDING)
        assert ExecutionState.READY in allowed
        assert ExecutionState.CANCELLED in allowed


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionReportGenerator
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionReportGenerator:
    def test_generate_success_report(self) -> None:
        generator = ExecutionReportGenerator()
        report = generator.generate(
            session_id="sess-1",
            package_id="pkg-1",
            total_tasks=5,
            completed_tasks=5,
            final_state=ExecutionState.COMPLETED,
        )
        assert report.overall_success is True
        assert report.total_tasks == 5
        assert report.tasks_completed == 5

    def test_generate_failure_report(self) -> None:
        generator = ExecutionReportGenerator()
        report = generator.generate(
            session_id="sess-1",
            package_id="pkg-1",
            total_tasks=5,
            completed_tasks=3,
            failed_tasks=2,
            final_state=ExecutionState.FAILED,
        )
        assert report.overall_success is False
        assert report.tasks_failed == 2

    def test_generate_with_retries(self) -> None:
        generator = ExecutionReportGenerator()
        report = generator.generate(
            session_id="sess-1",
            package_id="pkg-1",
            total_tasks=5,
            completed_tasks=5,
            retries_performed=3,
            final_state=ExecutionState.COMPLETED,
        )
        assert report.retries_performed == 3

    def test_generate_summary(self) -> None:
        generator = ExecutionReportGenerator()
        summary = generator.generate_summary(
            session_id="sess-1",
            package_id="pkg-1",
            total_tasks=10,
            completed_tasks=8,
            failed_tasks=2,
            final_state=ExecutionState.COMPLETED,
        )
        assert summary["total_tasks"] == 10
        assert summary["success_rate"] == 0.8


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionTrace
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionTrace:
    def test_record_stage(self) -> None:
        trace = ExecutionTrace()
        record = trace.record_stage(
            stage_name="execution",
            session_id="sess-1",
            task_id="t1",
            details="Task execution",
        )
        assert record.stage_name == "execution"
        assert record.session_id == "sess-1"

    def test_record_execution_stage(self) -> None:
        trace = ExecutionTrace()
        record = trace.record_execution_stage(session_id="sess-1", task_id="t1", duration_ms=100.0)
        assert record.stage_name == "execution"
        assert record.duration_ms == 100.0

    def test_record_monitoring_stage(self) -> None:
        trace = ExecutionTrace()
        record = trace.record_monitoring_stage(session_id="sess-1")
        assert record.stage_name == "monitoring"

    def test_record_recovery_stage(self) -> None:
        trace = ExecutionTrace()
        record = trace.record_recovery_stage(
            session_id="sess-1",
            task_id="t1",
            recovery_type="retry",
        )
        assert record.stage_name == "recovery.retry"

    def test_get_traces_filtered(self) -> None:
        trace = ExecutionTrace()
        trace.record_stage("execution", session_id="sess-1")
        trace.record_stage("monitoring", session_id="sess-1")
        traces = trace.get_traces(stage_name="execution")
        assert len(traces) == 1

    def test_clear(self) -> None:
        trace = ExecutionTrace()
        trace.record_stage("execution", session_id="sess-1")
        trace.clear()
        assert len(trace.get_all_traces()) == 0


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionMetricsCollector
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionMetricsCollector:
    def test_record_session(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_session()
        assert metrics.get_sessions_total() == 1

    def test_record_task(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_task(5)
        assert metrics.get_tasks_total() == 5

    def test_record_task_completed(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_task_completed(150.0)
        assert metrics.get_tasks_completed() == 1
        assert metrics.get_average_task_duration_ms() == 150.0

    def test_record_task_failed(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_task_failed()
        assert metrics.get_tasks_failed() == 1

    def test_record_retry(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_retry()
        assert metrics.get_retries_total() == 1

    def test_record_rollback(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_rollback()
        assert metrics.get_rollbacks_total() == 1

    def test_record_compensation(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_compensation()
        assert metrics.get_compensations_total() == 1

    def test_snapshot(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_session()
        metrics.record_task(10)
        metrics.record_task_completed(100.0)
        metrics.record_task_failed()
        snapshot = metrics.snapshot()
        assert snapshot.sessions_total == 1
        assert snapshot.tasks_total == 10
        assert snapshot.tasks_completed == 1
        assert snapshot.tasks_failed == 1

    def test_reset(self) -> None:
        metrics = ExecutionMetricsCollector()
        metrics.record_session()
        metrics.reset()
        assert metrics.get_sessions_total() == 0
