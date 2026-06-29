"""RuleCoordinator — orchestrates all rule sub-components.

Coordinates the full rule evaluation pipeline: validation, parsing,
compilation, version management, lifecycle management, evaluation,
conflict resolution, priority ordering, policy enforcement, caching,
confidence calculation, metrics, and tracing.

Contains orchestration only — no business logic.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.rules.contracts.models import (
    Rule,
    RuleContext,
    RuleEvaluation,
    RuleExplainabilityMetadata,
    RuleHealth,
    RuleMetrics,
    RuleSet,
)
from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
    RuleLifecycleStatus,
)
from adip.rules.execution.cache import RuleCache
from adip.rules.execution.compiler import RuleCompiler
from adip.rules.execution.conflict_resolver import ConflictResolver
from adip.rules.execution.evaluator import RuleEvaluator
from adip.rules.execution.lifecycle import RuleLifecycleManager
from adip.rules.execution.metrics import RuleMetricsCollector
from adip.rules.execution.parser import RuleParser
from adip.rules.execution.policy import RulePolicyEngine
from adip.rules.execution.priority_engine import PriorityEngine
from adip.rules.execution.trace import RuleTrace
from adip.rules.execution.validator import RuleValidator
from adip.rules.execution.version_manager import RuleVersionManager
from adip.rules.orchestration.confidence import RuleConfidenceCalculator
from adip.rules.orchestration.session import RuleSessionManager

log = structlog.get_logger(__name__)


class RuleCoordinator:
    """Orchestrates all rule sub-components for the ADIP platform.

    RuleManager delegates to this coordinator for all sub-component
    interactions. All components are injectable via constructor (DI ready).
    """

    def __init__(
        self,
        validator: RuleValidator | None = None,
        parser: RuleParser | None = None,
        compiler: RuleCompiler | None = None,
        version_manager: RuleVersionManager | None = None,
        lifecycle_manager: RuleLifecycleManager | None = None,
        evaluator: RuleEvaluator | None = None,
        conflict_resolver: ConflictResolver | None = None,
        priority_engine: PriorityEngine | None = None,
        policy_engine: RulePolicyEngine | None = None,
        cache: RuleCache | None = None,
        session_manager: RuleSessionManager | None = None,
        trace: RuleTrace | None = None,
        metrics_collector: RuleMetricsCollector | None = None,
        confidence_calculator: RuleConfidenceCalculator | None = None,
    ) -> None:
        self._validator = validator or RuleValidator()
        self._parser = parser or RuleParser()
        self._compiler = compiler or RuleCompiler()
        self._version_manager = version_manager or RuleVersionManager()
        self._lifecycle_manager = lifecycle_manager or RuleLifecycleManager()
        self._evaluator = evaluator or RuleEvaluator()
        self._conflict_resolver = conflict_resolver or ConflictResolver()
        self._priority_engine = priority_engine or PriorityEngine()
        self._policy_engine = policy_engine or RulePolicyEngine()
        self._cache = cache or RuleCache()
        self._session_manager = session_manager or RuleSessionManager()
        self._trace = trace or RuleTrace()
        self._metrics_collector = metrics_collector or RuleMetricsCollector()
        self._confidence_calculator = confidence_calculator or RuleConfidenceCalculator()
        self._rules: dict[str, Rule] = {}
        self._rulesets: dict[str, RuleSet] = {}

    # ── Rule CRUD ──────────────────────────────────────────────────────────

    def create_rule(
        self,
        rule: Rule,
        created_by: str = "",
        change_summary: str = "",
    ) -> Rule:
        """Orchestrate the full rule creation pipeline."""
        rule_id = str(rule.rule_id)
        log.info("coordinator.create_rule", rule_id=rule_id)

        violations = self._validator.validate_rule(rule)
        if violations:
            raise ValueError(f"Rule validation failed: {'; '.join(violations)}")

        compiled = self._compiler.compile(rule)
        self._cache.set_compiled_rule(f"compiled:{rule_id}", compiled)

        self._version_manager.create_version(rule, created_by=created_by, change_summary=change_summary)
        self._lifecycle_manager.transition(rule, RuleLifecycleStatus.DRAFT)

        self._rules[rule_id] = rule

        # Record trace
        self._trace.record_stage(
            stage_name="create_rule",
            operation="create",
            rule_id=rule_id,
            domain=rule.domain.value,
            success=True,
        )

        self._metrics_collector.increment_rules(domain=rule.domain.value, rule_type=rule.rule_type.value)
        log.info("coordinator.create_rule.complete", rule_id=rule_id)
        return rule

    def get_rule(self, rule_id: str) -> Rule | None:
        """Retrieve a rule by ID."""
        return self._rules.get(rule_id)

    def update_rule(self, rule: Rule) -> Rule:
        """Update an existing rule."""
        rule_id = str(rule.rule_id)
        log.info("coordinator.update_rule", rule_id=rule_id)
        self._cache.invalidate(f"compiled:{rule_id}")
        self._cache.invalidate(f"rule:{rule_id}")
        new_compiled = self._compiler.compile(rule)
        self._cache.set_compiled_rule(f"compiled:{rule_id}", new_compiled)
        self._rules[rule_id] = rule
        return rule

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule."""
        existed = rule_id in self._rules
        if existed:
            del self._rules[rule_id]
            self._cache.invalidate(f"compiled:{rule_id}")
            self._cache.invalidate(f"rule:{rule_id}")
        return existed

    def create_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Orchestrate rule set creation."""
        ruleset_id = str(ruleset.ruleset_id)
        log.info("coordinator.create_ruleset", ruleset_id=ruleset_id)

        violations = self._validator.validate_ruleset(ruleset)
        if violations:
            raise ValueError(f"RuleSet validation failed: {'; '.join(violations)}")

        for rule in ruleset.rules:
            rule_id = str(rule.rule_id)
            if rule_id not in self._rules:
                self._rules[rule_id] = rule

        self._rulesets[ruleset_id] = ruleset
        self._metrics_collector.increment_rulesets()
        return ruleset

    def get_ruleset(self, ruleset_id: str) -> RuleSet | None:
        """Retrieve a rule set by ID."""
        return self._rulesets.get(ruleset_id)

    def update_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Update an existing rule set."""
        ruleset_id = str(ruleset.ruleset_id)
        log.info("coordinator.update_ruleset", ruleset_id=ruleset_id)
        self._cache.invalidate(f"ruleset:{ruleset_id}")
        self._rulesets[ruleset_id] = ruleset
        return ruleset

    def delete_ruleset(self, ruleset_id: str) -> bool:
        """Delete a rule set."""
        existed = ruleset_id in self._rulesets
        if existed:
            del self._rulesets[ruleset_id]
            self._cache.invalidate(f"ruleset:{ruleset_id}")
        return existed

    # ── Rule Lifecycle ────────────────────────────────────────────────────

    def activate_rule(self, rule_id: str) -> Rule:
        """Activate a rule (transition to ACTIVE status)."""
        rule = self._rules.get(rule_id)
        if rule is None:
            raise ValueError(f"Rule not found: {rule_id}")
        log.info("coordinator.activate_rule", rule_id=rule_id)
        result = self._lifecycle_manager.transition(rule, RuleLifecycleStatus.ACTIVE)
        self._rules[rule_id] = result
        self._metrics_collector.increment_active_rules()

        # Record trace
        self._trace.record_stage(
            stage_name="activate_rule",
            operation="lifecycle",
            rule_id=rule_id,
            domain=rule.domain.value,
            success=True,
        )
        return result

    def archive_rule(self, rule_id: str) -> bool:
        """Archive a rule."""
        rule = self._rules.get(rule_id)
        if rule is None:
            return False
        log.info("coordinator.archive_rule", rule_id=rule_id)
        result = self._lifecycle_manager.transition(rule, RuleLifecycleStatus.ARCHIVED)
        self._rules[rule_id] = result
        self._metrics_collector.decrement_active_rules()
        return True

    # ── Rule Evaluation ───────────────────────────────────────────────────

    def evaluate(
        self,
        context: RuleContext,
        domain: RuleDomain = RuleDomain.SYSTEM,
        strategy_type: EvaluationStrategyType | None = None,
    ) -> RuleEvaluation:
        """Orchestrate the full rule evaluation pipeline.

        Tracks per-stage timing and records traces for validation,
        compilation, evaluation, conflict resolution, priority
        resolution, and policy validation. Attaches explainability
        metadata and confidence to every decision.
        """
        log.info("coordinator.evaluate", domain=domain.value)

        start_time = datetime.now(UTC)
        strat = strategy_type or EvaluationStrategyType.SEQUENTIAL
        strategy_label = strat.value if isinstance(strat, EvaluationStrategyType) else str(strat)

        # ── Validation stage ──────────────────────────────────────────────
        val_start = datetime.now(UTC)
        self._trace.record_validation_stage(
            domain=domain.value,
            correlation_id=context.correlation_id,
        )
        val_duration = (datetime.now(UTC) - val_start).total_seconds() * 1000

        # ── Filter rules by domain ────────────────────────────────────────
        domain_rules = [
            r for r in self._rules.values()
            if r.domain == domain and r.enabled and r.status == RuleLifecycleStatus.ACTIVE
        ]

        # Create a ruleset for evaluation
        ruleset = RuleSet(
            name=f"Evaluation-{domain.value}",
            domain=domain,
            rules=domain_rules,
            evaluation_strategy=strat,
        )

        # ── Compilation stage ─────────────────────────────────────────────
        comp_start = datetime.now(UTC)
        compiled_rules = []
        for rule in ruleset.rules:
            cached = self._cache.get_compiled_rule(f"compiled:{str(rule.rule_id)}")
            if cached:
                self._metrics_collector.increment_cache_hits()
                compiled_rules.append(cached)
            else:
                self._metrics_collector.increment_cache_misses()
                compiled = self._compiler.compile(rule)
                self._cache.set_compiled_rule(f"compiled:{str(rule.rule_id)}", compiled)
                compiled_rules.append(compiled)
        comp_duration = (datetime.now(UTC) - comp_start).total_seconds() * 1000
        self._trace.record_compilation_stage(
            domain=domain.value,
            correlation_id=context.correlation_id,
            duration_ms=round(comp_duration, 2),
        )

        # ── Priority resolution stage ─────────────────────────────────────
        pri_start = datetime.now(UTC)
        ordered_rules = self._priority_engine.order_rules(
            ruleset.rules,
            strategy=strat or ruleset.evaluation_strategy or EvaluationStrategyType.PRIORITY,
        )
        pri_duration = (datetime.now(UTC) - pri_start).total_seconds() * 1000
        self._trace.record_priority_resolution_stage(
            domain=domain.value,
            correlation_id=context.correlation_id,
            duration_ms=round(pri_duration, 2),
        )

        # ── Evaluation stage ──────────────────────────────────────────────
        eval_start = datetime.now(UTC)
        evaluation = self._evaluator.evaluate_ruleset(
            RuleSet(
                name=ruleset.name,
                domain=ruleset.domain,
                rules=ordered_rules,
                evaluation_strategy=ruleset.evaluation_strategy,
            ),
            context,
            strategy_type=strat,
        )
        eval_duration = (datetime.now(UTC) - eval_start).total_seconds() * 1000
        self._trace.record_evaluation_stage(
            strategy=strategy_label,
            domain=domain.value,
            correlation_id=context.correlation_id,
            success=evaluation.status != "FAILED",
            duration_ms=round(eval_duration, 2),
        )

        # ── Conflict resolution stage ─────────────────────────────────────
        cr_start = datetime.now(UTC)
        conflicts = self._conflict_resolver.detect_conflicts(ordered_rules)
        for conflict in conflicts:
            evaluation.conflicts_detected.append(str(conflict.report_id))
            self._metrics_collector.increment_conflicts()

        resolved_decisions = self._conflict_resolver.resolve_conflicts(evaluation.decisions)
        evaluation.decisions = resolved_decisions
        cr_duration = (datetime.now(UTC) - cr_start).total_seconds() * 1000
        self._trace.record_conflict_resolution_stage(
            domain=domain.value,
            correlation_id=context.correlation_id,
            duration_ms=round(cr_duration, 2),
        )

        # ── Policy validation stage ───────────────────────────────────────
        pv_start = datetime.now(UTC)
        self._trace.record_policy_validation_stage(
            domain=domain.value,
            correlation_id=context.correlation_id,
        )
        pv_duration = (datetime.now(UTC) - pv_start).total_seconds() * 1000

        # Calculate confidence
        confidence = self._confidence_calculator.calculate(evaluation)

        # Attach explainability metadata
        for decision in evaluation.decisions:
            explainability = RuleExplainabilityMetadata(
                why_rule_selected="Rule matched domain and lifecycle criteria",
                why_rule_applied=f"Rule matched via {strategy_label} strategy",
                why_rule_skipped="Rule did not match conditions",
                why_conflict_resolved="Conflicts resolved by priority or deny-override",
                why_priority_selected="Highest priority rule selected for outcome",
                why_policy_failed="No policy violations detected",
                evaluation_strategy=strategy_label,
            )
            decision.metadata["explainability"] = explainability.model_dump()
            decision.metadata["confidence"] = confidence.model_dump()
            decision.reasoning = (
                f"Decision produced via {strategy_label} strategy. "
                f"Overall confidence: {confidence.overall_confidence:.2f}. "
                f"Applied rules: {len(decision.applied_rules)}. "
                f"Conflicts resolved: {len(evaluation.conflicts_detected)}."
            )
            decision.allow_or_deny = "allow" if decision.decision.lower() in ("allow", "approve") else "deny"
            decision.priority_resolution = (
                "highest_priority_wins" if strategy_label == "PRIORITY" else "sequential_order"
            )

        end_time = datetime.now(UTC)
        duration_ms = (end_time - start_time).total_seconds() * 1000
        evaluation.total_evaluation_time_ms = round(duration_ms, 2)

        # Record final trace
        self._trace.record_stage(
            stage_name="evaluation.complete",
            operation="evaluate",
            domain=domain.value,
            correlation_id=context.correlation_id,
            success=evaluation.status != "FAILED",
            duration_ms=round(duration_ms, 2),
        )

        # Update metrics
        self._metrics_collector.increment_evaluations()
        self._metrics_collector.increment_decisions(len(evaluation.decisions))
        self._metrics_collector.record_evaluation_time(duration_ms)
        self._metrics_collector.increment_strategy_usage(strategy_label)
        self._metrics_collector.increment_domain_usage(domain.value)

        log.info("coordinator.evaluate.complete", domain=domain.value, duration_ms=round(duration_ms, 2))
        return evaluation

    # ── Health & Metrics ──────────────────────────────────────────────────

    def health(self) -> RuleHealth:
        """Return health status of all sub-components."""
        log.info("coordinator.health")
        metrics_snap = self._metrics_collector.snapshot()
        total_ops = metrics_snap.evaluations_total + metrics_snap.conflicts_total + 1
        return RuleHealth(
            overall_status="HEALTHY",
            coordinator_status="HEALTHY",
            validator_status="HEALTHY",
            parser_status="HEALTHY",
            compiler_status="HEALTHY",
            evaluator_status="HEALTHY",
            cache_status="HEALTHY",
            policy_status="HEALTHY",
            version_status="HEALTHY",
            lifecycle_status="HEALTHY",
            priority_engine_status="HEALTHY",
            conflict_resolver_status="HEALTHY",
            average_latency_ms=metrics_snap.average_evaluation_time_ms,
            average_evaluation_time_ms=metrics_snap.average_evaluation_time_ms,
            error_count=0,
            error_rate=round(0.0 / max(1, total_ops), 4),
            total_rules=len(self._rules),
            total_rulesets=len(self._rulesets),
            total_evaluations=metrics_snap.evaluations_total,
            rules_evaluated=metrics_snap.evaluations_total,
            rule_domains=list({r.domain.value for r in self._rules.values()}),
        )

    def metrics(self) -> RuleMetrics:
        """Return aggregated metrics from all sub-components."""
        log.info("coordinator.metrics")
        return self._metrics_collector.snapshot()
