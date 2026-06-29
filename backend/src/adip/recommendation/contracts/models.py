"""Domain models for the Recommendation Engine.

Defines all domain models used across recommendation contracts,
interfaces, and execution components.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.recommendation.enums import (
    BenefitType,
    ConstraintType,
    RecommendationDomain,
    RecommendationStatus,
)
from adip.recommendation.enums import (
    RecommendationGoal as RecommendationGoalEnum,
)
from adip.recommendation.enums import (
    RecommendationPriority as RecommendationPriorityEnum,
)
from adip.recommendation.enums import (
    RecommendationStrategy as RecommendationStrategyEnum,
)


class RecommendationRequest(BaseModel):
    """Request to initiate a recommendation operation.

    Captures the input parameters for a recommendation operation,
    including the reasoning result to transform and the context
    for generating actionable business recommendations.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    reasoning_result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="The reasoning result ID to transform into recommendations",
    )
    domain: RecommendationDomain = Field(
        default=RecommendationDomain.GENERAL,
        description="The domain for this recommendation operation",
    )
    strategy: RecommendationStrategyEnum = Field(
        default=RecommendationStrategyEnum.NEXT_BEST_ACTION,
        description="The recommendation strategy to apply",
    )
    goals: list[RecommendationGoalEnum] = Field(
        default_factory=list,
        description="The goals for this recommendation operation",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the recommendation operation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was created",
    )


