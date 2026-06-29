"""Tests for AggregatedTracing."""

from __future__ import annotations

from adip.memory.enums import MemoryOperation
from adip.memory.orchestration.tracing import AggregatedTracing


class TestAggregatedTracing:
    def test_initial_empty(self) -> None:
        tracing = AggregatedTracing()
        assert tracing.get_traces() == []

    def test_record_stage(self) -> None:
        tracing = AggregatedTracing()
        entry = tracing.record_stage(
            stage_name="test.stage",
            operation=MemoryOperation.CREATE,
            memory_id="mem-1",
            session_id="sess-1",
            correlation_id="corr-1",
            domain="SYSTEM",
            namespace="default",
            tier="HOT",
            duration_ms=10.5,
            success=True,
        )
        assert entry["stage_name"] == "test.stage"
        assert entry["operation"] == "CREATE"
        assert entry["memory_id"] == "mem-1"
        assert entry["session_id"] == "sess-1"
        assert entry["correlation_id"] == "corr-1"
        assert entry["duration_ms"] == 10.5

    def test_get_traces_filter_by_stage(self) -> None:
        tracing = AggregatedTracing()
        tracing.record_stage("stage.a", MemoryOperation.CREATE)
        tracing.record_stage("stage.b", MemoryOperation.READ)
        results = tracing.get_traces(stage_name="stage.a")
        assert len(results) == 1
        assert results[0]["stage_name"] == "stage.a"

    def test_get_traces_filter_by_session(self) -> None:
        tracing = AggregatedTracing()
        tracing.record_stage("s1", MemoryOperation.CREATE, session_id="session-1")
        tracing.record_stage("s2", MemoryOperation.READ, session_id="session-2")
        results = tracing.get_traces(session_id="session-1")
        assert len(results) == 1

    def test_get_traces_filter_by_operation(self) -> None:
        tracing = AggregatedTracing()
        tracing.record_stage("s1", MemoryOperation.CREATE)
        tracing.record_stage("s2", MemoryOperation.READ)
        results = tracing.get_traces(operation=MemoryOperation.CREATE)
        assert len(results) == 1
        assert results[0]["operation"] == "CREATE"

    def test_clear(self) -> None:
        tracing = AggregatedTracing()
        tracing.record_stage("s1", MemoryOperation.CREATE)
        tracing.clear()
        assert tracing.get_traces() == []

    def test_limit(self) -> None:
        tracing = AggregatedTracing()
        for i in range(10):
            tracing.record_stage(f"s{i}", MemoryOperation.CREATE)
        results = tracing.get_traces(limit=3)
        assert len(results) == 3

    def test_warnings_and_errors(self) -> None:
        tracing = AggregatedTracing()
        entry = tracing.record_stage(
            stage_name="test",
            operation=MemoryOperation.UPDATE,
            warnings=["slow operation"],
            errors=["timeout"],
            success=False,
        )
        assert entry["warnings"] == ["slow operation"]
        assert entry["errors"] == ["timeout"]
        assert entry["success"] is False
