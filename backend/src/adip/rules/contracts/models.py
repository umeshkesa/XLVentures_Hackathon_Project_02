"""Rule Manager domain models.

Defines the core data contracts for the enterprise policy platform
including rules, rule sets, conditions, actions, contexts, decisions,
evaluations, policies, health, and metrics.

All models are Pydantic v2 BaseModel subclasses with full type
annotations, validation, and documentation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
    RuleLifecycleStatus,
    RuleType,
)

# ─────────────────────────────────────────────────────────────────────────────
# RuleCondition
# ─────────────────────────────────────────────────────────────────────────────


class RuleCondition(BaseModel):
    """A condition that must be satisfied for a rule to apply.

    Encapsulates the field, operator, value, and logical grouping
    for rule condition evaluation. Supports composable conditions
    via nested conditions.
    """

    condition_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique condition identifier",
    )
    field: str = Field(
        default="",
        description="The field or attribute to evaluate",
    )
    operator: str = Field(
        default="",
        description="Comparison operator (eq, neq, gt, gte, lt, lte, in, contains, matches)",
    )
    value: str = Field(
        default="",
        description="The value to compare against",
    )
    logic: str = Field(
        default="AND",
        description="Logical connector (AND, OR) when combined with other conditions",
    )
    conditions: list[RuleCondition] = Field(
        default_factory=list,
        description="Nested sub-conditions for complex evaluation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional condition metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleAction
# ─────────────────────────────────────────────────────────────────────────────


class RuleAction(BaseModel):
    """An action to execute when a rule evaluates successfully.

    Defines the action type, parameters, and execution metadata
    for rule-based decision outcomes.
    """

    action_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique action identifier",
    )
    action_type: str = Field(
        default="",
        description="The type of action (approve, reject, flag, notify, block, escalate)",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters and configuration",
    )
    priority: int = Field(
        default=0,
        description="Execution priority for this action",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional action metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Rule
# ─────────────────────────────────────────────────────────────────────────────


class Rule(BaseModel):
    """A single rule in the enterprise policy platform.

    Represents a deterministic decision rule with conditions,
    actions, lifecycle tracking, and enterprise metadata.
    """

    rule_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique rule identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable rule name",
    )
    description: str = Field(
        default="",
        description="Rule description and intent",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain this rule belongs to",
    )
    rule_type: RuleType = Field(
        default=RuleType.BUSINESS,
        description="The type of rule",
    )
    status: RuleLifecycleStatus = Field(
        default=RuleLifecycleStatus.DRAFT,
        description="Current lifecycle status",
    )
    conditions: list[RuleCondition] = Field(
        default_factory=list,
        description="Conditions that must be satisfied for this rule to apply",
    )
    actions: list[RuleAction] = Field(
        default_factory=list,
        description="Actions to execute when conditions are met",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Rule priority (higher = more important)",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Rule version number",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="User-defined tags for classification",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this rule",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    source: str = Field(
        default="",
        description="Original source identifier (file path, URL, etc.)",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the rule is currently enabled for evaluation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the rule was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the rule was last updated",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration timestamp",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for arbitrary additional data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleSet
# ─────────────────────────────────────────────────────────────────────────────


class RuleSet(BaseModel):
    """A collection of rules that are evaluated together.

    RuleSets enable grouping of related rules under a common
    evaluation strategy, domain, and lifecycle. Enhanced for
    Phase 3.5 with first-class support for multiple categories,
    nested RuleSets, comprehensive metadata, version tracking,
    and lifecycle management.
    """

    ruleset_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique rule set identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable rule set name",
    )
    description: str = Field(
        default="",
        description="Rule set description and intent",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain this rule set belongs to",
    )
    categories: list[str] = Field(
        default_factory=list,
        description="Multiple categories for classification and filtering",
    )
    rules: list[Rule] = Field(
        default_factory=list,
        description="The rules in this set",
    )
    nested_rulesets: list[RuleSet] = Field(
        default_factory=list,
        description="Nested child rule sets for hierarchical organisation",
    )
    evaluation_strategy: EvaluationStrategyType = Field(
        default=EvaluationStrategyType.SEQUENTIAL,
        description="The evaluation strategy for this rule set",
    )
    status: RuleLifecycleStatus = Field(
        default=RuleLifecycleStatus.DRAFT,
        description="Current lifecycle status",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Rule set version number",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="User-defined tags for classification",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this rule set",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the rule set is currently enabled",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the rule set was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the rule set was last updated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Rule set metadata for custom attributes and annotations",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for arbitrary additional data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleContext
# ─────────────────────────────────────────────────────────────────────────────


class RuleContext(BaseModel):
    """The evaluation context for a rule or rule set.

    Carries all input data, metadata, and environmental information
    needed to evaluate rules. Acts as the input contract for the
    evaluation pipeline.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain this context belongs to",
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for rule evaluation",
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Entity attributes for condition matching",
    )
    user_id: str = Field(
        default="",
        description="The user or system triggering the evaluation",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the context was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleDecision
# ─────────────────────────────────────────────────────────────────────────────


class RuleDecision(BaseModel):
    """The outcome of a rule evaluation.

    Records which rules matched, which actions were taken, the
    final decision, and supporting explainability data for audit
    and tracing. Enhanced for Phase 3.5 with full decision
    provenance — applied/skipped/ignored/conflicting rules,
    priority resolution, reasoning trace, and confidence.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    evaluation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="The evaluation that produced this decision",
    )
    context_id: UUID4 = Field(
        description="The evaluation context that produced this decision",
    )
    rule_id: UUID4 = Field(
        description="The rule that produced this decision",
    )
    ruleset_id: UUID4 | None = Field(
        default=None,
        description="The rule set that produced this decision (if applicable)",
    )
    applied_rules: list[str] = Field(
        default_factory=list,
        description="Rule IDs that were applied to reach this decision",
    )
    skipped_rules: list[str] = Field(
        default_factory=list,
        description="Rule IDs that were skipped during evaluation",
    )
    ignored_rules: list[str] = Field(
        default_factory=list,
        description="Rule IDs that were ignored (not considered)",
    )
    conflicting_rules: list[str] = Field(
        default_factory=list,
        description="Rule IDs that conflicted with the final decision",
    )
    priority_resolution: str = Field(
        default="",
        description="How priorities were resolved (e.g. 'highest_priority_wins', 'domain_precedence')",
    )
    decision: str = Field(
        default="",
        description="The decision outcome (allow, deny, approve, reject, flag, escalate)",
    )
    allow_or_deny: str = Field(
        default="deny",
        description="Simplified allow/deny classification of the decision",
    )
    matched: bool = Field(
        default=False,
        description="Whether the rule conditions matched",
    )
    actions_taken: list[str] = Field(
        default_factory=list,
        description="Actions that were executed as a result",
    )
    reason: str = Field(
        default="",
        description="Human-readable reason for the decision",
    )
    reasoning: str = Field(
        default="",
        description="Detailed reasoning trace for the decision pipeline",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the decision (0.0–1.0)",
    )
    evaluation_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to evaluate in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleEvaluation
# ─────────────────────────────────────────────────────────────────────────────


class RuleEvaluation(BaseModel):
    """A complete evaluation record for a rule or rule set.

    Captures the full evaluation lifecycle: context, rules evaluated,
    decisions produced, conflicts detected, and execution timing.
    """

    evaluation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique evaluation identifier",
    )
    context: RuleContext = Field(
        description="The evaluation context",
    )
    rules_evaluated: list[UUID4] = Field(
        default_factory=list,
        description="IDs of rules that were evaluated",
    )
    decisions: list[RuleDecision] = Field(
        default_factory=list,
        description="Decisions produced by the evaluation",
    )
    conflicts_detected: list[str] = Field(
        default_factory=list,
        description="Conflicts detected during evaluation",
    )
    evaluation_strategy: EvaluationStrategyType = Field(
        default=EvaluationStrategyType.SEQUENTIAL,
        description="The evaluation strategy used",
    )
    total_evaluation_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total time for the evaluation in milliseconds",
    )
    status: str = Field(
        default="COMPLETED",
        description="Evaluation status (COMPLETED, FAILED, PARTIAL)",
    )
    error_message: str = Field(
        default="",
        description="Error details if evaluation failed",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the evaluation was performed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional evaluation metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RulePolicy
# ─────────────────────────────────────────────────────────────────────────────


class RulePolicy(BaseModel):
    """A policy document that governs rule evaluation behaviour.

    Defines global and domain-specific constraints, allowed actions,
    conflict resolution rules, and evaluation limits.
    """

    policy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique policy identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable policy name",
    )
    description: str = Field(
        default="",
        description="Policy description and intent",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain this policy applies to",
    )
    allowed_rule_types: list[RuleType] = Field(
        default_factory=list,
        description="Rule types permitted under this policy",
    )
    allowed_actions: list[str] = Field(
        default_factory=list,
        description="Actions permitted under this policy",
    )
    max_rules_per_set: int = Field(
        default=100,
        ge=1,
        description="Maximum number of rules in a single rule set",
    )
    max_evaluation_depth: int = Field(
        default=10,
        ge=1,
        description="Maximum depth for nested condition evaluation",
    )
    conflict_resolution: str = Field(
        default="PRIORITY",
        description="Strategy for resolving rule conflicts (PRIORITY, DENY_OVERRIDE, MOST_SPECIFIC)",
    )
    default_decision: str = Field(
        default="DENY",
        description="Default decision when no rules match",
    )
    enforce_paralysed: bool = Field(
        default=False,
        description="Whether to enforce a paralysed state (deny all) when policy cannot be evaluated",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the policy is currently enabled",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Policy version number",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the policy was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the policy was last updated",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for arbitrary additional data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleHealth
# ─────────────────────────────────────────────────────────────────────────────


class RuleHealth(BaseModel):
    """Health status of the Rule Manager platform.

    Tracks overall and per-component health status for monitoring
    and observability. Enhanced for Phase 3.5 with comprehensive
    component status flags, latency tracking, and error metrics.
    """

    overall_status: str = Field(
        default="HEALTHY",
        description="Overall health: HEALTHY, DEGRADED, or UNHEALTHY",
    )
    coordinator_status: str = Field(
        default="HEALTHY",
        description="RuleCoordinator health",
    )
    validator_status: str = Field(
        default="HEALTHY",
        description="RuleValidator health",
    )
    parser_status: str = Field(
        default="HEALTHY",
        description="RuleParser health",
    )
    compiler_status: str = Field(
        default="HEALTHY",
        description="RuleCompiler health",
    )
    evaluator_status: str = Field(
        default="HEALTHY",
        description="RuleEvaluator health",
    )
    cache_status: str = Field(
        default="HEALTHY",
        description="RuleCache health",
    )
    policy_status: str = Field(
        default="HEALTHY",
        description="RulePolicyEngine health",
    )
    version_status: str = Field(
        default="HEALTHY",
        description="RuleVersionManager health",
    )
    lifecycle_status: str = Field(
        default="HEALTHY",
        description="RuleLifecycleManager health",
    )
    priority_engine_status: str = Field(
        default="HEALTHY",
        description="PriorityEngine health",
    )
    conflict_resolver_status: str = Field(
        default="HEALTHY",
        description="ConflictResolver health",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average latency across all operations in milliseconds",
    )
    average_evaluation_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average rule evaluation time in milliseconds",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Error rate as a fraction of total operations (0.0–1.0)",
    )
    total_rules: int = Field(
        default=0,
        ge=0,
        description="Total number of rules managed",
    )
    total_rulesets: int = Field(
        default=0,
        ge=0,
        description="Total number of rule sets managed",
    )
    total_evaluations: int = Field(
        default=0,
        ge=0,
        description="Total number of evaluations performed",
    )
    rules_evaluated: int = Field(
        default=0,
        ge=0,
        description="Total number of individual rule evaluations performed",
    )
    rule_domains: list[str] = Field(
        default_factory=list,
        description="List of rule domains with active rules",
    )
    last_checked_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the health check was last performed",
    )

    def is_healthy(self) -> bool:
        """Return True if overall status is HEALTHY."""
        return self.overall_status == "HEALTHY"


# ─────────────────────────────────────────────────────────────────────────────
# RuleMetrics
# ─────────────────────────────────────────────────────────────────────────────


class RuleMetrics(BaseModel):
    """Aggregated metrics snapshot for the Rule Manager.

    Provides a point-in-time view of key operational metrics for
    monitoring and observability. Enhanced for Phase 3.5 with
    category, scope, and version tracking.
    """

    rules_total: int = Field(
        default=0,
        ge=0,
        description="Total rules defined",
    )
    rulesets_total: int = Field(
        default=0,
        ge=0,
        description="Total rule sets defined",
    )
    evaluations_total: int = Field(
        default=0,
        ge=0,
        description="Total evaluation operations",
    )
    decisions_total: int = Field(
        default=0,
        ge=0,
        description="Total decisions produced",
    )
    conflicts_total: int = Field(
        default=0,
        ge=0,
        description="Total conflicts detected",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Total cache hits",
    )
    cache_misses: int = Field(
        default=0,
        ge=0,
        description="Total cache misses",
    )
    rules_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Rule count per rule domain",
    )
    rules_per_type: dict[str, int] = Field(
        default_factory=dict,
        description="Rule count per rule type",
    )
    rules_per_category: dict[str, int] = Field(
        default_factory=dict,
        description="Rule count per rule category",
    )
    rules_per_scope: dict[str, int] = Field(
        default_factory=dict,
        description="Rule count per rule scope",
    )
    average_evaluation_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average time to evaluate a rule set in milliseconds",
    )
    average_decision_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average time to produce a decision in milliseconds",
    )
    strategy_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Usage count per evaluation strategy",
    )
    domain_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Usage count per rule domain for evaluations",
    )
    version_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Usage count per rule version number",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the metrics snapshot was taken",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleSession
# ─────────────────────────────────────────────────────────────────────────────


class RuleSession(BaseModel):
    """A rule evaluation session.

    Tracks every evaluation request's lifecycle — who triggered it,
    what rules were evaluated, decisions made, conflicts detected,
    and processing statistics.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    domain: RuleDomain = Field(
        default=RuleDomain.SYSTEM,
        description="The domain being evaluated",
    )
    user_id: str = Field(
        default="",
        description="The user or system that initiated the session",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    evaluation_strategy: EvaluationStrategyType = Field(
        default=EvaluationStrategyType.SEQUENTIAL,
        description="The evaluation strategy used",
    )
    rules_evaluated: list[str] = Field(
        default_factory=list,
        description="Rule IDs evaluated during the session",
    )
    rulesets_evaluated: list[str] = Field(
        default_factory=list,
        description="Rule set IDs evaluated during the session",
    )
    decisions_made: list[RuleDecision] = Field(
        default_factory=list,
        description="Decisions made during the session",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Number of cache hits",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total session duration in milliseconds",
    )
    processing_statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Processing statistics (timing per stage, etc.)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RuleConfidence
# ─────────────────────────────────────────────────────────────────────────────


class RuleConfidence(BaseModel):
    """Aggregated confidence and quality assessment for rule evaluation.

    Produced by RuleConfidenceCalculator from rule completeness,
    version freshness, lifecycle validity, conflict resolution
    quality, policy compliance, and evaluation coverage.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the evaluation (0.0–1.0)",
    )
    rule_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness score based on rule condition coverage (0.0–1.0)",
    )
    version_freshness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Freshness score based on rule version recency (0.0–1.0)",
    )
    lifecycle_validity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Validity score based on lifecycle status appropriateness (0.0–1.0)",
    )
    conflict_quality: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Quality score based on conflict resolution (0.0–1.0)",
    )
    policy_compliance: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Compliance score based on policy adherence (0.0–1.0)",
    )
    evaluation_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Coverage score based on proportion of rules evaluated (0.0–1.0)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ExplainabilityMetadata (rule-specific)
# ─────────────────────────────────────────────────────────────────────────────


class RuleExplainabilityMetadata(BaseModel):
    """Explainability metadata attached to each rule evaluation result.

    Preserves why each rule was applied or skipped, how conflicts
    were resolved, which priority was selected, why policy checks
    failed, and the evaluation strategy used.
    """

    why_rule_selected: str = Field(
        default="",
        description="Reason this rule was selected for evaluation",
    )
    why_rule_applied: str = Field(
        default="",
        description="Reason this rule was applied (e.g. condition matched, priority selected)",
    )
    why_rule_skipped: str = Field(
        default="",
        description="Reason this rule was skipped (if applicable)",
    )
    why_conflict_resolved: str = Field(
        default="",
        description="How conflicts involving this rule were resolved",
    )
    why_priority_selected: str = Field(
        default="",
        description="Rationale for the priority assignment",
    )
    why_policy_failed: str = Field(
        default="",
        description="Reason a policy check failed (if applicable)",
    )
    evaluation_strategy: str = Field(
        default="",
        description="The evaluation strategy that produced this result",
    )
