"""Abstract interfaces for the Rule Manager.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

Architecture:
    RuleService  →  RuleManager  →  RuleCoordinator
                                            ├── RuleValidator
                                            ├── RuleParser
                                            ├── RuleCompiler
                                            ├── RuleEvaluator
                                            ├── ConflictResolver
                                            ├── PriorityEngine
                                            └── RuleCache

RuleService is the enterprise facade for external callers.
RuleManager is the internal orchestrator.
RuleCoordinator coordinates all sub-components.
"""

from __future__ import annotations

import abc

from adip.rules.contracts.models import (
    Rule,
    RuleContext,
    RuleDecision,
    RuleEvaluation,
    RuleHealth,
    RuleMetrics,
    RuleSet,
)
from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
    RuleLifecycleStatus,
    RuleType,
)

# ─────────────────────────────────────────────────────────────────────────────
# RuleService — enterprise facade (ONLY public API)
# ─────────────────────────────────────────────────────────────────────────────


class RuleService(abc.ABC):
    """Enterprise facade for rule operations.

    Provides validation, authorisation, audit, and observability
    wrapping around the RuleManager. External modules interact
    with this facade rather than with RuleManager directly.
    """

    @abc.abstractmethod
    async def create_rule(self, rule: Rule) -> Rule:
        """Validate, authorise, and create a new rule."""
        ...

    @abc.abstractmethod
    async def get_rule(self, rule_id: str) -> Rule | None:
        """Retrieve a rule by its identifier."""
        ...

    @abc.abstractmethod
    async def update_rule(self, rule: Rule) -> Rule:
        """Update an existing rule with authorisation."""
        ...

    @abc.abstractmethod
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule with authorisation and audit."""
        ...

    @abc.abstractmethod
    async def evaluate(
        self,
        context: RuleContext,
        domain: RuleDomain = RuleDomain.SYSTEM,
    ) -> RuleEvaluation:
        """Evaluate rules matching the given context and domain."""
        ...

    @abc.abstractmethod
    async def create_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Create a new rule set."""
        ...

    @abc.abstractmethod
    async def get_ruleset(self, ruleset_id: str) -> RuleSet | None:
        """Retrieve a rule set by its identifier."""
        ...

    @abc.abstractmethod
    async def activate_rule(self, rule_id: str) -> Rule:
        """Activate a rule (transition to ACTIVE status)."""
        ...

    @abc.abstractmethod
    async def archive_rule(self, rule_id: str, reason: str = "") -> bool:
        """Archive a rule."""
        ...

    @abc.abstractmethod
    async def health(self) -> RuleHealth:
        """Return the current health status of the rule platform."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> RuleMetrics:
        """Return aggregated rule platform metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleManager — internal orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class RuleManager(abc.ABC):
    """Internal orchestrator for all rule operations.

    Every ADIP module that needs rule operations goes through
    this interface. The RuleManager:
      1. Validates the operation
      2. Delegates to RuleCoordinator for orchestration
      3. Records events for audit and observability
    """

    @abc.abstractmethod
    async def create_rule(self, rule: Rule) -> Rule:
        """Store a new rule."""
        ...

    @abc.abstractmethod
    async def read_rule(self, rule_id: str) -> Rule | None:
        """Retrieve a rule by ID."""
        ...

    @abc.abstractmethod
    async def update_rule(self, rule: Rule) -> Rule:
        """Update an existing rule."""
        ...

    @abc.abstractmethod
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule."""
        ...

    @abc.abstractmethod
    async def search_rules(
        self,
        query: str = "",
        domain: RuleDomain | None = None,
        rule_type: RuleType | None = None,
        status: RuleLifecycleStatus | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Rule]:
        """Search for rules matching the given filters."""
        ...

    @abc.abstractmethod
    async def evaluate_rules(
        self,
        context: RuleContext,
        domain: RuleDomain = RuleDomain.SYSTEM,
    ) -> RuleEvaluation:
        """Evaluate rules matching the given context and domain."""
        ...

    @abc.abstractmethod
    async def create_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Create a new rule set."""
        ...

    @abc.abstractmethod
    async def read_ruleset(self, ruleset_id: str) -> RuleSet | None:
        """Retrieve a rule set by ID."""
        ...

    @abc.abstractmethod
    async def update_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Update an existing rule set."""
        ...

    @abc.abstractmethod
    async def delete_ruleset(self, ruleset_id: str) -> bool:
        """Delete a rule set."""
        ...

    @abc.abstractmethod
    async def activate_rule(self, rule_id: str) -> Rule:
        """Activate a rule (transition to ACTIVE status)."""
        ...

    @abc.abstractmethod
    async def archive_rule(self, rule_id: str, reason: str = "") -> bool:
        """Archive a rule."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> RuleHealth:
        """Return the current health status."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> RuleMetrics:
        """Return aggregated metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleCoordinator — sub-component orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class RuleCoordinator(abc.ABC):
    """Sub-component orchestrator for rule operations.

    Coordinates RuleValidator, RuleParser, RuleCompiler,
    RuleEvaluator, ConflictResolver, PriorityEngine, and
    RuleCache. Contains orchestration only — no business logic.
    """

    @abc.abstractmethod
    async def create_rule(self, rule: Rule) -> Rule:
        """Orchestrate the full rule creation pipeline."""
        ...

    @abc.abstractmethod
    async def get_rule(self, rule_id: str) -> Rule | None:
        """Retrieve a rule by ID."""
        ...

    @abc.abstractmethod
    async def update_rule(self, rule: Rule) -> Rule:
        """Update an existing rule."""
        ...

    @abc.abstractmethod
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule."""
        ...

    @abc.abstractmethod
    async def evaluate(
        self,
        context: RuleContext,
        domain: RuleDomain = RuleDomain.SYSTEM,
    ) -> RuleEvaluation:
        """Orchestrate rule evaluation across all sub-components."""
        ...

    @abc.abstractmethod
    async def create_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Orchestrate rule set creation."""
        ...

    @abc.abstractmethod
    async def get_ruleset(self, ruleset_id: str) -> RuleSet | None:
        """Retrieve a rule set by ID."""
        ...

    @abc.abstractmethod
    async def update_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Update an existing rule set."""
        ...

    @abc.abstractmethod
    async def delete_ruleset(self, ruleset_id: str) -> bool:
        """Delete a rule set."""
        ...

    @abc.abstractmethod
    async def activate_rule(self, rule_id: str) -> Rule:
        """Activate a rule."""
        ...

    @abc.abstractmethod
    async def archive_rule(self, rule_id: str) -> bool:
        """Archive a rule."""
        ...

    @abc.abstractmethod
    async def health(self) -> RuleHealth:
        """Return health status of all sub-components."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> RuleMetrics:
        """Return aggregated metrics from all sub-components."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleValidator
# ─────────────────────────────────────────────────────────────────────────────


class RuleValidator(abc.ABC):
    """Validates rules and rule sets for correctness and consistency.

    Ensures rules are structurally valid, conditions are well-formed,
    actions are permitted, and the rule does not violate policy
    constraints.
    """

    @abc.abstractmethod
    async def validate_rule(self, rule: Rule) -> list[str]:
        """Validate a single rule. Returns list of validation violations."""
        ...

    @abc.abstractmethod
    async def validate_ruleset(self, ruleset: RuleSet) -> list[str]:
        """Validate a rule set. Returns list of validation violations."""
        ...

    @abc.abstractmethod
    async def validate_context(self, context: RuleContext) -> list[str]:
        """Validate an evaluation context. Returns list of validation violations."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleParser
# ─────────────────────────────────────────────────────────────────────────────


class RuleParser(abc.ABC):
    """Parses rule definitions from various source formats.

    Supports parsing rules from structured data, DSL strings,
    configuration files, and other serialisation formats.
    """

    @abc.abstractmethod
    async def parse_rule(self, source: str, format: str = "json") -> Rule:
        """Parse a rule definition from a source string."""
        ...

    @abc.abstractmethod
    async def parse_ruleset(self, source: str, format: str = "json") -> RuleSet:
        """Parse a rule set definition from a source string."""
        ...

    @abc.abstractmethod
    async def get_supported_formats(self) -> list[str]:
        """Return the source formats this parser supports."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleCompiler
# ─────────────────────────────────────────────────────────────────────────────


class RuleCompiler(abc.ABC):
    """Compiles rule definitions into an executable form.

    Transforms parsed rules into an optimised internal representation
    for efficient evaluation.
    """

    @abc.abstractmethod
    async def compile_rule(self, rule: Rule) -> Rule:
        """Compile a rule into an executable form."""
        ...

    @abc.abstractmethod
    async def compile_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Compile a rule set into an executable form."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleEvaluator
# ─────────────────────────────────────────────────────────────────────────────


class RuleEvaluator(abc.ABC):
    """Evaluates rules against a given context.

    Supports multiple evaluation strategies: sequential, priority,
    conditional, composite, and parallel.
    """

    @abc.abstractmethod
    async def evaluate_rule(
        self,
        rule: Rule,
        context: RuleContext,
    ) -> RuleDecision:
        """Evaluate a single rule against the given context."""
        ...

    @abc.abstractmethod
    async def evaluate_ruleset(
        self,
        ruleset: RuleSet,
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate all rules in a rule set against the given context."""
        ...

    @abc.abstractmethod
    def get_supported_strategies(self) -> list[EvaluationStrategyType]:
        """Return the evaluation strategies this evaluator supports."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# ConflictResolver
# ─────────────────────────────────────────────────────────────────────────────


class ConflictResolver(abc.ABC):
    """Detects and resolves conflicts between rules.

    Identifies rule conflicts such as direct overlap, priority
    inversion, and circular dependencies, and applies the configured
    resolution strategy.
    """

    @abc.abstractmethod
    async def detect_conflicts(self, rules: list[Rule]) -> list[dict[str, str]]:
        """Detect conflicts within a list of rules. Returns list of conflict descriptions."""
        ...

    @abc.abstractmethod
    async def resolve_conflicts(
        self,
        decisions: list[RuleDecision],
        strategy: str = "PRIORITY",
    ) -> list[RuleDecision]:
        """Resolve conflicts between decisions using the given strategy."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# PriorityEngine
