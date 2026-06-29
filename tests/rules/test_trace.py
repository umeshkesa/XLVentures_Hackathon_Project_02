"""Tests for RuleTrace."""

from __future__ import annotations

from adip.rules.execution.models import TraceRecord
from adip.rules.execution.trace import RuleTrace


class TestRuleTrace:
    def test_record(self) -> None:
        trace = RuleTrace()
        record = TraceRecord(stage_name="validation", operation="validate_rule")
        trace.record(record)
        assert trace.count() == 1

    def test_record_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_stage(
            stage_name="evaluation",
            operation="evaluate_ruleset",
            domain="ENERGY",
            evaluation_strategy="SEQUENTIAL",
            correlation_id="corr-123",
        )
        assert record.stage_name == "evaluation"
        assert record.domain == "ENERGY"
        assert record.evaluation_strategy == "SEQUENTIAL"
        assert trace.count() == 1

    def test_record_stage_with_warnings(self) -> None:
        trace = RuleTrace()
        record = trace.record_stage(
            stage_name="validation",
            operation="validate_rule",
            warnings=["Low priority"],
            success=True,
        )
        assert len(record.warnings) == 1
        assert record.success is True

    def test_record_stage_with_errors(self) -> None:
        trace = RuleTrace()
        record = trace.record_stage(
            stage_name="compilation",
            operation="compile_rule",
            errors=["Compilation failed"],
            success=False,
        )
        assert len(record.errors) == 1
        assert record.success is False

    def test_get_by_operation(self) -> None:
        trace = RuleTrace()
        trace.record_stage("eval", "evaluate")
        trace.record_stage("val", "validate")
        trace.record_stage("eval2", "evaluate")
        results = trace.get_by_operation("evaluate")
        assert len(results) == 2

    def test_get_by_stage(self) -> None:
        trace = RuleTrace()
        trace.record_stage("validation", "validate")
        trace.record_stage("evaluation", "evaluate")
        results = trace.get_by_stage("validation")
        assert len(results) == 1

    def test_get_recent(self) -> None:
        trace = RuleTrace()
        for i in range(5):
            trace.record_stage(f"stage_{i}", "test")
        recent = trace.get_recent(3)
        assert len(recent) == 3

    def test_clear(self) -> None:
        trace = RuleTrace()
        trace.record_stage("test", "test")
        trace.clear()
        assert trace.count() == 0

    def test_count(self) -> None:
        trace = RuleTrace()
        assert trace.count() == 0
        trace.record_stage("a", "op")
        assert trace.count() == 1
        trace.record_stage("b", "op")
        assert trace.count() == 2
