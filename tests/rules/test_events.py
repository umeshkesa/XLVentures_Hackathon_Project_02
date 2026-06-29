"""Tests for Rule Manager events."""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest

from adip.rules.contracts.events import (
    EventVersion,
    RuleActivated,
    RuleArchived,
    RuleConflictDetected,
    RuleCreated,
    RuleEvaluated,
    RuleUpdated,
)
from adip.rules.enums import RuleDomain, RuleLifecycleStatus, RuleType


class TestEventVersion:
    def test_version_string(self) -> None:
        assert EventVersion == "1.0.0"


class TestRuleEvent:
    def test_defaults(self) -> None:
        event = RuleCreated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.BUSINESS,
        )
        assert event.domain == RuleDomain.SYSTEM
        assert event.correlation_id == ""
        assert event.payload == {}
        assert isinstance(event.timestamp, datetime)

    def test_custom_values(self) -> None:
        event = RuleCreated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.SAFETY,
            domain=RuleDomain.ENERGY,
            correlation_id="corr-789",
            payload={"source": "manual"},
        )
        assert event.domain == RuleDomain.ENERGY
        assert event.correlation_id == "corr-789"
        assert event.payload["source"] == "manual"

    def test_uuid_generated(self) -> None:
        event = RuleCreated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.BUSINESS,
        )
        assert isinstance(event.event_id, uuid.UUID)


class TestRuleCreated:
    def test_defaults(self) -> None:
        event = RuleCreated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.BUSINESS,
        )
        assert event.version == 1

    def test_custom_version(self) -> None:
        event = RuleCreated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.COMPLIANCE,
            version=3,
        )
        assert event.version == 3

    def test_version_constraint(self) -> None:
        with pytest.raises(Exception):
            RuleCreated(rule_id=uuid.uuid4(), rule_type=RuleType.BUSINESS, version=0)


class TestRuleUpdated:
    def test_defaults(self) -> None:
        event = RuleUpdated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.BUSINESS,
        )
        assert event.previous_version == 0
        assert event.new_version == 1

    def test_custom_versions(self) -> None:
        event = RuleUpdated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.SAFETY,
            previous_version=2,
            new_version=3,
        )
        assert event.previous_version == 2
        assert event.new_version == 3

    def test_version_constraints(self) -> None:
        with pytest.raises(Exception):
            RuleUpdated(rule_id=uuid.uuid4(), rule_type=RuleType.BUSINESS, previous_version=-1)
        with pytest.raises(Exception):
            RuleUpdated(rule_id=uuid.uuid4(), rule_type=RuleType.BUSINESS, new_version=0)


class TestRuleActivated:
    def test_custom_values(self) -> None:
        event = RuleActivated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.WORKFLOW,
            previous_status=RuleLifecycleStatus.APPROVED,
            activated_by="admin-1",
        )
        assert event.previous_status == RuleLifecycleStatus.APPROVED
        assert event.activated_by == "admin-1"


class TestRuleEvaluated:
    def test_defaults(self) -> None:
        event = RuleEvaluated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.BUSINESS,
            context_id=uuid.uuid4(),
        )
        assert event.matched is False
        assert event.decision == ""
        assert event.evaluation_time_ms == 0.0

    def test_custom_values(self) -> None:
        event = RuleEvaluated(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.SAFETY,
            context_id=uuid.uuid4(),
            matched=True,
            decision="allow",
            evaluation_time_ms=15.3,
        )
        assert event.matched is True
        assert event.decision == "allow"
        assert event.evaluation_time_ms == 15.3


class TestRuleConflictDetected:
    def test_custom_values(self) -> None:
        rule_id = uuid.uuid4()
        conflicting_id = uuid.uuid4()
        event = RuleConflictDetected(
            rule_id=rule_id,
            rule_type=RuleType.BUSINESS,
            conflicting_rule_id=conflicting_id,
            conflicting_rule_name="Priority Inversion Rule",
            conflict_type="priority_inversion",
            resolution="adjusted priority",
        )
        assert event.conflicting_rule_id == conflicting_id
        assert event.conflicting_rule_name == "Priority Inversion Rule"
        assert event.conflict_type == "priority_inversion"
        assert event.resolution == "adjusted priority"


class TestRuleArchived:
    def test_defaults(self) -> None:
        event = RuleArchived(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.BUSINESS,
        )
        assert event.reason == ""

    def test_with_reason(self) -> None:
        event = RuleArchived(
            rule_id=uuid.uuid4(),
            rule_type=RuleType.MAINTENANCE,
            reason="Superseded by v2",
        )
        assert event.reason == "Superseded by v2"
