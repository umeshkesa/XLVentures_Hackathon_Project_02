"""Smoke tests for platform trace management."""

from __future__ import annotations

from adip.platform.enums import PipelineStage
from adip.platform.orchestration.trace_manager import DefaultTraceManager


class TestTraceManagement:
    """Verify unified tracing across all modules."""

    def test_create_trace(self) -> None:
        """Verify trace creation."""
        trace = DefaultTraceManager()
        t = trace.create_trace("corr-123")
        assert t.correlation_id == "corr-123"
        assert not t.completed
        assert t.entries == []
        assert t.total_duration_ms == 0.0

    def test_record_stage(self) -> None:
        """Verify stage recording."""
        trace = DefaultTraceManager()
        t = trace.create_trace("corr-456")
        trace.record_stage(
            trace_id=str(t.trace_id),
            stage=PipelineStage.PLANNER,
            module="planner",
            status="success",
            duration_ms=42.0,
            details={"output": "ok"},
        )
        stored = trace.get_trace(str(t.trace_id))
        assert stored is not None
        assert len(stored.entries) == 1
        assert stored.entries[0].stage == PipelineStage.PLANNER
        assert stored.entries[0].duration_ms == 42.0
        assert stored.total_duration_ms == 42.0

    def test_record_multiple_stages(self) -> None:
        """Verify multiple stages accumulated correctly."""
        trace = DefaultTraceManager()
        t = trace.create_trace("corr-multi")
        tid = str(t.trace_id)
        trace.record_stage(tid, PipelineStage.PLANNER, "planner", "success", 10.0)
        trace.record_stage(tid, PipelineStage.MEMORY, "memory", "success", 20.0)
        trace.record_stage(tid, PipelineStage.ENERGY, "energy", "failure", 5.0)
        stored = trace.get_trace(tid)
        assert stored is not None
        assert len(stored.entries) == 3
        assert stored.total_duration_ms == 35.0

    def test_complete_trace(self) -> None:
        """Verify trace completion."""
        trace = DefaultTraceManager()
        t = trace.create_trace("corr-complete")
        trace.complete_trace(str(t.trace_id), 100.0)
        stored = trace.get_trace(str(t.trace_id))
        assert stored is not None
        assert stored.completed
        assert stored.total_duration_ms == 100.0

    def test_list_traces(self) -> None:
        """Verify listing all traces."""
        trace = DefaultTraceManager()
        trace.create_trace("corr-1")
        trace.create_trace("corr-2")
        trace.create_trace("corr-3")
        all_traces = trace.list_traces()
        assert len(all_traces) == 3

    def test_get_nonexistent_trace(self) -> None:
        """Verify getting a nonexistent trace returns None."""
        trace = DefaultTraceManager()
        result = trace.get_trace("nonexistent")
        assert result is None

    def test_clear(self) -> None:
        """Verify clearing traces."""
        trace = DefaultTraceManager()
        trace.create_trace("corr-1")
        trace.create_trace("corr-2")
        trace.clear()
        assert len(trace.list_traces()) == 0
