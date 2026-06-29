"""Tests for Rule Manager domain models."""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from adip.rules.contracts.models import (
    Rule,
    RuleAction,
    RuleCondition,
    RuleContext,
    RuleDecision,
    RuleEvaluation,
    RuleHealth,
    RuleMetrics,
    RulePolicy,
    RuleSession,
    RuleSet,
)
from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
    RuleLifecycleStatus,
    RuleType,
)


class TestRuleCondition:
    def test_defaults(self) -> None:
        cond = RuleCondition()
        assert cond.field == ""
        assert cond.operator == ""
        assert cond.value == ""
        assert cond.logic == "AND"
        assert cond.conditions == []
        assert cond.metadata == {}

    def test_custom_values(self) -> None:
        cond = RuleCondition(
            field="temperature",
            operator="gt",
            value="100",
            logic="OR",
        )
        assert cond.field == "temperature"
        assert cond.operator == "gt"
        assert cond.value == "100"
        assert cond.logic == "OR"

    def test_nested_conditions(self) -> None:
        inner = RuleCondition(field="pressure", operator="lt", value="50")
        outer = RuleCondition(
            field="",
            operator="",
            value="",
            logic="AND",
            conditions=[inner],
        )
        assert len(outer.conditions) == 1
        assert outer.conditions[0].field == "pressure"

    def test_uuid_generated(self) -> None:
        cond = RuleCondition()
        assert isinstance(cond.condition_id, uuid.UUID)


class TestRuleAction:
    def test_defaults(self) -> None:
        action = RuleAction()
        assert action.action_type == ""
        assert action.parameters == {}
        assert action.priority == 0
        assert action.metadata == {}

    def test_custom_values(self) -> None:
        action = RuleAction(
            action_type="approve",
            parameters={"limit": 10000},
            priority=10,
        )
        assert action.action_type == "approve"
        assert action.parameters["limit"] == 10000
        assert action.priority == 10

    def test_uuid_generated(self) -> None:
        action = RuleAction()
        assert isinstance(action.action_id, uuid.UUID)


class TestRule:
    def test_defaults(self) -> None:
        rule = Rule()
        assert rule.name == ""
        assert rule.description == ""
        assert rule.domain == RuleDomain.SYSTEM
        assert rule.rule_type == RuleType.BUSINESS
        assert rule.status == RuleLifecycleStatus.DRAFT
        assert rule.conditions == []
        assert rule.actions == []
        assert rule.priority == 0
        assert rule.version == 1
        assert rule.enabled is True
        assert rule.namespace == "default"

    def test_custom_values(self) -> None:
        rule = Rule(
            name="High Temperature Alert",
            description="Alert when temperature exceeds threshold",
            domain=RuleDomain.ENERGY,
            rule_type=RuleType.SAFETY,
            priority=100,
            enabled=False,
        )
        assert rule.name == "High Temperature Alert"
        assert rule.domain == RuleDomain.ENERGY
        assert rule.rule_type == RuleType.SAFETY
        assert rule.priority == 100
        assert rule.enabled is False

    def test_with_condition(self) -> None:
        cond = RuleCondition(field="temperature", operator="gt", value="100")
        rule = Rule(
            name="Temp Check",
            conditions=[cond],
        )
        assert len(rule.conditions) == 1
        assert rule.conditions[0].field == "temperature"

    def test_with_action(self) -> None:
        action = RuleAction(action_type="alert", parameters={"channel": "slack"})
        rule = Rule(
            name="Alert Rule",
            actions=[action],
        )
        assert len(rule.actions) == 1
        assert rule.actions[0].action_type == "alert"

    def test_version_constraint(self) -> None:
        with pytest.raises(ValidationError):
            Rule(version=0)

    def test_uuid_generated(self) -> None:
        rule = Rule()
        assert isinstance(rule.rule_id, uuid.UUID)

    def test_timestamps(self) -> None:
        rule = Rule()
        assert isinstance(rule.created_at, datetime)
        assert isinstance(rule.updated_at, datetime)

    def test_expires_at_optional(self) -> None:
        rule = Rule()
        assert rule.expires_at is None

    def test_extra_dict(self) -> None:
        rule = Rule(extra={"custom_key": "custom_value"})
        assert rule.extra["custom_key"] == "custom_value"