class RecommendationResult(BaseModel):
    """Result of a recommendation operation.

    Captures the complete output of a recommendation operation,
    including the decision, package, candidates, and confidence assessment.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    request_id: UUID4 = Field(
        description="The request this result belongs to",
    )
    decision: RecommendationDecision | None = Field(
        default=None,
        description="The recommendation decision",
    )
    package: RecommendationPackage | None = Field(
        default=None,
        description="The recommendation package",
    )
    candidates: list[RecommendationCandidate] = Field(
        default_factory=list,
        description="Recommendation candidates generated",
    )
    confidence: RecommendationConfidence | None = Field(
        default=None,
        description="Confidence assessment for this result",
    )
    readiness: str = Field(
        default="",
        description="Readiness assessment for this result",
    )
    status: RecommendationStatus = Field(
        default=RecommendationStatus.INITIALIZED,
        description="Status of the recommendation operation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata",
    )


class RecommendationDecision(BaseModel):
    """Decision produced by a recommendation operation.

    Captures the final recommendation decision, selected and rejected
    candidates, and the associated recommendation package.
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
        description="The final recommendation conclusion",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of the reasoning that led to this recommendation",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this recommendation (0.0-1.0)",
    )
    selected_candidates: list[str] = Field(
        default_factory=list,
        description="Candidate IDs selected as part of this decision",
    )
    rejected_candidates: list[str] = Field(
        default_factory=list,
        description="Candidate IDs rejected during recommendation",
    )
    package: RecommendationPackage | None = Field(
        default=None,
        description="The recommendation package",
    )
    business_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Business value score for the decision (0.0-1.0)",
    )
    primary_recommendation: str = Field(
        default="",
        description="The primary recommended action",
    )
    alternative_recommendations: list[str] = Field(
        default_factory=list,
        description="Alternative recommended actions",
    )
    portfolio: dict[str, Any] | None = Field(
        default=None,
        description="Portfolio of recommendation decisions",
    )
    feasibility: str = Field(
        default="UNKNOWN",
        description="Feasibility assessment result",
    )
    readiness: str = Field(
        default="UNKNOWN",
        description="Readiness assessment result",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score for this decision (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )


class RecommendationPackage(BaseModel):
    """A packaged set of recommendation candidates.

    Groups a primary recommendation with alternate candidates,
    merged benefits, risks, and overall impact assessment.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    result_id: UUID4 = Field(
        description="The result this package belongs to",
    )
    primary_candidate: RecommendationCandidate | None = Field(
        default=None,
        description="The primary recommended candidate",
    )
    alternate_candidates: list[RecommendationCandidate] = Field(
        default_factory=list,
        description="Alternate recommendation candidates",
    )
    merged_benefits: list[RecommendationBenefit] = Field(
        default_factory=list,
        description="Merged benefits across all candidates",
    )
    merged_risks: list[RecommendationRisk] = Field(
        default_factory=list,
        description="Merged risks across all candidates",
    )
    overall_impact: RecommendationImpact | None = Field(
        default=None,
        description="Overall impact assessment for the package",
    )
    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for the package (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was created",
    )


class RecommendationCandidate(BaseModel):
    """A single recommendation candidate.

    Represents one proposed action or decision with its expected
    benefits, risks, impact, and confidence assessment.
    """

    candidate_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique candidate identifier",
    )
    description: str = Field(
        default="",
        description="Description of this recommendation candidate",
    )
    action: str = Field(
        default="",
        description="The recommended action to take",
    )
    domain: RecommendationDomain = Field(
        default=RecommendationDomain.GENERAL,
        description="The domain for this candidate",
    )
    strategy: RecommendationStrategyEnum = Field(
        default=RecommendationStrategyEnum.NEXT_BEST_ACTION,
        description="The strategy used for this candidate",
    )
    priority: RecommendationPriorityEnum = Field(
        default=RecommendationPriorityEnum.MEDIUM,
        description="Priority level of this candidate",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this candidate (0.0-1.0)",
    )
    expected_benefits: list[RecommendationBenefit] = Field(
        default_factory=list,
        description="Expected benefits of this candidate",
    )
    expected_risks: list[RecommendationRisk] = Field(
        default_factory=list,
        description="Expected risks of this candidate",
    )
    estimated_impact: RecommendationImpact | None = Field(
        default=None,
        description="Estimated impact of this candidate",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall candidate score (0.0-1.0)",
    )
    reasoning: str = Field(
        default="",
        description="Reasoning behind this recommendation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional candidate metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the candidate was created",
    )


class RecommendationStrategy(BaseModel):
    """Strategy configuration for generating recommendations.

    Defines the strategy to use for generating recommendations,
    including its type, configuration, and activation status.
    """

    strategy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique strategy identifier",
    )
    strategy_type: RecommendationStrategyEnum = Field(
        default=RecommendationStrategyEnum.NEXT_BEST_ACTION,
        description="The type of this recommendation strategy",
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
    domain: RecommendationDomain | None = Field(
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


class RecommendationGoal(BaseModel):
    """A recommendation goal configuration.

    Defines a goal for recommendation operations, including its
    type, target value, and priority.
    """

    goal_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique goal identifier",
    )
    goal_type: RecommendationGoalEnum = Field(
        default=RecommendationGoalEnum.REDUCE_DOWNTIME,
        description="The type of this recommendation goal",
    )
    name: str = Field(
        default="",
        description="Human-readable name for this goal",
    )
    description: str = Field(
        default="",
        description="Description of this goal",
    )
    target_value: float | None = Field(
        default=None,
        description="Target value for this goal",
    )
    priority: int = Field(
        default=0,
        ge=0,
        description="Priority of this goal (higher = more important)",
    )
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary goal",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional goal metadata",
    )


class RecommendationContext(BaseModel):
    """Contextual metadata for recommendation operations.

    Carries context information such as asset, machine, facility,
    customer, workflow, and time window for recommendations.
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
        description="The planner goal relevant to this recommendation",
    )
    time_window_start: datetime | None = Field(
        default=None,
        description="Start of the recommendation time window",
    )
    time_window_end: datetime | None = Field(
        default=None,
        description="End of the recommendation time window",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


class RecommendationConstraint(BaseModel):
    """A constraint on a recommendation operation.

    Defines constraints that must be satisfied for a recommendation
    to be valid, including hard, soft, budget, and time constraints.
    """

    constraint_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique constraint identifier",
    )
    constraint_type: ConstraintType = Field(
        default=ConstraintType.HARD,
        description="The type of this constraint",
    )
    name: str = Field(
        default="",
        description="Human-readable name for this constraint",
    )
    description: str = Field(
        default="",
        description="Description of this constraint",
    )
    value: float | None = Field(
        default=None,
        description="The constraint value",
    )
    unit: str = Field(
        default="",
        description="The unit of measurement for the constraint value",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this constraint is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional constraint metadata",
    )


