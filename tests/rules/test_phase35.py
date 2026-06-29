"""Tests for Rule Manager Phase 3.5 — Enterprise Refinement & Interface Freeze.

Tests cover enhanced RuleDecision, RuleConfidence, RuleHealth, RuleMetrics,
RuleSet, RuleExplainabilityMetadata, RuleTrace stage tracking, and
RuleMetricsCollector extensions. All existing Phase 1–3 tests must
continue to pass without modification.
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.rules.contracts.models import (
    Rule,
    RuleConfidence,
    RuleContext,
    RuleDecision,
    RuleEvaluation,
    RuleExplainabilityMetadata,
    RuleHealth,
    RuleMetrics,
    RuleSet,
)
from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
)
from adip.rules.execution.metrics import RuleMetricsCollector
from adip.rules.execution.trace import RuleTrace
from adip.rules.orchestration.confidence import RuleConfidenceCalculator

# ═════════════════════════════════════════════════════════════════════════════
# RuleDecision — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleDecisionPhase35:
    """Tests for enhanced RuleDecision fields (Phase 3.5)."""

    def test_defaults_include_evaluation_id(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert isinstance(dec.evaluation_id, uuid.UUID)
        assert dec.evaluation_id is not None

    def test_defaults_include_applied_rules(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.applied_rules == []

    def test_defaults_include_skipped_rules(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.skipped_rules == []

    def test_defaults_include_ignored_rules(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.ignored_rules == []

    def test_defaults_include_conflicting_rules(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.conflicting_rules == []

    def test_defaults_include_priority_resolution(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.priority_resolution == ""

    def test_defaults_include_allow_or_deny(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.allow_or_deny == "deny"

    def test_defaults_include_reasoning(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id)
        assert dec.reasoning == ""

    def test_custom_values_all_new_fields(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        eval_id = uuid.uuid4()
        dec = RuleDecision(
            evaluation_id=eval_id,
            context_id=ctx.context_id,
            rule_id=rule.rule_id,
            applied_rules=["rule-1", "rule-2"],
            skipped_rules=["rule-3"],
            ignored_rules=["rule-4"],
            conflicting_rules=["rule-5"],
            priority_resolution="highest_priority_wins",
            decision="allow",
            allow_or_deny="allow",
            matched=True,
            reasoning="Applied rule-1 (priority 100) over rule-2 (priority 50)",
        )
        assert dec.evaluation_id == eval_id
        assert dec.applied_rules == ["rule-1", "rule-2"]
        assert dec.skipped_rules == ["rule-3"]
        assert dec.ignored_rules == ["rule-4"]
        assert dec.conflicting_rules == ["rule-5"]
        assert dec.priority_resolution == "highest_priority_wins"
        assert dec.allow_or_deny == "allow"
        assert dec.reasoning == "Applied rule-1 (priority 100) over rule-2 (priority 50)"

    def test_existing_fields_still_work(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(
            context_id=ctx.context_id,
            rule_id=rule.rule_id,
            decision="deny",
            confidence=0.85,
            matched=False,
        )
        assert dec.decision == "deny"
        assert dec.confidence == 0.85
        assert dec.matched is False


# ═════════════════════════════════════════════════════════════════════════════
# RuleConfidence — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleConfidencePhase35:
    """Tests for enhanced RuleConfidence with lifecycle_validity."""

    def test_defaults_include_lifecycle_validity(self) -> None:
        conf = RuleConfidence()
        assert conf.lifecycle_validity == 1.0
        assert 0.0 <= conf.lifecycle_validity <= 1.0

    def test_custom_lifecycle_validity(self) -> None:
        conf = RuleConfidence(
            overall_confidence=0.75,
            rule_completeness=0.8,
            version_freshness=0.9,
            lifecycle_validity=0.85,
            conflict_quality=0.7,
            policy_compliance=1.0,
            evaluation_coverage=0.6,
        )
        assert conf.lifecycle_validity == 0.85
        assert conf.overall_confidence == 0.75

    def test_lifecycle_validity_range(self) -> None:
        with pytest.raises(ValidationError):
            RuleConfidence(lifecycle_validity=-0.1)
        with pytest.raises(ValidationError):
            RuleConfidence(lifecycle_validity=1.5)

    def test_all_scores_bounded(self) -> None:
        conf = RuleConfidence(
            overall_confidence=0.5,
            rule_completeness=0.5,
            version_freshness=0.5,
            lifecycle_validity=0.5,
            conflict_quality=0.5,
            policy_compliance=0.5,
            evaluation_coverage=0.5,
        )
        for val in [conf.overall_confidence, conf.rule_completeness,
                     conf.version_freshness, conf.lifecycle_validity,
                     conf.conflict_quality, conf.policy_compliance,
                     conf.evaluation_coverage]:
            assert 0.0 <= val <= 1.0


# ═════════════════════════════════════════════════════════════════════════════
# RuleHealth — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleHealthPhase35:
    """Tests for enhanced RuleHealth with additional status fields."""

    def test_defaults_include_policy_status(self) -> None:
        health = RuleHealth()
        assert health.policy_status == "HEALTHY"

    def test_defaults_include_version_status(self) -> None:
        health = RuleHealth()
        assert health.version_status == "HEALTHY"

    def test_defaults_include_lifecycle_status(self) -> None:
        health = RuleHealth()
        assert health.lifecycle_status == "HEALTHY"

    def test_defaults_include_average_latency(self) -> None:
        health = RuleHealth()
        assert health.average_latency_ms == 0.0

    def test_defaults_include_rules_evaluated(self) -> None:
        health = RuleHealth()
        assert health.rules_evaluated == 0

    def test_custom_health_with_new_fields(self) -> None:
        health = RuleHealth(
            overall_status="DEGRADED",
            validator_status="HEALTHY",
            parser_status="HEALTHY",
            compiler_status="HEALTHY",
            evaluator_status="DEGRADED",
            cache_status="HEALTHY",
            policy_status="HEALTHY",
            version_status="HEALTHY",
            lifecycle_status="HEALTHY",
            average_latency_ms=15.5,
            average_evaluation_time_ms=12.3,
            error_rate=0.02,
            total_rules=100,
            rules_evaluated=500,
            rule_domains=["ENERGY", "SYSTEM"],
        )
        assert health.overall_status == "DEGRADED"
        assert health.evaluator_status == "DEGRADED"
        assert health.policy_status == "HEALTHY"
        assert health.average_latency_ms == 15.5
        assert health.rules_evaluated == 500

    def test_health_reordered_fields(self) -> None:
        """Verify fields exist regardless of order."""
        health = RuleHealth()
        assert hasattr(health, "validator_status")
        assert hasattr(health, "policy_status")
        assert hasattr(health, "version_status")
        assert hasattr(health, "lifecycle_status")
        assert hasattr(health, "average_latency_ms")
        assert hasattr(health, "rules_evaluated")

    def test_is_healthy_still_works(self) -> None:
        health = RuleHealth()
        assert health.is_healthy() is True
        degraded = RuleHealth(overall_status="DEGRADED")
        assert degraded.is_healthy() is False


# ═════════════════════════════════════════════════════════════════════════════
# RuleMetrics — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleMetricsPhase35:
    """Tests for enhanced RuleMetrics with category, scope, version tracking."""

    def test_defaults_include_rules_per_category(self) -> None:
        metrics = RuleMetrics()
        assert metrics.rules_per_category == {}

    def test_defaults_include_rules_per_scope(self) -> None:
        metrics = RuleMetrics()
        assert metrics.rules_per_scope == {}

    def test_defaults_include_version_usage(self) -> None:
        metrics = RuleMetrics()
        assert metrics.version_usage == {}

    def test_custom_metrics_with_new_fields(self) -> None:
        metrics = RuleMetrics(
            rules_total=200,
            rulesets_total=15,
            evaluations_total=5000,
            decisions_total=4800,
            conflicts_total=25,
            rules_per_domain={"ENERGY": 80, "SYSTEM": 70, "SAFETY": 50},
            rules_per_type={"SAFETY": 60, "COMPLIANCE": 40},
            rules_per_category={"safety": 60, "compliance": 40, "maintenance": 100},
            rules_per_scope={"global": 150, "local": 50},
            strategy_usage={"SEQUENTIAL": 300, "PRIORITY": 200},
            domain_usage={"ENERGY": 400, "SYSTEM": 300},
            version_usage={"1": 100, "2": 50, "3": 30, "4": 20},
        )
        assert metrics.rules_per_category["safety"] == 60
        assert metrics.rules_per_scope["global"] == 150
        assert metrics.version_usage["1"] == 100
        assert metrics.rules_per_category["maintenance"] == 100
        assert metrics.version_usage["4"] == 20


# ═════════════════════════════════════════════════════════════════════════════
# RuleSet — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleSetPhase35:
    """Tests for enhanced RuleSet with categories, nested_rulesets, metadata."""

    def test_defaults_include_categories(self) -> None:
        rs = RuleSet()
        assert rs.categories == []

    def test_defaults_include_nested_rulesets(self) -> None:
        rs = RuleSet()
        assert rs.nested_rulesets == []

    def test_defaults_include_metadata(self) -> None:
        rs = RuleSet()
        assert rs.metadata == {}

    def test_custom_ruleset_with_new_fields(self) -> None:
        inner = RuleSet(name="Inner Set", domain=RuleDomain.EVIDENCE)
        rs = RuleSet(
            name="Parent Set",
            domain=RuleDomain.SYSTEM,
            categories=["safety", "compliance"],
            rules=[Rule(name="R1")],
            nested_rulesets=[inner],
            metadata={"owner": "platform-team", "severity": "high"},
        )
        assert rs.categories == ["safety", "compliance"]
        assert len(rs.nested_rulesets) == 1
        assert rs.nested_rulesets[0].name == "Inner Set"
        assert rs.metadata["owner"] == "platform-team"
        assert rs.metadata["severity"] == "high"

    def test_existing_fields_still_work(self) -> None:
        rs = RuleSet(
            name="Existing",
            domain=RuleDomain.ENERGY,
            evaluation_strategy=EvaluationStrategyType.PRIORITY,
        )
        assert rs.name == "Existing"
        assert rs.domain == RuleDomain.ENERGY
        assert rs.evaluation_strategy == EvaluationStrategyType.PRIORITY
        assert rs.version == 1
        assert rs.enabled is True

    def test_nested_ruleset_recursion(self) -> None:
        leaf = RuleSet(name="Leaf")
        middle = RuleSet(name="Middle", nested_rulesets=[leaf])
        top = RuleSet(name="Top", nested_rulesets=[middle])
        assert len(top.nested_rulesets) == 1
        assert top.nested_rulesets[0].name == "Middle"
        assert top.nested_rulesets[0].nested_rulesets[0].name == "Leaf"


# ═════════════════════════════════════════════════════════════════════════════
# RuleExplainabilityMetadata — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleExplainabilityMetadataPhase35:
    """Tests for enhanced RuleExplainabilityMetadata with why_policy_failed."""

    def test_defaults_include_why_policy_failed(self) -> None:
        meta = RuleExplainabilityMetadata()
        assert meta.why_policy_failed == ""

    def test_defaults_include_why_rule_selected(self) -> None:
        meta = RuleExplainabilityMetadata()
        assert meta.why_rule_selected == ""

    def test_custom_values_all_fields(self) -> None:
        meta = RuleExplainabilityMetadata(
            why_rule_selected="Rule matched domain ENERGY",
            why_rule_applied="Condition temperature > 100 matched",
            why_rule_skipped="Rule in DEPRECATED lifecycle status",
            why_conflict_resolved="Higher priority rule (100) selected over (50)",
            why_priority_selected="Rule with highest priority in domain",
            why_policy_failed="Rule action 'shutdown' not in allowed_actions",
            evaluation_strategy="PRIORITY",
        )
        assert meta.why_rule_selected == "Rule matched domain ENERGY"
        assert meta.why_rule_applied == "Condition temperature > 100 matched"
        assert meta.why_rule_skipped == "Rule in DEPRECATED lifecycle status"
        assert meta.why_conflict_resolved == "Higher priority rule (100) selected over (50)"
        assert meta.why_priority_selected == "Rule with highest priority in domain"
        assert meta.why_policy_failed == "Rule action 'shutdown' not in allowed_actions"
        assert meta.evaluation_strategy == "PRIORITY"


# ═════════════════════════════════════════════════════════════════════════════
# RuleConfidenceCalculator — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleConfidenceCalculatorPhase35:
    """Tests for enhanced RuleConfidenceCalculator with lifecycle_validity."""

    def test_calculate_includes_lifecycle_validity(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        evaluation = RuleEvaluation(
            context=ctx,
            rules_evaluated=[rule.rule_id],
            decisions=[],
        )
        calculator = RuleConfidenceCalculator()
        confidence = calculator.calculate(evaluation)
        assert hasattr(confidence, "lifecycle_validity")
        assert 0.0 <= confidence.lifecycle_validity <= 1.0

    def test_calculate_empty_rules(self) -> None:
        ctx = RuleContext()
        evaluation = RuleEvaluation(context=ctx)
        calculator = RuleConfidenceCalculator()
        confidence = calculator.calculate(evaluation)
        assert confidence.overall_confidence == 0.0
        assert confidence.lifecycle_validity == 1.0

    def test_calculate_with_confidence(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id, decision="allow")
        evaluation = RuleEvaluation(
            context=ctx,
            rules_evaluated=[rule.rule_id],
            decisions=[dec],
            status="COMPLETED",
        )
        calculator = RuleConfidenceCalculator()
        confidence = calculator.calculate(evaluation)
        assert confidence.overall_confidence > 0.0
        assert confidence.lifecycle_validity == 1.0
        assert confidence.rule_completeness == 1.0

    def test_calculate_with_conflicts(self) -> None:
        ctx = RuleContext()
        rule_a = Rule()
        rule_b = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule_a.rule_id, decision="allow")
        evaluation = RuleEvaluation(
            context=ctx,
            rules_evaluated=[rule_a.rule_id, rule_b.rule_id],
            decisions=[dec],
            conflicts_detected=["conflict-1", "conflict-2"],
            status="COMPLETED",
        )
        calculator = RuleConfidenceCalculator()
        confidence = calculator.calculate(evaluation)
        assert 0.0 < confidence.conflict_quality < 1.0
        assert confidence.conflict_quality == max(0.0, 1.0 - 2 * 0.2)

    def test_calculate_weights_all_scores(self) -> None:
        ctx = RuleContext()
        rule = Rule()
        dec = RuleDecision(context_id=ctx.context_id, rule_id=rule.rule_id, decision="deny")
        evaluation = RuleEvaluation(
            context=ctx,
            rules_evaluated=[rule.rule_id],
            decisions=[dec],
            status="COMPLETED",
        )
        calculator = RuleConfidenceCalculator()
        confidence = calculator.calculate(evaluation)
        # All scores > 0 should give overall > 0
        assert confidence.overall_confidence > 0.0
        assert confidence.rule_completeness == 1.0
        assert confidence.version_freshness == 1.0
        assert confidence.lifecycle_validity == 1.0
        assert confidence.conflict_quality == 1.0
        assert confidence.policy_compliance == 1.0
        assert confidence.evaluation_coverage == 1.0


# ═════════════════════════════════════════════════════════════════════════════
# RuleTrace — Phase 3.5 Enhancement (Stage Tracking)
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleTracePhase35:
    """Tests for enhanced RuleTrace with dedicated stage tracking methods."""

    def test_record_validation_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_validation_stage(
            domain="ENERGY",
            correlation_id="corr-1",
        )
        assert record.stage_name == "validation"
        assert record.operation == "validate"
        assert record.domain == "ENERGY"

    def test_record_parsing_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_parsing_stage(
            domain="SYSTEM",
            correlation_id="corr-2",
        )
        assert record.stage_name == "parsing"
        assert record.operation == "parse"

    def test_record_compilation_stage(self) -> None:
        trace = RuleTrace()
        rule_id = str(uuid.uuid4())
        record = trace.record_compilation_stage(
            rule_id=rule_id,
            domain="ENERGY",
            correlation_id="corr-3",
        )
        assert record.stage_name == "compilation"
        assert record.operation == "compile"
        assert record.rule_id is not None

    def test_record_evaluation_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_evaluation_stage(
            strategy="PRIORITY",
            domain="ENERGY",
            correlation_id="corr-4",
            duration_ms=12.5,
        )
        assert record.stage_name == "evaluation"
        assert record.operation == "evaluate"
        assert record.evaluation_strategy == "PRIORITY"
        assert record.duration_ms == 12.5

    def test_record_conflict_resolution_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_conflict_resolution_stage(
            domain="ENERGY",
            correlation_id="corr-5",
            duration_ms=3.2,
        )
        assert record.stage_name == "conflict_resolution"
        assert record.operation == "resolve_conflicts"

    def test_record_priority_resolution_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_priority_resolution_stage(
            domain="ENERGY",
            correlation_id="corr-6",
            duration_ms=1.5,
        )
        assert record.stage_name == "priority_resolution"
        assert record.operation == "resolve_priorities"

    def test_record_policy_validation_stage(self) -> None:
        trace = RuleTrace()
        record = trace.record_policy_validation_stage(
            domain="ENERGY",
            correlation_id="corr-7",
            success=True,
        )
        assert record.stage_name == "policy_validation"
        assert record.operation == "validate_policy"
        assert record.success is True

    def test_record_stage_with_duration(self) -> None:
        trace = RuleTrace()
        record = trace.record_stage(
            stage_name="evaluation",
            operation="evaluate",
            duration_ms=15.3,
        )
        assert record.duration_ms == 15.3

    def test_stage_with_warnings_and_errors(self) -> None:
        trace = RuleTrace()
        record = trace.record_validation_stage(
            warnings=["Low confidence"],
            errors=["Validation timeout"],
            success=False,
            duration_ms=5.0,
        )
        assert len(record.warnings) == 1
        assert len(record.errors) == 1
        assert record.success is False
        assert record.duration_ms == 5.0

    def test_all_stages_tracked_separately(self) -> None:
        trace = RuleTrace()
        trace.record_validation_stage(domain="A")
        trace.record_parsing_stage(domain="A")
        trace.record_compilation_stage(domain="A")
        trace.record_evaluation_stage(domain="A")
        trace.record_conflict_resolution_stage(domain="A")
        trace.record_priority_resolution_stage(domain="A")
        trace.record_policy_validation_stage(domain="A")
        assert trace.count() == 7
        assert len(trace.get_by_stage("validation")) == 1
        assert len(trace.get_by_stage("evaluation")) == 1
        assert len(trace.get_by_stage("conflict_resolution")) == 1
        assert len(trace.get_by_stage("policy_validation")) == 1


# ═════════════════════════════════════════════════════════════════════════════
# RuleMetricsCollector — Phase 3.5 Enhancement
# ═════════════════════════════════════════════════════════════════════════════

class TestRuleMetricsCollectorPhase35:
    """Tests for enhanced RuleMetricsCollector with category/scope/version tracking."""

    def test_increment_rules_per_category(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules_per_category("safety")
        collector.increment_rules_per_category("safety")
        collector.increment_rules_per_category("compliance")
        metrics = collector.snapshot()
        assert metrics.rules_per_category["safety"] == 2
        assert metrics.rules_per_category["compliance"] == 1

    def test_increment_rules_per_scope(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules_per_scope("global")
        collector.increment_rules_per_scope("local")
        metrics = collector.snapshot()
        assert metrics.rules_per_scope["global"] == 1
        assert metrics.rules_per_scope["local"] == 1

    def test_increment_version_usage(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_version_usage("1")
        collector.increment_version_usage("2")
        collector.increment_version_usage("1")
        metrics = collector.snapshot()
        assert metrics.version_usage["1"] == 2
        assert metrics.version_usage["2"] == 1

    def test_existing_metrics_still_work(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules(domain="ENERGY", rule_type="SAFETY")
        collector.increment_evaluations()
        collector.increment_cache_hits()
        collector.record_evaluation_time(10.0)
        metrics = collector.snapshot()
        assert metrics.rules_total == 1
        assert metrics.rules_per_domain["ENERGY"] == 1
        assert metrics.evaluations_total == 1
        assert metrics.cache_hits == 1

    def test_reset_includes_new_counters(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules_per_category("safety")
        collector.increment_rules_per_scope("global")
        collector.increment_version_usage("1")
        collector.reset()
        metrics = collector.snapshot()
        assert metrics.rules_per_category == {}
        assert metrics.rules_per_scope == {}
        assert metrics.version_usage == {}
        assert metrics.rules_total == 0


# ═════════════════════════════════════════════════════════════════════════════
# Backward Compatibility — Phase 3.5
# ═════════════════════════════════════════════════════════════════════════════

class TestBackwardCompatibilityPhase35:
    """Existing Phase 1-3 models still construct and serialize correctly."""

    def test_rule_still_works(self) -> None:
        rule = Rule(name="Phase3 Compat", domain=RuleDomain.SYSTEM)
        assert rule.name == "Phase3 Compat"
        assert rule.domain == RuleDomain.SYSTEM
        assert rule.version >= 1

    def test_rule_context_still_works(self) -> None:
        ctx = RuleContext(domain=RuleDomain.ENERGY, inputs={"temp": 100})
        assert ctx.domain == RuleDomain.ENERGY
        assert ctx.inputs["temp"] == 100

    def test_rule_evaluation_still_works(self) -> None:
        ctx = RuleContext()
        evaluation = RuleEvaluation(context=ctx, status="COMPLETED")
        assert evaluation.status == "COMPLETED"
        assert evaluation.total_evaluation_time_ms == 0.0

    def test_explainability_old_fields_still_work(self) -> None:
        meta = RuleExplainabilityMetadata(
            why_rule_applied="Matched",
            evaluation_strategy="SEQUENTIAL",
        )
        assert meta.why_rule_applied == "Matched"
        assert meta.evaluation_strategy == "SEQUENTIAL"

    def test_rule_set_old_fields_still_work(self) -> None:
        rs = RuleSet(name="Legacy", rules=[Rule(name="R1")])
        assert rs.name == "Legacy"
        assert len(rs.rules) == 1
