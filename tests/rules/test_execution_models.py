"""Tests for Rule Manager execution-layer models."""

from __future__ import annotations

import uuid

import pytest

from adip.rules.contracts.models import Rule
from adip.rules.enums import RuleLifecycleStatus
from adip.rules.execution.models import (
    CompiledRule,
    ConflictReport,
    LifecycleHistoryEntry,
    TraceRecord,
    VersionRecord,
)


class TestCompiledRule:
    def test_defaults(self) -> None:
        rule = Rule()
        cr = CompiledRule(rule_id=rule.rule_id, rule=rule)
        assert cr.compiled_conditions == []
        assert cr.compiled_actions == []
        assert cr.metadata == {}
        assert cr.version == 1

    def test_custom_values(self) -> None:
        rule = Rule(name="test")
        cr = CompiledRule(
            rule_id=rule.rule_id,
            rule=rule,
            compiled_conditions=[{"field": "temp", "operator": "gt"}],
            compiled_actions=[{"action_type": "alert"}],
            version=3,
        )
        assert len(cr.compiled_conditions) == 1
        assert len(cr.compiled_actions) == 1
        assert cr.version == 3

    def test_version_constraint(self) -> None:
        rule = Rule()
        with pytest.raises(Exception):
            CompiledRule(rule_id=rule.rule_id, rule=rule, version=0)

    def test_uuid_generated(self) -> None:
        rule = Rule()
        cr = CompiledRule(rule_id=rule.rule_id, rule=rule)
        assert isinstance(cr.compiled_id, uuid.UUID)


class TestVersionRecord:
    def test_defaults(self) -> None:
        rule = Rule()
        vr = VersionRecord(rule_id=rule.rule_id)
        assert vr.version_number == 1
        assert vr.parent_version is None
        assert vr.created_by == ""
        assert vr.change_summary == ""
        assert vr.active is True

    def test_custom_values(self) -> None:
        rule = Rule()
        vr = VersionRecord(
            rule_id=rule.rule_id,
            version_number=3,
            parent_version=2,
            created_by="admin",
            change_summary="Updated priority",
            active=True,
        )
        assert vr.version_number == 3
        assert vr.parent_version == 2
        assert vr.created_by == "admin"

    def test_version_constraint(self) -> None:
        rule = Rule()
        with pytest.raises(Exception):
            VersionRecord(rule_id=rule.rule_id, version_number=0)

    def test_uuid_generated(self) -> None:
        rule = Rule()
        vr = VersionRecord(rule_id=rule.rule_id)
        assert isinstance(vr.version_id, uuid.UUID)


class TestLifecycleHistoryEntry:
    def test_defaults(self) -> None:
        rule = Rule()
        entry = LifecycleHistoryEntry(
            rule_id=rule.rule_id,
            to_status=RuleLifecycleStatus.ACTIVE,
        )
        assert entry.from_status is None
        assert entry.reason == ""
        assert entry.changed_by == ""

    def test_custom_values(self) -> None:
        rule = Rule()
        entry = LifecycleHistoryEntry(
            rule_id=rule.rule_id,
            from_status=RuleLifecycleStatus.DRAFT,
            to_status=RuleLifecycleStatus.UNDER_REVIEW,
            reason="Ready for review",
            changed_by="user-1",
        )
        assert entry.from_status == RuleLifecycleStatus.DRAFT
        assert entry.to_status == RuleLifecycleStatus.UNDER_REVIEW
        assert entry.reason == "Ready for review"

    def test_uuid_generated(self) -> None:
        rule = Rule()
        entry = LifecycleHistoryEntry(rule_id=rule.rule_id, to_status=RuleLifecycleStatus.DRAFT)
        assert isinstance(entry.entry_id, uuid.UUID)


class TestConflictReport:
    def test_defaults(self) -> None:
        rule = Rule()
        cr = ConflictReport(rule_id=rule.rule_id, conflicting_rule_id=uuid.uuid4())
        assert cr.conflict_type == ""
        assert cr.description == ""
        assert cr.resolution == ""
        assert cr.resolved_by == ""

    def test_custom_values(self) -> None:
        rule = Rule()
        cr = ConflictReport(
            rule_id=rule.rule_id,
            conflicting_rule_id=uuid.uuid4(),
            conflict_type="priority_inversion",
            description="Rule A has higher priority than Rule B but B evaluated first",
            resolution="Reordered by priority",
            resolved_by="PriorityEngine",
        )
        assert cr.conflict_type == "priority_inversion"
        assert "Rule A" in cr.description

    def test_uuid_generated(self) -> None:
        rule = Rule()
        cr = ConflictReport(rule_id=rule.rule_id, conflicting_rule_id=uuid.uuid4())
        assert isinstance(cr.report_id, uuid.UUID)


class TestTraceRecord:
    def test_defaults(self) -> None:
        tr = TraceRecord(stage_name="validation", operation="validate_rule")
        assert tr.rule_id is None
        assert tr.version is None
        assert tr.lifecycle_state == ""
        assert tr.evaluation_strategy == ""
        assert tr.success is True
        assert tr.warnings == []
        assert tr.errors == []

    def test_custom_values(self) -> None:
        tr = TraceRecord(
            stage_name="evaluation",
            operation="evaluate_ruleset",
            rule_id=uuid.uuid4(),
            version=2,
            lifecycle_state="ACTIVE",
            domain="ENERGY",
            evaluation_strategy="SEQUENTIAL",
            success=True,
            warnings=["Low confidence"],
            correlation_id="corr-123",
        )
        assert tr.stage_name == "evaluation"
        assert tr.version == 2
        assert tr.lifecycle_state == "ACTIVE"
        assert tr.evaluation_strategy == "SEQUENTIAL"
        assert len(tr.warnings) == 1

    def test_version_constraint(self) -> None:
        with pytest.raises(Exception):
            TraceRecord(stage_name="test", operation="test", version=0)

    def test_uuid_generated(self) -> None:
        tr = TraceRecord(stage_name="test", operation="test")
        assert isinstance(tr.trace_id, uuid.UUID)