class RecommendationPriority(BaseModel):
    """Priority assignment for a recommendation.

    Defines the priority level, score, and ordering for a
    recommendation to support ranking.
    """

    priority_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique priority identifier",
    )
    level: RecommendationPriorityEnum = Field(
        default=RecommendationPriorityEnum.MEDIUM,
        description="Priority level",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Priority score (0.0-1.0)",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Ordering position for this priority",
    )
    reason: str = Field(
        default="",
        description="Reason for this priority assignment",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional priority metadata",
    )


class RecommendationImpact(BaseModel):
    """Impact assessment for a recommendation.

    Captures the estimated impact of a recommendation across
    multiple dimensions including cost, time, safety, and quality.
    """

    impact_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique impact identifier",
    )
    cost_impact: float = Field(
        default=0.0,
        description="Estimated cost impact",
    )
    time_impact: float = Field(
        default=0.0,
        description="Estimated time impact in hours",
    )
    safety_impact: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Safety impact score (0.0-1.0)",
    )
    quality_impact: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality impact score (0.0-1.0)",
    )
    description: str = Field(
        default="",
        description="Description of the impact",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional impact metadata",
    )


class RecommendationBenefit(BaseModel):
    """Expected benefit of a recommendation.

    Captures the expected benefit including type, value,
    probability, and description.
    """

    benefit_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique benefit identifier",
    )
    benefit_type: BenefitType = Field(
        default=BenefitType.COST_SAVING,
        description="The type of this benefit",
    )
    description: str = Field(
        default="",
        description="Description of the benefit",
    )
    estimated_value: float = Field(
        default=0.0,
        description="Estimated monetary value of the benefit",
    )
    probability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Probability of realizing this benefit (0.0-1.0)",
    )
    time_horizon: str = Field(
        default="",
        description="Time horizon for realizing this benefit (short, medium, long)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional benefit metadata",
    )


class RecommendationRisk(BaseModel):
    """Expected risk of a recommendation.

    Captures the expected risk including description,
    probability, impact severity, and mitigation strategy.
    """

    risk_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique risk identifier",
    )
    description: str = Field(
        default="",
        description="Description of the risk",
    )
    probability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Probability of the risk occurring (0.0-1.0)",
    )
    impact_severity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Severity of the risk impact (0.0-1.0)",
    )
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Composite risk score (0.0-1.0)",
    )
    mitigation: str = Field(
        default="",
        description="Mitigation strategy for this risk",
    )
    category: str = Field(
        default="",
        description="Category of this risk",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional risk metadata",
    )


class RecommendationPolicy(BaseModel):
    """Policy for recommendation operations.

    Defines policies that govern recommendation generation,
    including allowed domains, strategies, and constraints.
    """

    policy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique policy identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable name for this policy",
    )
    description: str = Field(
        default="",
        description="Description of this policy",
    )
    allowed_domains: list[RecommendationDomain] = Field(
        default_factory=list,
        description="Domains allowed by this policy",
    )
    allowed_strategies: list[RecommendationStrategyEnum] = Field(
        default_factory=list,
        description="Strategies allowed by this policy",
    )
    max_candidates: int = Field(
        default=10,
        ge=1,
        description="Maximum number of candidates allowed",
    )
    min_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold (0.0-1.0)",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this policy is active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional policy metadata",
    )


