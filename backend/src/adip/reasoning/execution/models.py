"""Execution-layer models for the Reasoning Engine Phase 2.

Internal models used by execution components during reasoning
pipeline processing. Not part of the public API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.reasoning.enums import (
    AlternativeStatus,
    AssumptionStatus,
    ConstraintType,
    PolicyType,
    ReasoningGoalType,
    ReasoningStrategyType,
)


class ReasoningGoal(BaseModel):
    """A reasoning goal that drives the reasoning process.

    Goals define the objective of a reasoning operation and
    influence strategy selection, hypothesis generation, and
    evaluation criteria.
    """

    goal_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique goal identifier",
    )
    goal_type: ReasoningGoalType = Field(
        description="The type of reasoning goal",
    )
    description: str = Field(
        default="",
        description="Description of this goal",
    )
    priority: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Priority of this goal (0–10, higher = more important)",
    )
    is_primary: bool = Field(
        default=True,
        description="Whether this is the primary goal",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for this goal",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional goal metadata",
    )


class Constraint(BaseModel):
    """A constraint that bounds the reasoning process.

    Constraints define limits, requirements, or conditions
    that must be satisfied during reasoning.
    """

    constraint_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique constraint identifier",
    )
    constraint_type: ConstraintType = Field(
        description="The type of this constraint",
    )
    description: str = Field(
        default="",
        description="Description of this constraint",
    )
    value: float = Field(
        default=0.0,
        description="Numeric value for this constraint",
    )
    unit: str = Field(
        default="",
        description="Unit of measurement for the value",
    )
    is_hard: bool = Field(
        default=True,
        description="Whether this is a hard (required) or soft (preferred) constraint",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this constraint is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional constraint metadata",
    )


class Assumption(BaseModel):
    """An assumption made during reasoning.

    Assumptions are propositions taken as true for the
    purpose of reasoning, tracked for validation and
    explainability.
    """

    assumption_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique assumption identifier",
    )
    description: str = Field(
        default="",
        description="Description of this assumption",
    )
    status: AssumptionStatus = Field(
        default=AssumptionStatus.ACTIVE,
        description="Current status of this assumption",
    )
    source: str = Field(
        default="",
        description="Source of this assumption (user, system, rule, etc.)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the assumption was created",
    )
    validated_at: datetime | None = Field(
        default=None,
        description="When the assumption was validated (None if not validated)",
    )
    invalidated_at: datetime | None = Field(
        default=None,
        description="When the assumption was invalidated (None if not invalidated)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional assumption metadata",
    )


class ReasoningAlternative(BaseModel):
    """A candidate decision alternative.

    Represents one possible decision outcome with associated
    confidence, reasoning, and supporting evidence.
    """

    alternative_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique alternative identifier",
    )
    decision_description: str = Field(
        default="",
        description="Description of this decision alternative",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this alternative (0.0–1.0)",
    )
    reasoning: list[str] = Field(
        default_factory=list,
        description="Reasoning steps supporting this alternative",
    )
    supporting_evidence: list[str] = Field(
        default_factory=list,
        description="Evidence IDs supporting this alternative",
    )
    status: AlternativeStatus = Field(
        default=AlternativeStatus.CANDIDATE,
        description="Current status of this alternative",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Evaluation score for this alternative (0.0–1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional alternative metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the alternative was created",
    )


class ReasoningScore(BaseModel):
    """Scoring assessment for a reasoning result.

    Evaluates reasoning quality across multiple dimensions:
    consistency, coverage, completeness, rule satisfaction,
    and assumption quality.
    """

    consistency: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consistency score (0.0–1.0)",
    )
    coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Coverage score (0.0–1.0)",
    )
    completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness score (0.0–1.0)",
    )
    rule_satisfaction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Rule satisfaction score (0.0–1.0)",
    )
    assumption_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Assumption quality score (0.0–1.0)",
    )
    overall: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall reasoning score (0.0–1.0)",
    )


class PolicyDecision(BaseModel):
    """Result of a policy check during reasoning.

    Captures whether a reasoning operation or decision
    complies with the configured policy.
    """

    policy_type: PolicyType = Field(
        default=PolicyType.BALANCED,
        description="The policy type used for this decision",
    )
    allowed: bool = Field(
        default=True,
        description="Whether the operation is allowed by policy",
    )
    reasoning: list[str] = Field(
        default_factory=list,
        description="Reasoning for the policy decision",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the policy decision (0.0–1.0)",
    )


class ReasoningGraphNode(BaseModel):
    """A node in the reasoning inference graph.

    Represents an evidence item, hypothesis, inference,
    or decision within the reasoning graph.
    """

    node_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique node identifier",
    )
    node_type: str = Field(
        default="",
        description="Type of node (evidence, hypothesis, inference, decision)",
    )
    label: str = Field(
        default="",
        description="Human-readable label for this node",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional data for this node",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional node metadata",
    )


class ReasoningGraphEdge(BaseModel):
    """An edge in the reasoning inference graph.

    Represents a relationship between two nodes in the
    reasoning graph, such as supports, contradicts, or
    leads_to.
    """

    edge_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique edge identifier",
    )
    source_id: UUID4 = Field(
        description="Source node ID",
    )
    target_id: UUID4 = Field(
        description="Target node ID",
    )
    edge_type: str = Field(
        default="",
        description="Type of edge (supports, contradicts, leads_to, etc.)",
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Weight of this edge (0.0–1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge metadata",
    )


class ReasoningGraph(BaseModel):
    """An inference graph for reasoning.

    Captures the complete graph structure of a reasoning
    operation, including nodes, edges, decision paths,
    and alternative paths.
    """

    graph_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique graph identifier",
    )
    nodes: list[ReasoningGraphNode] = Field(
        default_factory=list,
        description="Nodes in this reasoning graph",
    )
    edges: list[ReasoningGraphEdge] = Field(
        default_factory=list,
        description="Edges in this reasoning graph",
    )
    decision_paths: list[list[UUID4]] = Field(
        default_factory=list,
        description="Ordered node IDs forming decision paths",
    )
    alternative_paths: list[list[UUID4]] = Field(
        default_factory=list,
        description="Ordered node IDs forming alternative paths",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional graph metadata",
    )


class GoalConfig(BaseModel):
    """Configuration for a reasoning goal.

    Defines parameters and settings for a specific goal
    type to guide reasoning behaviour.
    """

    goal_type: ReasoningGoalType = Field(
        description="The goal type this config applies to",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Goal-specific parameters",
    )
    priority: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Default priority for this goal type",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional config metadata",
    )


class TraceRecord(BaseModel):
    """Trace record for a reasoning pipeline stage.

    Captures timing, stage info, and metadata for a single
    pipeline stage in the reasoning process.
    """

    trace_id: str = Field(
        default="",
        description="Unique trace record identifier",
    )
    stage_name: str = Field(
        default="",
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        default="",
        description="The operation being traced",
    )
    reasoning_id: str = Field(
        default="",
        description="The reasoning ID associated with this trace",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage started",
    )
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage completed",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Stage duration in milliseconds",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed successfully",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings generated during this stage",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors generated during this stage",
    )


class ReasoningMetrics(BaseModel):
    """Snapshot of reasoning pipeline metrics.

    Captures counts and statistics for a reasoning operation
    at a point in time.
    """

    metrics_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique metrics identifier",
    )
    hypotheses_count: int = Field(
        default=0, ge=0, description="Total hypotheses generated",
    )
    alternatives_count: int = Field(
        default=0, ge=0, description="Total alternatives generated",
    )
    constraints_count: int = Field(
        default=0, ge=0, description="Total constraints evaluated",
    )
    contradictions_count: int = Field(
        default=0, ge=0, description="Total contradictions detected",
    )
    goals_count: int = Field(
        default=0, ge=0, description="Total goals tracked",
    )
    average_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Average reasoning score",
    )
    trace_count: int = Field(
        default=0, ge=0, description="Total trace records",
    )
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When metrics were collected",
    )
    reasonings_count: int = Field(default=0, ge=0, description="Total reasoning operations")
    sessions_count: int = Field(default=0, ge=0, description="Total sessions")
    average_latency_ms: float = Field(default=0.0, ge=0.0, description="Average latency in ms")
    reasonings_per_domain: dict[str, int] = Field(default_factory=dict)
    reasonings_per_strategy: dict[str, int] = Field(default_factory=dict)
    decisions_per_strategy: dict[str, int] = Field(default_factory=dict)
    hypotheses_per_strategy: dict[str, int] = Field(default_factory=dict)
    inferences_per_domain: dict[str, int] = Field(default_factory=dict)
    contradictions_per_severity: dict[str, int] = Field(default_factory=dict)
    review_count: int = Field(default=0, ge=0, description="Total reviews performed")
    readiness_ready: int = Field(default=0, ge=0, description="Decisions marked READY")
    readiness_not_ready: int = Field(default=0, ge=0, description="Decisions marked NOT_READY")
    readiness_more_info: int = Field(default=0, ge=0, description="Decisions needing more info")
    average_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Average decision quality score")


class RiskAssessment(BaseModel):
    """Risk assessment for a reasoning alternative.

    Captures risk type, score (0.0–1.0), level (LOW/MEDIUM/HIGH),
    contributing factors, and recommendations for mitigation.
    """

    risk_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique risk identifier",
    )
    risk_type: str = Field(
        default="",
        description="Type of risk (composite, financial, operational, etc.)",
    )
    score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Risk score (0.0 = no risk, 1.0 = maximum risk)",
    )
    level: str = Field(
        default="LOW",
        description="Risk level (LOW, MEDIUM, HIGH)",
    )
    description: str = Field(
        default="",
        description="Description of this risk",
    )
    factors: dict[str, float] = Field(
        default_factory=dict,
        description="Contributing factors and their scores",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for risk mitigation",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the risk was assessed",
    )


class ImpactAssessment(BaseModel):
    """Impact assessment for a reasoning alternative.

    Captures impact type, score (0.0–1.0), quantitative value,
    unit, and detailed breakdown.
    """

    impact_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique impact identifier",
    )
    impact_type: str = Field(
        default="",
        description="Type of impact (composite, financial, operational, etc.)",
    )
    score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Impact score (0.0 = no impact, 1.0 = maximum impact)",
    )
    description: str = Field(
        default="",
        description="Description of this impact",
    )
    quantitative_value: float = Field(
        default=0.0,
        description="Quantitative value for this impact",
    )
    unit: str = Field(
        default="",
        description="Unit of measurement for the quantitative value",
    )
    details: dict[str, float] = Field(
        default_factory=dict,
        description="Detailed impact breakdown",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the impact was assessed",
    )


class UncertaintyAnalysis(BaseModel):
    """Uncertainty analysis for a reasoning operation.

    Captures sources of uncertainty, criticality (0.0–1.0),
    and detailed breakdown of contributing factors.
    """

    uncertainty_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique uncertainty identifier",
    )
    uncertainty_type: str = Field(
        default="",
        description="Type of uncertainty (missing_information, unknown_variables, conflicting_evidence)",
    )
    description: str = Field(
        default="",
        description="Description of this uncertainty",
    )
    criticality: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Criticality of this uncertainty (0.0–1.0)",
    )
    source: str = Field(
        default="",
        description="Source of this uncertainty",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed uncertainty breakdown",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the uncertainty was analysed",
    )


class MemoryEntry(BaseModel):
    """A stored memory entry for reasoning state.

    Captures a key-value pair with type classification,
    data payload, timestamp, and metadata.
    """

    entry_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique memory entry identifier",
    )
    key: str = Field(
        default="",
        description="Key for this memory entry",
    )
    entry_type: str = Field(
        default="",
        description="Type of entry (context, alternative, risk, impact, uncertainty, decision)",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Data payload for this entry",
    )
    stored_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the entry was stored",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional entry metadata",
    )


class DecisionComparison(BaseModel):
    """Comparison of a decision alternative across multiple criteria.

    Captures confidence, risk, impact, constraint satisfaction,
    cost, and composite scores for a single alternative comparison.
    """

    comparison_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique comparison identifier",
    )
    alternative_id: str = Field(
        default="",
        description="The alternative ID being compared",
    )
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Confidence score for this alternative (0.0–1.0)",
    )
    risk_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Risk score for this alternative (0.0–1.0)",
    )
    impact_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Impact score for this alternative (0.0–1.0)",
    )
    constraint_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Constraint satisfaction score (0.0–1.0)",
    )
    cost_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Cost score for this alternative (0.0–1.0)",
    )
    composite_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Composite multi-criteria score (0.0–1.0)",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional comparison details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the comparison was made",
    )


class DecisionQuality(BaseModel):
    """Quality assessment for a reasoning decision.

    Captures quality across multiple dimensions: evidence coverage,
    rule coverage, goal satisfaction, constraint satisfaction,
    and assumption completeness.
    """

    quality_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique quality identifier",
    )
    evidence_coverage: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Proportion of evidence covered (0.0–1.0)",
    )
    rule_coverage: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Proportion of rules applied (0.0–1.0)",
    )
    goal_satisfaction: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Proportion of goals achieved (0.0–1.0)",
    )
    constraint_satisfaction: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Proportion of constraints satisfied (0.0–1.0)",
    )
    assumption_completeness: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Proportion of assumptions validated (0.0–1.0)",
    )
    overall: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Overall quality score (0.0–1.0)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the quality was assessed",
    )


class ReviewResult(BaseModel):
    """Result of a reasoning review.

    Aggregates reviews across goals, constraints, assumptions,
    contradictions, risks, alternatives, and confidence into
    a single review result with pass/fail, score, warnings, and errors.
    """

    review_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique review identifier",
    )
    passed: bool = Field(
        default=False,
        description="Whether the review passed all checks",
    )
    overall_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Overall review score (0.0–1.0)",
    )
    goal_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Goal review results",
    )
    constraint_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Constraint review results",
    )
    assumption_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Assumption review results",
    )
    contradiction_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Contradiction review results",
    )
    risk_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Risk review results",
    )
    alternative_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Alternative review results",
    )
    confidence_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Confidence review results",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings generated during review",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors generated during review",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the review was performed",
    )


class DecisionJustificationModel(BaseModel):
    """Justification for a reasoning decision.

    Captures all supporting evidence, rules, constraints, assumptions,
    risks, and alternatives that justify a decision.
    """

    justification_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique justification identifier",
    )
    supporting_evidence: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Supporting evidence items",
    )
    rules_used: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Rules used in the decision",
    )
    constraints_used: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Constraints used in the decision",
    )
    assumptions_used: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Assumptions used in the decision",
    )
    risks_assessed: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Risks assessed for the decision",
    )
    alternatives: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Decision alternatives considered",
    )
    selected_alternative: dict[str, Any] | None = Field(
        default=None,
        description="The selected alternative, if any",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the justification was built",
    )


class ReasoningLineageModel(BaseModel):
    """Lineage trace for a reasoning operation.

    Captures the complete lineage from evidence through hypotheses,
    inferences, alternatives, to the final decision.
    """

    lineage_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique lineage identifier",
    )
    evidence: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence items in the lineage",
    )
    hypotheses: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Hypotheses in the lineage",
    )
    inferences: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Inferences in the lineage",
    )
    alternatives: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Alternatives in the lineage",
    )
    final_decision: dict[str, Any] | None = Field(
        default=None,
        description="Final decision in the lineage",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the lineage was built",
    )


class ReasoningSnapshotModel(BaseModel):
    """Immutable snapshot of a reasoning state.

    Captures the complete reasoning state at a point in time,
    including context, graph, alternatives, confidence, risks,
    impacts, and metadata.
    """

    snapshot_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique snapshot identifier",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Reasoning context at snapshot time",
    )
    graph: dict[str, Any] | None = Field(
        default=None,
        description="Reasoning graph at snapshot time",
    )
    alternatives: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Alternatives at snapshot time",
    )
    confidence: dict[str, Any] | None = Field(
        default=None,
        description="Confidence at snapshot time",
    )
    risks: dict[str, Any] = Field(
        default_factory=dict,
        description="Risk assessments at snapshot time",
    )
    impacts: dict[str, Any] = Field(
        default_factory=dict,
        description="Impact assessments at snapshot time",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional snapshot metadata",
    )
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was captured",
    )


class StrategyPerformanceRecord(BaseModel):
    """Performance record for a reasoning strategy.

    Tracks execution statistics for a specific reasoning strategy,
    including total executions, successes, failures, latency,
    and confidence.
    """

    strategy: ReasoningStrategyType = Field(
        description="The reasoning strategy type",
    )
    total_executions: int = Field(
        default=0, ge=0,
        description="Total number of executions",
    )
    successful: int = Field(
        default=0, ge=0,
        description="Number of successful executions",
    )
    failed: int = Field(
        default=0, ge=0,
        description="Number of failed executions",
    )
    total_latency_ms: float = Field(
        default=0.0, ge=0.0,
        description="Total latency across all executions in milliseconds",
    )
    total_confidence: float = Field(
        default=0.0, ge=0.0,
        description="Total confidence across all executions",
    )
    last_executed: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the strategy was last executed",
    )
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this record was created",
    )


class DecisionReadinessResult(BaseModel):
    """Result of a decision readiness assessment.

    Determines whether a decision is ready to be made based on
    confidence, risk, uncertainty, contradictions, constraints,
    alternatives, and quality score.
    """

    decision_id: str = Field(
        default="",
        description="Identifier for the decision being assessed",
    )
    readiness: str = Field(
        default="NOT_READY",
        description="Readiness status (READY, NOT_READY, MORE_INFORMATION_REQUIRED)",
    )
    overall_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Overall readiness score (0.0–1.0)",
    )
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Confidence component score (0.0–1.0)",
    )
    risk_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Risk component score (0.0–1.0)",
    )
    quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Quality component score (0.0–1.0)",
    )
    factors: dict[str, Any] = Field(
        default_factory=dict,
        description="Factors influencing the readiness assessment",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for achieving readiness",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the readiness was assessed",
    )


class DecisionQuality(BaseModel):
    quality_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    rule_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    goal_satisfaction: float = Field(default=0.0, ge=0.0, le=1.0)
    constraint_satisfaction: float = Field(default=0.0, ge=0.0, le=1.0)
    assumption_completeness: float = Field(default=0.0, ge=0.0, le=1.0)
    overall: float = Field(default=0.0, ge=0.0, le=1.0)


class ReviewResult(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    passed: bool = Field(default=True)
    overall_score: float = Field(default=1.0, ge=0.0, le=1.0)
    goal_review: dict[str, Any] = Field(default_factory=dict)
    constraint_review: dict[str, Any] = Field(default_factory=dict)
    assumption_review: dict[str, Any] = Field(default_factory=dict)
    contradiction_review: dict[str, Any] = Field(default_factory=dict)
    risk_review: dict[str, Any] = Field(default_factory=dict)
    alternative_review: dict[str, Any] = Field(default_factory=dict)
    confidence_review: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