# ─────────────────────────────────────────────────────────────────────────────


class PriorityEngine(abc.ABC):
    """Determines rule priority ordering for evaluation.

    Computes the effective priority of rules, considering explicit
    priority values, rule type precedence, domain precedence, and
    dependency ordering.
    """

    @abc.abstractmethod
    async def order_rules(
        self,
        rules: list[Rule],
        strategy: EvaluationStrategyType = EvaluationStrategyType.PRIORITY,
    ) -> list[Rule]:
        """Order rules by their effective priority for evaluation."""
        ...

    @abc.abstractmethod
    async def get_effective_priority(
        self,
        rule: Rule,
        context: RuleContext | None = None,
    ) -> int:
        """Compute the effective priority of a rule, considering context."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RuleCache
# ─────────────────────────────────────────────────────────────────────────────


class RuleCache(abc.ABC):
    """Cache layer for rule evaluation results.

    Caches evaluation results to reduce latency for repeated or
    similar evaluation requests.
    """

    @abc.abstractmethod
    async def get(self, cache_key: str) -> RuleEvaluation | None:
        """Retrieve a cached RuleEvaluation by cache key."""
        ...

    @abc.abstractmethod
    async def set(self, cache_key: str, evaluation: RuleEvaluation, ttl_seconds: int = 300) -> None:
        """Cache a RuleEvaluation with an optional TTL."""
        ...

    @abc.abstractmethod
    async def invalidate(self, cache_key: str) -> bool:
        """Invalidate a single cache entry."""
        ...

    @abc.abstractmethod
    async def clear(self) -> int:
        """Clear all cache entries. Returns the number cleared."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# EvaluationStrategy — strategy pattern for evaluation approaches
# ─────────────────────────────────────────────────────────────────────────────


class EvaluationStrategy(abc.ABC):
    """Strategy for evaluating a set of rules.

    Each concrete strategy implements a different evaluation approach
    (sequential, priority, conditional, composite, parallel) while
    conforming to this common interface.
    """

    @abc.abstractmethod
    async def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate the given rules against the context using this strategy."""
        ...

    @abc.abstractmethod
    def get_strategy_type(self) -> EvaluationStrategyType:
        """Return the evaluation strategy type."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Concrete evaluation strategies
# ─────────────────────────────────────────────────────────────────────────────


class SequentialEvaluation(EvaluationStrategy):
    """Sequential evaluation — evaluate rules in order, stop at first match."""

    async def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        ...

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.SEQUENTIAL


class PriorityEvaluation(EvaluationStrategy):
    """Priority evaluation — evaluate rules by priority, highest wins."""

    async def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        ...

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.PRIORITY


class ConditionalEvaluation(EvaluationStrategy):
    """Conditional evaluation — evaluate based on condition evaluation."""

    async def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        ...

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.CONDITIONAL


class CompositeEvaluation(EvaluationStrategy):
    """Composite evaluation — combine multiple strategies."""

    async def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        ...

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.COMPOSITE