class RecommendationConfidence(BaseModel):
    """Confidence assessment for a recommendation result.

    Captures confidence across multiple dimensions: strategy,
    impact accuracy, benefit reliability, risk assessment,
    constraint compliance, and overall confidence.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0-1.0)",
    )
    strategy_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in strategy selection (0.0-1.0)",
    )
    impact_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Accuracy of impact estimation (0.0-1.0)",
    )
    benefit_reliability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Reliability of benefit estimates (0.0-1.0)",
    )
    risk_assessment: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality of risk assessment (0.0-1.0)",
    )
    constraint_compliance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in constraint compliance (0.0-1.0)",
    )
    reasoning_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence from reasoning engine (0.0-1.0)",
    )
    business_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Business value score (0.0-1.0)",
    )
    portfolio_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Portfolio quality score (0.0-1.0)",
    )
    policy_compliance: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Policy compliance score (0.0-1.0)",
    )
    feasibility_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Feasibility score (0.0-1.0)",
    )
    outcome_prediction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Outcome prediction confidence (0.0-1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional confidence metadata",
    )


class RecommendationMetadata(BaseModel):
    """Metadata for a recommendation operation.

    Captures descriptive metadata about a recommendation operation
    including title, description, tags, category, and source.
    """

    title: str = Field(
        default="",
        description="Title of the recommendation operation",
    )
    description: str = Field(
        default="",
        description="Description of the recommendation operation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags associated with this recommendation",
    )
    category: str = Field(
        default="",
        description="Category classification for this recommendation",
    )
    source: str = Field(
        default="",
        description="Source identifier for this recommendation",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the recommendation definition",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class RecommendationHealth(BaseModel):
    """Health status of the Recommendation Engine.

    Provides operational health information for monitoring and
    observability of all recommendation pipeline components.
    """

    overall_status: str = Field(
        default="UNKNOWN",
        description="Overall health status (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)",
    )
    recommendation_count: int = Field(
        default=0,
        ge=0,
        description="Total number of recommendation operations",
    )
    coordinator_status: str = Field(
        default="UNKNOWN",
        description="Status of the recommendation coordinator",
    )
    generator_status: str = Field(
        default="UNKNOWN",
        description="Status of the recommendation generator",
    )
    ranker_status: str = Field(
        default="UNKNOWN",
        description="Status of the recommendation ranker",
    )
    validator_status: str = Field(
        default="UNKNOWN",
        description="Status of the recommendation validator",
    )
    policy_engine_status: str = Field(
        default="UNKNOWN",
        description="Status of the recommendation policy engine",
    )
    session_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the session manager",
    )
    confidence_calculator_status: str = Field(
        default="UNKNOWN",
        description="Status of the confidence calculator",
    )
    review_status: str = Field(
        default="UNKNOWN",
        description="Status of the review component",
    )
    version_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the version manager",
    )
    readiness_status: str = Field(
        default="UNKNOWN",
        description="Status of the readiness assessment",
    )
    lineage_status: str = Field(
        default="UNKNOWN",
        description="Status of the lineage tracker",
    )
    snapshot_status: str = Field(
        default="UNKNOWN",
        description="Status of the snapshot manager",
    )
    portfolio_comparator_status: str = Field(
        default="UNKNOWN",
        description="Status of the portfolio comparator",
    )
    hooks_status: str = Field(
        default="UNKNOWN",
        description="Status of the integration hooks",
    )
    quality_status: str = Field(
        default="UNKNOWN",
        description="Status of the quality manager",
    )
    justification_status: str = Field(
        default="UNKNOWN",
        description="Status of the justification component",
    )
    approval_readiness_status: str = Field(
        default="UNKNOWN",
        description="Status of the approval readiness component",
    )
    portfolio_quality_status: str = Field(
        default="UNKNOWN",
        description="Status of the portfolio quality evaluator",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of recommendation pipeline errors",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average pipeline latency in milliseconds",
    )
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Recommendation engine uptime in seconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


class RecommendationMetrics(BaseModel):
    """Aggregated metrics for the Recommendation Engine.

    Tracks operational metrics for monitoring, alerting, and
    capacity planning of the recommendation pipeline.
    """

    recommendation_total: int = Field(
        default=0,
        ge=0,
        description="Total number of recommendation operations",
    )
    candidates_total: int = Field(
        default=0,
        ge=0,
        description="Total number of candidates generated",
    )
    decisions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of decisions produced",
    )
    packages_total: int = Field(
        default=0,
        ge=0,
        description="Total number of packages created",
    )
    validated_total: int = Field(
        default=0,
        ge=0,
        description="Total number of validations performed",
    )
    failed_total: int = Field(
        default=0,
        ge=0,
        description="Total number of failed recommendation operations",
    )
    candidates_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Candidate count per domain",
    )
    candidates_per_strategy: dict[str, int] = Field(
        default_factory=dict,
        description="Candidate count per strategy",
    )
    average_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence across all operations (0.0-1.0)",
    )
    sessions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of recommendation sessions",
    )
    reviews_total: int = Field(
        default=0,
        ge=0,
        description="Total number of reviews performed",
    )
    versions_created: int = Field(
        default=0,
        ge=0,
        description="Total number of versions created",
    )
    snapshots_taken: int = Field(
        default=0,
        ge=0,
        description="Total number of snapshots taken",
    )
    readiness_ready: int = Field(
        default=0,
        ge=0,
        description="Number of readiness-ready assessments",
    )
    readiness_blocked: int = Field(
        default=0,
        ge=0,
        description="Number of readiness-blocked assessments",
    )
    average_business_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average business score across all operations (0.0-1.0)",
    )
    average_feasibility: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average feasibility across all operations (0.0-1.0)",
    )
    quality_total: int = Field(
        default=0,
        ge=0,
        description="Total number of quality assessments performed",
    )
    justifications_total: int = Field(
        default=0,
        ge=0,
        description="Total number of justifications created",
    )
    approval_readiness_ready: int = Field(
        default=0,
        ge=0,
        description="Number of approval-ready assessments",
    )
    approval_readiness_review_required: int = Field(
        default=0,
        ge=0,
        description="Number of approval assessments requiring review",
    )
    approval_readiness_blocked: int = Field(
        default=0,
        ge=0,
        description="Number of approval assessments blocked",
    )
    average_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average quality score across all operations (0.0-1.0)",
    )
    portfolios_quality_total: int = Field(
        default=0,
        ge=0,
        description="Total number of portfolio quality evaluations",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When these metrics were captured",
    )


class RecommendationSession(BaseModel):
    """Operational session for a recommendation operation.

    Tracks the lifecycle of a recommendation operation from
    initialisation through completion or failure.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    request_id: UUID4 = Field(
        description="The request this session belongs to",
    )
    domain: RecommendationDomain = Field(
        default=RecommendationDomain.GENERAL,
        description="The domain for this session",
    )
    reasoning_session: str = Field(
        default="",
        description="Associated reasoning session identifier",
    )
    goal: str = Field(
        default="",
        description="The recommendation goal for this session",
    )
    strategy: str = Field(
        default="",
        description="The recommendation strategy for this session",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Constraints applicable to this session",
    )
    portfolio: dict[str, Any] | None = Field(
        default=None,
        description="Portfolio configuration for this session",
    )
    status: RecommendationStatus = Field(
        default=RecommendationStatus.INITIALIZED,
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


class RecommendationExplainabilityMetadata(BaseModel):
    """Explainability metadata for recommendation decisions.

    Captures why certain recommendations, strategies, candidates,
    policies, and confidence scores were produced during a
    recommendation operation.
    """

    why_candidate_selected: str = Field(
        default="",
        description="Why a candidate was selected",
    )
    why_candidate_rejected: str = Field(
        default="",
        description="Why a candidate was rejected",
    )
    why_strategy_chosen: str = Field(
        default="",
        description="Why a strategy was chosen",
    )
    why_priority_assigned: str = Field(
        default="",
        description="Why a priority was assigned",
    )
    why_policy_applied: str = Field(
        default="",
        description="Why a policy was applied",
    )
    why_confidence_calculated: str = Field(
        default="",
        description="Why confidence was calculated",
    )
    why_generated: str = Field(
        default="",
        description="Why the recommendation was generated",
    )
    why_ranked: str = Field(
        default="",
        description="Why recommendations were ranked this way",
    )
    why_portfolio: str = Field(
        default="",
        description="Why the portfolio was constructed this way",
    )
    why_reviewed: str = Field(
        default="",
        description="Why the recommendation was reviewed",
    )
    why_quality_assessed: str = Field(
        default="",
        description="Why the quality assessment was performed",
    )
    why_approved: str = Field(
        default="",
        description="Why the decision was approved",
    )
    why_rejected_decision: str = Field(
        default="",
        description="Why the decision was rejected",
    )


class RecommendationTrace(BaseModel):
    """Trace record for a recommendation pipeline stage.

    Captures timing, success/failure, and metadata for a single
    stage in the recommendation pipeline for observability.
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
    recommendation_id: str = Field(
        default="",
        description="The recommendation ID being processed",
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