class TestRuleSet:
    def test_defaults(self) -> None:
        rs = RuleSet()
        assert rs.name == ""
        assert rs.description == ""
        assert rs.domain == RuleDomain.SYSTEM
        assert rs.rules == []
        assert rs.evaluation_strategy == EvaluationStrategyType.SEQUENTIAL
        assert rs.status == RuleLifecycleStatus.DRAFT
        assert rs.version == 1
        assert rs.enabled is True

    def test_with_rules(self) -> None:
        rule1 = Rule(name="Rule 1")
        rule2 = Rule(name="Rule 2")
        rs = RuleSet(
            name="Safety Checks",
            rules=[rule1, rule2],
            evaluation_strategy=EvaluationStrategyType.PRIORITY,
        )
        assert rs.name == "Safety Checks"
        assert len(rs.rules) == 2
        assert rs.evaluation_strategy == EvaluationStrategyType.PRIORITY

    def test_version_constraint(self) -> None:
        with pytest.raises(ValidationError):
            RuleSet(version=0)

    def test_uuid_generated(self) -> None:
        rs = RuleSet()
        assert isinstance(rs.ruleset_id, uuid.UUID)


class TestRuleContext:
    def test_defaults(self) -> None:
        ctx = RuleContext()
        assert ctx.domain == RuleDomain.SYSTEM
        assert ctx.inputs == {}
        assert ctx.attributes == {}
        assert ctx.user_id == ""
        assert ctx.namespace == "default"
        assert ctx.correlation_id == ""

    def test_custom_values(self) -> None:
        ctx = RuleContext(
            domain=RuleDomain.ENERGY,
            inputs={"temperature": 95, "pressure": 40},
            attributes={"asset_type": "turbine"},
            user_id="system-1",
            correlation_id="corr-123",
        )
        assert ctx.domain == RuleDomain.ENERGY
        assert ctx.inputs["temperature"] == 95
        assert ctx.attributes["asset_type"] == "turbine"
        assert ctx.user_id == "system-1"
        assert ctx.correlation_id == "corr-123"

    def test_uuid_generated(self) -> None:
        ctx = RuleContext()
        assert isinstance(ctx.context_id, uuid.UUID)


