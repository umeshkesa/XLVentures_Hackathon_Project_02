"""Phase 2 smoke tests — integration trace and metrics."""

from __future__ import annotations

from adip.platform.enums import PipelineStage
from adip.platform.orchestration.integration_metrics import DefaultIntegrationMetrics
from adip.platform.orchestration.integration_trace import DefaultIntegrationTrace


class TestIntegrationTrace:
    """Verify workflow-spanning trace."""

    def test_initialise(self) -> None:
        trace = DefaultIntegrationTrace()
        assert trace.list_traces() == []

    def test_create_and_complete(self) -> None:
        trace = DefaultIntegrationTrace()
        t = trace.create_trace("test-123")
        trace.complete_trace(str(t.trace_id), 100.0)
        stored = trace.get_trace(str(t.trace_id))
        assert stored is not None
        assert stored.completed
        assert stored.total_duration_ms == 100.0

    def test_record_workflow_stage(self) -> None:
        trace = DefaultIntegrationTrace()
        t = trace.create_trace("test-456")
        trace.record_workflow_stage(
            trace_id=str(t.trace_id),
            stage=PipelineStage.PLANNER,
            module="planner",
            input_keys=["request"],
            output_keys=["plan"],
            duration_ms=50.0,
        )
        stored = trace.get_trace(str(t.trace_id))
        assert stored is not None
        assert len(stored.entries) == 1
        entry = stored.entries[0]
        assert entry.stage == PipelineStage.PLANNER
        assert entry.module == "planner"
        assert entry.details["input_keys"] == ["request"]
        assert entry.details["output_keys"] == ["plan"]
        assert entry.details["workflow_level"] is True

    def test_summarize_workflow(self) -> None:
        trace = DefaultIntegrationTrace()
        t = trace.create_trace("test-789")
        trace.record_workflow_stage(str(t.trace_id), PipelineStage.PLANNER, "planner", ["in"], ["out"], 30.0)
        trace.record_workflow_stage(str(t.trace_id), PipelineStage.ENERGY, "energy", ["in"], ["out"], 70.0)
        trace.complete_trace(str(t.trace_id), 100.0)
        summary = trace.summarize_workflow(str(t.trace_id))
        assert summary["stages_count"] == 2
        assert summary["total_duration_ms"] == 100.0
        assert "planner" in summary["module_breakdown"]
        assert "energy" in summary["module_breakdown"]

    def test_summarize_nonexistent(self) -> None:
        trace = DefaultIntegrationTrace()
        summary = trace.summarize_workflow("nonexistent")
        assert "error" in summary

    def test_get_workflow_summary(self) -> None:
        trace = DefaultIntegrationTrace()
        t = trace.create_trace("test-summary")
        trace.summarize_workflow(str(t.trace_id))
        summary = trace.get_workflow_summary(str(t.trace_id))
        assert summary is not None
        assert summary["trace_id"] == str(t.trace_id)

    def test_multiple_workflow_stages(self) -> None:
        trace = DefaultIntegrationTrace()
        t = trace.create_trace("test-multi")
        stages = [
            (PipelineStage.VALIDATION, "validation"),
            (PipelineStage.PLANNER, "planner"),
            (PipelineStage.WORKFLOW, "workflow"),
            (PipelineStage.ENERGY, "energy"),
        ]
        for stage, mod in stages:
            trace.record_workflow_stage(str(t.trace_id), stage, mod, ["in"], ["out"], 10.0)
        stored = trace.get_trace(str(t.trace_id))
        assert stored is not None
        assert len(stored.entries) == 4
        assert stored.total_duration_ms == 40.0


class TestIntegrationMetrics:
    """Verify workflow-spanning metrics."""

    def test_initialise(self) -> None:
        metrics = DefaultIntegrationMetrics()
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 0

    def test_record_phase_latency(self) -> None:
        metrics = DefaultIntegrationMetrics()
        metrics.record_phase_latency("planning", 100.0)
        metrics.record_phase_latency("planning", 200.0)
        summary = metrics.get_phase_summary()
        assert "planning" in summary
        assert summary["planning"]["average_ms"] == 150.0
        assert summary["planning"]["count"] == 2
        assert summary["planning"]["total_ms"] == 300.0

    def test_record_request_updates_metrics(self) -> None:
        metrics = DefaultIntegrationMetrics()
        stages = [PipelineStage.PLANNER, PipelineStage.ENERGY]
        metrics.record_request(success=True, duration_ms=150.0, stages=stages)
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 1
        assert snapshot.successful_requests == 1

    def test_workflow_snapshot_includes_phases(self) -> None:
        metrics = DefaultIntegrationMetrics()
        metrics.record_phase_latency("intake", 10.0)
        metrics.record_phase_latency("energy", 50.0)
        ws = metrics.get_workflow_snapshot()
        assert "phases" in ws
        assert "base" in ws
        assert ws["phase_count"] == len(ws["phases"])

    def test_multiple_requests(self) -> None:
        metrics = DefaultIntegrationMetrics()
        stages = [PipelineStage.VALIDATION, PipelineStage.PLANNER]
        metrics.record_request(success=True, duration_ms=100.0, stages=stages)
        metrics.record_request(success=True, duration_ms=200.0, stages=stages)
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 2
        assert snapshot.average_duration_ms == 150.0

    def test_phase_latency_with_no_data(self) -> None:
        metrics = DefaultIntegrationMetrics()
        summary = metrics.get_phase_summary()
        for phase in ("intake", "planning", "knowledge", "rules", "evidence",
                      "reasoning", "recommendation", "explainability", "review",
                      "action", "energy", "response"):
            assert phase in summary
            assert summary[phase]["count"] == 0
