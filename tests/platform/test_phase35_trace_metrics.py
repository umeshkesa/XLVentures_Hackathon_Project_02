"""Phase 3.5 smoke tests — Trace and Metrics Enhancements."""

from __future__ import annotations

from adip.platform.orchestration.integration_metrics import DefaultIntegrationMetrics
from adip.platform.orchestration.integration_trace import DefaultIntegrationTrace


class TestIntegrationTraceEnhancement:
    """Verify Phase 3.5 trace enhancements."""

    def test_record_validation_stage(self) -> None:
        trace = DefaultIntegrationTrace()
        tr = trace.create_trace("test-validation")
        trace.record_validation_stage(
            trace_id=str(tr.trace_id),
            stage="readiness_check",
            component="readiness_checker",
            status="passed",
            duration_ms=15.5,
        )
        entries = trace.get_trace(str(tr.trace_id))
        assert entries is not None
        assert len(entries.entries) == 1
        assert entries.entries[0].details["validation_stage"] == "readiness_check"

    def test_get_phase_trace_summary(self) -> None:
        trace = DefaultIntegrationTrace()
        tr = trace.create_trace("test-phases")
        tid = str(tr.trace_id)
        trace.record_validation_stage(tid, "quality", "qm", "ok", 10.0)
        trace.record_validation_stage(tid, "compliance", "cm", "ok", 5.0)
        summary = trace.get_phase_trace_summary(tid)
        assert "quality" in summary["phase_breakdown"]
        assert "compliance" in summary["phase_breakdown"]
        assert summary["total_entries"] == 2

    def test_summarize_workflow_includes_phase_breakdown(self) -> None:
        trace = DefaultIntegrationTrace()
        tr = trace.create_trace("test-summary")
        tid = str(tr.trace_id)
        trace.record_validation_stage(tid, "readiness", "rc", "passed", 12.0)
        summary = trace.summarize_workflow(tid)
        assert "phase_breakdown" in summary


class TestIntegrationMetricsEnhancement:
    """Verify Phase 3.5 metrics enhancements."""

    def test_record_validation_operation(self) -> None:
        metrics = DefaultIntegrationMetrics()
        metrics.record_validation_operation()
        metrics.record_validation_operation()
        snapshot = metrics.get_workflow_snapshot()
        assert snapshot["validation_operations"] == 2

    def test_record_readiness_check(self) -> None:
        metrics = DefaultIntegrationMetrics()
        metrics.record_readiness_check()
        snapshot = metrics.get_workflow_snapshot()
        assert snapshot["readiness_checks"] == 1

    def test_record_audit_package_created(self) -> None:
        metrics = DefaultIntegrationMetrics()
        metrics.record_audit_package_created()
        snapshot = metrics.get_workflow_snapshot()
        assert snapshot["audit_packages_created"] == 1

    def test_record_snapshot_taken(self) -> None:
        metrics = DefaultIntegrationMetrics()
        metrics.record_snapshot_taken()
        snapshot = metrics.get_workflow_snapshot()
        assert snapshot["snapshots_taken"] == 1