class TestRuleDecision:
    def test_defaults(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(
            context_id=ctx.context_id,
            rule_id=rule.rule_id,
        )
        assert dec.decision == ""
        assert dec.matched is False
        assert dec.actions_taken == []
        assert dec.reason == ""
        assert dec.confidence == 1.0
        assert dec.ruleset_id is None

    def test_custom_values(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(
            context_id=ctx.context_id,
            rule_id=rule.rule_id,
            decision="allow",
            matched=True,
            actions_taken=["log", "notify"],
            reason="Temperature within safe range",
            confidence=0.95,
            evaluation_time_ms=12.5,
        )
        assert dec.decision == "allow"
        assert dec.matched is True
        assert len(dec.actions_taken) == 2
        assert dec.reason == "Temperature within safe range"
        assert dec.confidence == 0.95
        assert dec.evaluation_time_ms == 12.5

    def test_confidence_range(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        with pytest.raises(ValidationError):
            RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id, confidence=1.5)
        with pytest.raises(ValidationError):
            RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id, confidence=-0.1)

    def test_uuid_generated(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert isinstance(dec.decision_id, uuid.UUID)


class TestRuleEvaluation:
    def test_defaults(self) -> None:
        ctx = RuleContext()
        eval_ = RuleEvaluation(context=ctx)
        assert eval_.rules_evaluated == []
        assert eval_.decisions == []
        assert eval_.conflicts_detected == []
        assert eval_.evaluation_strategy == EvaluationStrategyType.SEQUENTIAL
        assert eval_.status == "COMPLETED"
        assert eval_.total_evaluation_time_ms == 0.0

    def test_with_decisions(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id, decision="allow")
        eval_ = RuleEvaluation(
            context=ctx,
            decisions=[dec],
            rules_evaluated=[rule.rule_id],
            status="COMPLETED",
            total_evaluation_time_ms=45.2,
        )
        assert len(eval_.decisions) == 1
        assert len(eval_.rules_evaluated) == 1
        assert eval_.status == "COMPLETED"
        assert eval_.total_evaluation_time_ms == 45.2

    def test_failed_evaluation(self) -> None:
        ctx = RuleContext()
        eval_ = RuleEvaluation(
            context=ctx,
            status="FAILED",
            error_message="Rule evaluation timed out",
        )
        assert eval_.status == "FAILED"
        assert eval_.error_message == "Rule evaluation timed out"

    def test_uuid_generated(self) -> None:
        ctx = RuleContext()
        eval_ = RuleEvaluation(context=ctx)
        assert isinstance(eval_.evaluation_id, uuid.UUID)


class TestRulePolicy:
    def test_defaults(self) -> None:
        policy = RulePolicy()
        assert policy.name == ""
        assert policy.domain == RuleDomain.SYSTEM
        assert policy.allowed_rule_types == []
        assert policy.allowed_actions == []
        assert policy.max_rules_per_set == 100
        assert policy.default_decision == "DENY"
        assert policy.enabled is True

    def test_custom_values(self) -> None:
        policy = RulePolicy(
            name="Energy Safety Policy",
            description="Safety rules for energy domain",
            domain=RuleDomain.ENERGY,
            allowed_rule_types=[RuleType.SAFETY, RuleType.COMPLIANCE],
            allowed_actions=["alert", "shutdown", "notify"],
            max_rules_per_set=50,
            default_decision="ALLOW",
        )
        assert policy.name == "Energy Safety Policy"
        assert len(policy.allowed_rule_types) == 2
        assert len(policy.allowed_actions) == 3
        assert policy.max_rules_per_set == 50
        assert policy.default_decision == "ALLOW"

    def test_version_constraint(self) -> None:
        with pytest.raises(ValidationError):
            RulePolicy(version=0)

    def test_uuid_generated(self) -> None:
        policy = RulePolicy()
        assert isinstance(policy.policy_id, uuid.UUID)

    def test_max_evaluation_depth_valid(self) -> None:
        with pytest.raises(ValidationError):
            RulePolicy(max_evaluation_depth=0)


class TestRuleHealth:
    def test_defaults(self) -> None:
        health = RuleHealth()
        assert health.overall_status == "HEALTHY"
        assert health.error_count == 0
        assert health.error_rate == 0.0
        assert health.total_rules == 0
        assert health.total_evaluations == 0

    def test_custom_values(self) -> None:
        health = RuleHealth(
            overall_status="DEGRADED",
            evaluator_status="DEGRADED",
            error_count=5,
            error_rate=0.05,
            total_rules=150,
            total_rulesets=10,
            total_evaluations=5000,
            rule_domains=["ENERGY", "SYSTEM", "SAFETY"],
        )
        assert health.overall_status == "DEGRADED"
        assert health.error_count == 5
        assert health.error_rate == 0.05
        assert health.total_rules == 150
        assert len(health.rule_domains) == 3

    def test_is_healthy(self) -> None:
        healthy = RuleHealth()
        assert healthy.is_healthy() is True
        degraded = RuleHealth(overall_status="DEGRADED")
        assert degraded.is_healthy() is False
        unhealthy = RuleHealth(overall_status="UNHEALTHY")
        assert unhealthy.is_healthy() is False


class TestRuleMetrics:
    def test_defaults(self) -> None:
        metrics = RuleMetrics()
        assert metrics.rules_total == 0
        assert metrics.rulesets_total == 0
        assert metrics.evaluations_total == 0
        assert metrics.decisions_total == 0
        assert metrics.conflicts_total == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.strategy_usage == {}

    def test_custom_values(self) -> None:
        metrics = RuleMetrics(
            rules_total=200,
            rulesets_total=15,
            evaluations_total=10000,
            decisions_total=9500,
            conflicts_total=23,
            cache_hits=500,
            cache_misses=50,
            rules_per_domain={"ENERGY": 80, "SYSTEM": 70, "SAFETY": 50},
            strategy_usage={"SEQUENTIAL": 100, "PRIORITY": 50},
            domain_usage={"ENERGY": 200, "SYSTEM": 150},
        )
        assert metrics.rules_total == 200
        assert metrics.cache_hits == 500
        assert metrics.strategy_usage["SEQUENTIAL"] == 100
        assert metrics.rules_per_domain["ENERGY"] == 80


class TestRuleSession:
    def test_defaults(self) -> None:
        session = RuleSession()
        assert session.domain == RuleDomain.SYSTEM
        assert session.user_id == ""
        assert session.correlation_id == ""
        assert session.evaluation_strategy == EvaluationStrategyType.SEQUENTIAL
        assert session.rules_evaluated == []
        assert session.decisions_made == []
        assert session.cache_hits == 0
        assert session.completed_at is None

    def test_custom_values(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        session = RuleSession(
            domain=RuleDomain.ENERGY,
            user_id="operator-1",
            correlation_id="corr-456",
            evaluation_strategy=EvaluationStrategyType.PRIORITY,
            rules_evaluated=["rule-1", "rule-2"],
            decisions_made=[dec],
            cache_hits=3,
        )
        assert session.domain == RuleDomain.ENERGY
        assert session.user_id == "operator-1"
        assert session.evaluation_strategy == EvaluationStrategyType.PRIORITY
        assert len(session.rules_evaluated) == 2
        assert len(session.decisions_made) == 1

    def test_uuid_generated(self) -> None:
        session = RuleSession()
        assert isinstance(session.session_id, uuid.UUID)

    def test_duration_calculation(self) -> None:
        session = RuleSession(duration_ms=150.5)
        assert session.duration_ms == 150.5
