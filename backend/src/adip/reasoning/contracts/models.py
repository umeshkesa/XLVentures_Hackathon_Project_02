"""Domain models for the Reasoning Engine.

Defines all domain models used across reasoning contracts,
interfaces, and execution components.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.reasoning.enums import (
    ContradictionResolutionStatus,
    ContradictionSeverity,
    HypothesisStatus,
    ReasoningDomain,
    ReasoningStatus,
    ReasoningStrategyType,
)
from adip.reasoning.execution.models import (
    ImpactAssessment,
    RiskAssessment,
    UncertaintyAnalysis,
)

# ─────────────────────────────────────────────────────────────────────────────
# ReasoningRequest
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningRequest(BaseModel):
    """Request to initiate a reasoning operation.

    Captures the input parameters for a reasoning operation,
    including the evidence to reason about, the domain context,
    and the reasoning strategy to apply.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    evidence_package_id: UUID4 = Field(
        description="The evidence package ID to reason about",
    )
    domain: ReasoningDomain = Field(
        default=ReasoningDomain.SYSTEM,
        description="The domain for this reasoning operation",
    )
    strategy: ReasoningStrategyType = Field(
        default=ReasoningStrategyType.HYBRID,
        description="The reasoning strategy to apply",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the reasoning operation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningResult
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningResult(BaseModel):
    """Result of a reasoning operation.

    Captures the complete output of a reasoning operation,
    including the decision, reasoning paths, hypotheses,
    inferences, and confidence assessment.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    request_id: UUID4 = Field(
        description="The request this result belongs to",
    )
    decision: ReasoningDecision | None = Field(
        default=None,
        description="The reasoning decision",
    )
    paths: list[ReasoningPath] = Field(
        default_factory=list,
        description="Reasoning paths explored",
    )
    hypotheses: list[Hypothesis] = Field(
        default_factory=list,
        description="Hypotheses generated during reasoning",
    )
    inferences: list[Inference] = Field(
        default_factory=list,
        description="Inferences made during reasoning",
    )
    contradictions: list[Contradiction] = Field(
        default_factory=list,
        description="Contradictions detected during reasoning",
    )
    confidence: ReasoningConfidence | None = Field(
        default=None,
        description="Confidence assessment for this result",
    )
    status: ReasoningStatus = Field(
        default=ReasoningStatus.INITIALIZED,
        description="Status of the reasoning operation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningDecision
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningDecision(BaseModel):
    """Decision produced by a reasoning operation.

    Captures the final conclusion, reasoning summary, and
    associated confidence for a reasoning operation.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    result_id: UUID4 = Field(
        description="The result this decision belongs to",
    )
    conclusion: str = Field(
        default="",
        description="The final conclusion reached",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of the reasoning that led to this decision",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this decision (0.0–1.0)",
    )
    selected_hypotheses: list[UUID4] = Field(
        default_factory=list,
        description="Hypothesis IDs selected as part of this decision",
    )
    rejected_hypotheses: list[UUID4] = Field(
        default_factory=list,
        description="Hypothesis IDs rejected during reasoning",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    reasoning: str = Field(default="", description="Detailed reasoning for this decision")
    allow_or_deny: str = Field(default="allow", description="Whether the decision allows or denies the action")
    applied_rules: list[str] = Field(default_factory=list, description="Rule IDs applied in this decision")
    skipped_rules: list[str] = Field(default_factory=list, description="Rule IDs skipped in this decision")
    ignored_rules: list[str] = Field(default_factory=list, description="Rule IDs ignored in this decision")
    conflicting_rules: list[str] = Field(default_factory=list, description="Rule IDs with conflicts in this decision")
    risk_assessments: dict[str, RiskAssessment] = Field(
        default_factory=dict,
        description="Risk assessments per risk type",
    )
    impact_assessments: dict[str, ImpactAssessment] = Field(
        default_factory=dict,
        description="Impact assessments per impact type",
    )
    uncertainty: UncertaintyAnalysis | None = Field(
        default=None,
        description="Uncertainty analysis for this decision",
    )
    decision_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Composite decision score (0.0–1.0)",
    )
    ranking_position: int = Field(
        default=0, ge=0,
        description="Position in the ranking of alternatives",
    )
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall decision quality score (0.0–1.0)")
    readiness_status: str = Field(default="NOT_READY", description="Readiness status (READY, NOT_READY, MORE_INFORMATION_REQUIRED)")


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningSession
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningSession(BaseModel):
    """Operational session for a reasoning sequence.

    Tracks the lifecycle of a reasoning operation from
    initialisation through completion or failure.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    request_id: UUID4 = Field(
        description="The request this session belongs to",
    )
    domain: ReasoningDomain = Field(
        default=ReasoningDomain.SYSTEM,
        description="The domain for this session",
    )
    status: ReasoningStatus = Field(
        default=ReasoningStatus.INITIALIZED,
        description="Current session status",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session was completed (None if active)",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Session statistics and timing data",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )
    correlation_id: str = Field(default="", description="Correlation ID for distributed tracing")
    strategy: ReasoningStrategyType = Field(default=ReasoningStrategyType.HYBRID, description="The reasoning strategy used")
    user_id: str = Field(default="", description="User identifier who initiated the session")
    duration_ms: float | None = Field(default=None, description="Session duration in milliseconds")
    hypotheses_count: int = Field(default=0, ge=0, description="Number of hypotheses generated in this session")
    inferences_count: int = Field(default=0, ge=0, description="Number of inferences made in this session")
    contradictions_count: int = Field(default=0, ge=0, description="Number of contradictions detected in this session")
    decisions_count: int = Field(default=0, ge=0, description="Number of decisions produced in this session")


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningContext
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningContext(BaseModel):
    """Contextual metadata for reasoning operations.

    Carries context information such as asset, machine, facility,
    customer, workflow, incident, planner goal, and time window
    that may be relevant during reasoning.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    asset_id: str = Field(
        default="",
        description="Asset identifier associated with this context",
    )
    machine_id: str = Field(
        default="",
        description="Machine identifier associated with this context",
    )
    facility_id: str = Field(
        default="",
        description="Facility identifier associated with this context",
    )
    customer_id: str = Field(
        default="",
        description="Customer identifier associated with this context",
    )
    workflow_id: str = Field(
        default="",
        description="Workflow identifier associated with this context",
    )
    incident_id: str = Field(
        default="",
        description="Incident identifier associated with this context",
    )
    planner_goal: str = Field(
        default="",
        description="The planner goal relevant to this reasoning",
    )
    time_window_start: datetime | None = Field(
        default=None,
        description="Start of the reasoning time window",
    )
    time_window_end: datetime | None = Field(
        default=None,
        description="End of the reasoning time window",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningMetadata
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningMetadata(BaseModel):
    """Metadata for a reasoning operation.

    Captures descriptive metadata about a reasoning operation
    including title, description, tags, category, and source.
    """

    title: str = Field(
        default="",
        description="Title of the reasoning operation",
    )
    description: str = Field(
        default="",
        description="Description of the reasoning operation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags associated with this reasoning",
    )
    category: str = Field(
        default="",
        description="Category classification for this reasoning",
    )
    source: str = Field(
        default="",
        description="Source identifier for this reasoning",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the reasoning definition",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningConfidence
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningConfidence(BaseModel):
    """Confidence assessment for a reasoning result.

    Captures confidence across multiple dimensions: evidence
    quality, hypothesis strength, inference validity, and
    contradiction resolution. Overall confidence is derived
    from the individual dimension scores.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0–1.0)",
    )
    evidence_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality of evidence used in reasoning (0.0–1.0)",
    )
    hypothesis_strength: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Strength of generated hypotheses (0.0–1.0)",
    )
    inference_validity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Validity of inferences made (0.0–1.0)",
    )
    contradiction_resolution: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality of contradiction resolution (0.0–1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional confidence metadata",
    )
    path_consistency: float = Field(default=0.0, ge=0.0, le=1.0, description="Consistency across reasoning paths (0.0–1.0)")
    goal_alignment: float = Field(default=0.0, ge=0.0, le=1.0, description="Alignment of reasoning with goals (0.0–1.0)")
    policy_compliance: float = Field(default=0.0, ge=0.0, le=1.0, description="Policy compliance confidence (0.0–1.0)")
    consensus: float = Field(default=0.0, ge=0.0, le=1.0, description="Consensus score across reasoning paths (0.0–1.0)")


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningHealth
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningHealth(BaseModel):
    """Health status of the Reasoning Engine.

    Provides operational health information for monitoring and
    observability of all reasoning pipeline components.
    """

    overall_status: str = Field(
        default="UNKNOWN",
        description="Overall health status (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)",
    )
    reasoning_count: int = Field(
        default=0,
        ge=0,
        description="Total number of reasoning operations",
    )
    coordinator_status: str = Field(
        default="UNKNOWN",
        description="Status of the reasoning coordinator",
    )
    hypothesis_generator_status: str = Field(
        default="UNKNOWN",
        description="Status of the hypothesis generator",
    )
    inference_engine_status: str = Field(
        default="UNKNOWN",
        description="Status of the inference engine",
    )
    contradiction_detector_status: str = Field(
        default="UNKNOWN",
        description="Status of the contradiction detector",
    )
    validator_status: str = Field(
        default="UNKNOWN",
        description="Status of the reasoning validator",
    )
    path_builder_status: str = Field(
        default="UNKNOWN",
        description="Status of the reasoning path builder",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of reasoning pipeline errors",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average pipeline latency in milliseconds",
    )
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Reasoning engine uptime in seconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )
    context_builder_status: str = Field(default="UNKNOWN", description="Status of the context builder")
    goal_manager_status: str = Field(default="UNKNOWN", description="Status of the goal manager")
    constraint_manager_status: str = Field(default="UNKNOWN", description="Status of the constraint manager")
    assumption_manager_status: str = Field(default="UNKNOWN", description="Status of the assumption manager")
    strategy_selector_status: str = Field(default="UNKNOWN", description="Status of the strategy selector")
    weight_manager_status: str = Field(default="UNKNOWN", description="Status of the weight manager")
    score_calculator_status: str = Field(default="UNKNOWN", description="Status of the score calculator")
    policy_engine_status: str = Field(default="UNKNOWN", description="Status of the policy engine")
    trace_status: str = Field(default="UNKNOWN", description="Status of the trace system")
    metrics_collector_status: str = Field(default="UNKNOWN", description="Status of the metrics collector")
    total_reasonings: int = Field(default=0, ge=0, description="Total number of reasoning operations")
    status: str = Field(default="UNKNOWN", description="Overall health status (HEALTHY, DEGRADED, UNHEALTHY)")


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningMetrics
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningMetrics(BaseModel):
    """Aggregated metrics for the Reasoning Engine.

    Tracks operational metrics for monitoring, alerting, and
    capacity planning of the reasoning pipeline.
    """

    reasoning_total: int = Field(
        default=0,
        ge=0,
        description="Total number of reasoning operations",
    )
    hypotheses_total: int = Field(
        default=0,
        ge=0,
        description="Total number of hypotheses generated",
    )
    inferences_total: int = Field(
        default=0,
        ge=0,
        description="Total number of inferences made",
    )
    contradictions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of contradictions detected",
    )
    contradictions_resolved: int = Field(
        default=0,
        ge=0,
        description="Total number of contradictions resolved",
    )
    paths_total: int = Field(
        default=0,
        ge=0,
        description="Total number of reasoning paths explored",
    )
    decisions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of decisions produced",
    )
    failed_total: int = Field(
        default=0,
        ge=0,
        description="Total number of failed reasoning operations",
    )
    hypotheses_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Hypothesis count per domain",
    )
    inferences_per_strategy: dict[str, int] = Field(
        default_factory=dict,
        description="Inference count per strategy type",
    )
    average_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence across all operations (0.0–1.0)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When these metrics were captured",
    )
    reasonings_per_domain: dict[str, int] = Field(default_factory=dict, description="Reasoning count per domain")
    reasonings_per_strategy: dict[str, int] = Field(default_factory=dict, description="Reasoning count per strategy")
    decisions_per_strategy: dict[str, int] = Field(default_factory=dict, description="Decision count per strategy")
    hypotheses_per_strategy: dict[str, int] = Field(default_factory=dict, description="Hypothesis count per strategy")
    inferences_per_domain: dict[str, int] = Field(default_factory=dict, description="Inference count per domain")
    contradictions_per_severity: dict[str, int] = Field(default_factory=dict, description="Contradictions per severity level")
    average_latency_ms: float = Field(default=0.0, ge=0.0, description="Average pipeline latency in milliseconds")
    total_sessions: int = Field(default=0, ge=0, description="Total number of reasoning sessions")


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningTrace
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningTrace(BaseModel):
    """Trace record for a reasoning pipeline stage.

    Captures timing, success/failure, and metadata for a single
    stage in the reasoning pipeline for observability.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        default="",
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        default="",
        description="The operation being performed",
    )
    reasoning_id: str = Field(
        default="",
        description="The reasoning ID being processed",
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


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningPath & ReasoningStep
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningStep(BaseModel):
    """A single step within a reasoning path.

    Represents one atomic reasoning operation within a larger
    reasoning path, capturing inputs, outputs, and metadata.
    """

    step_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique step identifier",
    )
    path_id: UUID4 = Field(
        description="The reasoning path this step belongs to",
    )
    step_type: str = Field(
        default="",
        description="Type of reasoning step (deduction, induction, abduction, etc.)",
    )
    description: str = Field(
        default="",
        description="Description of this reasoning step",
    )
    inputs: list[str] = Field(
        default_factory=list,
        description="Input evidence or hypotheses for this step",
    )
    outputs: list[str] = Field(
        default_factory=list,
        description="Output conclusions or inferences from this step",
    )
    inference_id: UUID4 | None = Field(
        default=None,
        description="Associated inference ID if this step produced one",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this step (0.0–1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional step metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the step was created",
    )


class ReasoningPath(BaseModel):
    """A complete reasoning path from evidence to conclusion.

    Represents one full reasoning chain consisting of ordered
    steps, associated inferences, and decision nodes.
    """

    path_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique path identifier",
    )
    request_id: UUID4 = Field(
        description="The request this path belongs to",
    )
    strategy: ReasoningStrategyType = Field(
        default=ReasoningStrategyType.HYBRID,
        description="The reasoning strategy used for this path",
    )
    steps: list[ReasoningStep] = Field(
        default_factory=list,
        description="Ordered list of reasoning steps in this path",
    )
    inferences: list[UUID4] = Field(
        default_factory=list,
        description="Inference IDs associated with this path",
    )
    decision_nodes: list[UUID4] = Field(
        default_factory=list,
        description="Decision node IDs in this path",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this path is still active/valid",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence for this path (0.0–1.0)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the path was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional path metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hypothesis & HypothesisSet
# ─────────────────────────────────────────────────────────────────────────────


class Hypothesis(BaseModel):
    """A hypothesis generated during reasoning.

    Represents a proposed explanation or conclusion that can
    be supported or contradicted by evidence.
    """

    hypothesis_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique hypothesis identifier",
    )
    description: str = Field(
        default="",
        description="Description of this hypothesis",
    )
    supporting_evidence: list[UUID4] = Field(
        default_factory=list,
        description="Evidence IDs that support this hypothesis",
    )
    contradicting_evidence: list[UUID4] = Field(
        default_factory=list,
        description="Evidence IDs that contradict this hypothesis",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this hypothesis (0.0–1.0)",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Priority of this hypothesis (higher = more important)",
    )
    status: HypothesisStatus = Field(
        default=HypothesisStatus.PROPOSED,
        description="Current status of this hypothesis",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional hypothesis metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the hypothesis was created",
    )


class HypothesisSet(BaseModel):
    """A set of hypotheses grouped for reasoning.

    Groups related hypotheses together within a reasoning
    operation for coherent evaluation.
    """

    set_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique set identifier",
    )
    request_id: UUID4 = Field(
        description="The request this set belongs to",
    )
    hypotheses: list[Hypothesis] = Field(
        default_factory=list,
        description="Hypotheses in this set",
    )
    domain: ReasoningDomain = Field(
        default=ReasoningDomain.SYSTEM,
        description="The domain for this hypothesis set",
    )
    description: str = Field(
        default="",
        description="Description of this hypothesis set",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the set was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional set metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Inference & InferenceChain
# ─────────────────────────────────────────────────────────────────────────────


class Inference(BaseModel):
    """An inference made during reasoning.

    Represents a logical conclusion drawn from premises,
    evidence, or hypotheses during reasoning.
    """

    inference_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique inference identifier",
    )
    hypothesis_id: UUID4 | None = Field(
        default=None,
        description="The hypothesis this inference relates to",
    )
    rule_id: str = Field(
        default="",
        description="Identifier of the rule used for this inference",
    )
    premise: str = Field(
        default="",
        description="The premise or starting point for this inference",
    )
    conclusion: str = Field(
        default="",
        description="The conclusion reached by this inference",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this inference (0.0–1.0)",
    )
    inference_type: str = Field(
        default="",
        description="Type of inference (deductive, inductive, abductive, etc.)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional inference metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the inference was made",
    )


class InferenceChain(BaseModel):
    """A chain of linked inferences.

    Represents a sequence of inferences connecting a starting
    hypothesis to a final conclusion through intermediate steps.
    """

    chain_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique chain identifier",
    )
    request_id: UUID4 = Field(
        description="The request this chain belongs to",
    )
    inferences: list[Inference] = Field(
        default_factory=list,
        description="Ordered list of inferences in this chain",
    )
    start_hypothesis_id: UUID4 | None = Field(
        default=None,
        description="The starting hypothesis ID",
    )
    end_conclusion: str = Field(
        default="",
        description="The final conclusion of this inference chain",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in this chain (0.0–1.0)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the chain was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional chain metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Contradiction
# ─────────────────────────────────────────────────────────────────────────────


class Contradiction(BaseModel):
    """A contradiction detected during reasoning.

    Represents conflicting evidence, hypotheses, or inferences
    that need resolution for coherent reasoning.
    """

    contradiction_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique contradiction identifier",
    )
    request_id: UUID4 = Field(
        description="The request this contradiction belongs to",
    )
    conflicting_items: list[str] = Field(
        default_factory=list,
        description="Identifiers of conflicting items (evidence, hypotheses, inferences)",
    )
    severity: ContradictionSeverity = Field(
        default=ContradictionSeverity.MEDIUM,
        description="Severity of this contradiction",
    )
    resolution_status: ContradictionResolutionStatus = Field(
        default=ContradictionResolutionStatus.UNRESOLVED,
        description="Resolution status of this contradiction",
    )
    description: str = Field(
        default="",
        description="Description of the contradiction",
    )
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the contradiction was detected",
    )
    resolved_at: datetime | None = Field(
        default=None,
        description="When the contradiction was resolved (None if unresolved)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional contradiction metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningStrategyConfig
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningStrategyConfig(BaseModel):
    """A reasoning strategy configuration.

    Defines a strategy for reasoning, including its type,
    configuration parameters, target domain, and activation status.
    """

    strategy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique strategy identifier",
    )
    strategy_type: ReasoningStrategyType = Field(
        description="The type of this reasoning strategy",
    )
    name: str = Field(
        default="",
        description="Human-readable name for this strategy",
    )
    description: str = Field(
        default="",
        description="Description of this strategy",
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration parameters for this strategy",
    )
    domain: ReasoningDomain | None = Field(
        default=None,
        description="Target domain (None for all domains)",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this strategy is active",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Priority of this strategy (higher = preferred)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the strategy was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional strategy metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReasoningExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class ReasoningExplainabilityMetadata(BaseModel):
    """Explainability metadata for reasoning decisions.

    Captures why certain hypotheses, inferences, contradictions,
    alternatives, policies, and confidence scores were produced
    during a reasoning operation.
    """

    why_hypothesis_selected: str = Field(default="", description="Why a hypothesis was selected")
    why_hypothesis_rejected: str = Field(default="", description="Why a hypothesis was rejected")
    why_inference_drawn: str = Field(default="", description="Why an inference was drawn")
    why_contradiction_detected: str = Field(default="", description="Why a contradiction was detected")
    why_alternative_selected: str = Field(default="", description="Why an alternative was selected")
    why_alternative_rejected: str = Field(default="", description="Why an alternative was rejected")
    why_policy_applied: str = Field(default="", description="Why a policy was applied")
    why_confidence_calculated: str = Field(default="", description="Why confidence was calculated")
    strategy_used: str = Field(default="", description="The reasoning strategy used")
    reasoning_steps: list[str] = Field(default_factory=list, description="List of reasoning steps")
    why_strategy_selected: str = Field(default="", description="Why this strategy was selected")
    why_goal_chosen: str = Field(default="", description="Why this goal was chosen")
    why_assumption_made: str = Field(default="", description="Why this assumption was made")
    why_constraint_applied: str = Field(default="", description="Why this constraint was applied")
    why_primary_selected: str = Field(default="", description="Why the primary decision was selected")
    why_alternative_rejected: str = Field(default="", description="Why the alternative was rejected")
