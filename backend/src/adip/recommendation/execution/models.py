"""Execution-layer models for the Recommendation Engine Phase 2.

Internal models used by execution components during recommendation
pipeline processing. Not part of the public API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.recommendation.enums import (
    FeasibilityStatus,
    ImplementationTimeline,
)


class RecommendationScore(BaseModel):
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique score identifier")
    business_value: float = Field(default=0.0, ge=0.0, le=1.0, description="Business value score (0.0–1.0)")
    feasibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Feasibility score (0.0–1.0)")
    impact: float = Field(default=0.0, ge=0.0, le=1.0, description="Impact score (0.0–1.0)")
    risk_adjustment: float = Field(default=0.0, ge=0.0, le=1.0, description="Risk adjustment factor (0.0–1.0, lower = more risky)")
    policy_compliance: float = Field(default=1.0, ge=0.0, le=1.0, description="Policy compliance score (0.0–1.0)")
    overall: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall recommendation score (0.0–1.0)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the score was calculated")


class FeasibilityAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis identifier")
    status: FeasibilityStatus = Field(default=FeasibilityStatus.UNKNOWN, description="Overall feasibility status")
    resources_available: bool = Field(default=False, description="Whether required resources are available")
    budget_available: bool = Field(default=False, description="Whether required budget is available")
    inventory_available: bool = Field(default=False, description="Whether required inventory is available")
    technician_available: bool = Field(default=False, description="Whether technician is available")
    time_window_available: bool = Field(default=False, description="Whether time window is available")
    operational_feasible: bool = Field(default=False, description="Whether operationally feasible")
    feasibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall feasibility score (0.0–1.0)")
    constraints: list[str] = Field(default_factory=list, description="Identified constraints")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed feasibility breakdown")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the analysis was performed")


class CostEstimate(BaseModel):
    estimate_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique estimate identifier")
    implementation_cost: float = Field(default=0.0, ge=0.0, description="Estimated implementation cost")
    operational_cost: float = Field(default=0.0, ge=0.0, description="Estimated operational cost")
    downtime_cost: float = Field(default=0.0, ge=0.0, description="Estimated downtime cost")
    total_cost: float = Field(default=0.0, ge=0.0, description="Total estimated cost")
    roi: float = Field(default=0.0, description="Estimated return on investment")
    currency: str = Field(default="USD", description="Currency for cost estimates")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed cost breakdown")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the estimate was made")


class DependencyNode(BaseModel):
    node_id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique node identifier")
    recommendation_id: str = Field(default="", description="The recommendation this node represents")
    description: str = Field(default="", description="Description of this dependency node")
    blocking_dependencies: list[str] = Field(default_factory=list, description="IDs of recommendations that block this one")
    optional_dependencies: list[str] = Field(default_factory=list, description="IDs of optional dependencies")
    depends_on: list[str] = Field(default_factory=list, description="IDs this node depends on")
    is_blocked: bool = Field(default=False, description="Whether this node is blocked by its dependencies")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional node metadata")


class DependencyGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique graph identifier")
    nodes: list[DependencyNode] = Field(default_factory=list, description="Nodes in the dependency graph")
    execution_order: list[str] = Field(default_factory=list, description="Recommended execution order (topological)")
    has_cycles: bool = Field(default=False, description="Whether the graph contains cycles")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional graph metadata")


class ImplementationStep(BaseModel):
    step_id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique step identifier")
    order: int = Field(default=0, ge=0, description="Step order in the implementation sequence")
    description: str = Field(default="", description="Description of this implementation step")
    required_resources: list[str] = Field(default_factory=list, description="Resources required for this step")
    estimated_duration: str = Field(default="", description="Estimated duration for this step")
    success_criteria: list[str] = Field(default_factory=list, description="Criteria to determine step success")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional step metadata")


class ImplementationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique plan identifier")
    recommendation_id: str = Field(default="", description="The recommendation this plan belongs to")
    steps: list[ImplementationStep] = Field(default_factory=list, description="Ordered implementation steps")
    total_duration: str = Field(default="", description="Total estimated duration for the plan")
    required_resources: list[str] = Field(default_factory=list, description="All resources required across all steps")
    success_criteria: list[str] = Field(default_factory=list, description="Overall success criteria for the plan")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional plan metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the plan was created")


class TimelineEstimate(BaseModel):
    estimate_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique estimate identifier")
    timeline: ImplementationTimeline = Field(default=ImplementationTimeline.PLANNED_FUTURE, description="Recommended implementation timeline")
    description: str = Field(default="", description="Description of this timeline estimate")
    estimated_hours: float = Field(default=0.0, ge=0.0, description="Estimated hours to implement")
    urgency_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Urgency score (0.0–1.0, higher = more urgent)")
    factors: list[str] = Field(default_factory=list, description="Factors influencing the timeline")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional timeline metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the estimate was created")


class TradeoffAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis identifier")
    primary_id: str = Field(default="", description="The primary recommendation ID")
    alternative_id: str = Field(default="", description="The alternative recommendation ID")
    cost_difference: float = Field(default=0.0, description="Cost difference between primary and alternative")
    risk_difference: float = Field(default=0.0, ge=-1.0, le=1.0, description="Risk difference (negative = primary less risky)")
    downtime_difference: float = Field(default=0.0, description="Downtime difference between options")
    energy_difference: float = Field(default=0.0, description="Energy difference between options")
    safety_difference: float = Field(default=0.0, ge=-1.0, le=1.0, description="Safety difference (negative = primary safer)")
    sla_difference: float = Field(default=0.0, ge=-1.0, le=1.0, description="SLA difference (negative = primary better for SLA)")
    overall_recommendation: str = Field(default="", description="Which option is recommended overall (primary/alternative)")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed trade-off breakdown")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the analysis was performed")


class PolicyEvalResult(BaseModel):
    eval_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique evaluation identifier")
    safety_passed: bool = Field(default=True, description="Whether safety policies passed")
    compliance_passed: bool = Field(default=True, description="Whether compliance policies passed")
    business_passed: bool = Field(default=True, description="Whether business policies passed")
    operational_passed: bool = Field(default=True, description="Whether operational policies passed")
    overall_passed: bool = Field(default=True, description="Whether all policies passed")
    violations: list[str] = Field(default_factory=list, description="Policy violations found")
    warnings: list[str] = Field(default_factory=list, description="Policy warnings")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed policy evaluation results")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the evaluation was performed")


class OutcomePrediction(BaseModel):
    prediction_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique prediction identifier")
    candidate_id: str = Field(default="", description="The recommendation candidate this prediction applies to")
    success_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Probability of success (0.0–1.0)")
    cost_savings: float = Field(default=0.0, description="Estimated cost savings")
    downtime_reduction: float = Field(default=0.0, description="Estimated downtime reduction in hours")
    energy_savings: float = Field(default=0.0, description="Estimated energy savings")
    risk_reduction: float = Field(default=0.0, ge=0.0, le=1.0, description="Estimated risk reduction (0.0–1.0)")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed outcome prediction")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the prediction was made")


class RecommendationPortfolio(BaseModel):
    portfolio_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique portfolio identifier")
    primary_recommendation_id: str = Field(default="", description="The primary recommendation ID")
    alternative_ids: list[str] = Field(default_factory=list, description="IDs of alternative recommendations")
    tradeoffs: list[TradeoffAnalysis] = Field(default_factory=list, description="Trade-off analyses between options")
    dependencies: DependencyGraph | None = Field(default=None, description="Dependency graph for the portfolio")
    expected_outcomes: list[OutcomePrediction] = Field(default_factory=list, description="Expected outcomes for each option")
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence in the portfolio")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional portfolio metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the portfolio was created")


class TraceRecord(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique trace record identifier")
    stage_name: str = Field(default="", description="Name of the pipeline stage")
    operation: str = Field(default="", description="The operation being traced")
    recommendation_id: str = Field(default="", description="The recommendation ID associated with this trace")
    correlation_id: str = Field(default="", description="Correlation ID for distributed tracing")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the stage started")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the stage completed")
    duration_ms: float | None = Field(default=None, ge=0.0, description="Stage duration in milliseconds")
    success: bool = Field(default=True, description="Whether the stage completed successfully")
    warnings: list[str] = Field(default_factory=list, description="Warnings generated during this stage")
    errors: list[str] = Field(default_factory=list, description="Errors generated during this stage")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")


class RecommendationMetrics(BaseModel):
    metrics_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique metrics identifier")
    candidates_generated: int = Field(default=0, ge=0, description="Total candidates generated")
    rankings_performed: int = Field(default=0, ge=0, description="Total ranking operations performed")
    scores_calculated: int = Field(default=0, ge=0, description="Total scores calculated")
    policy_violations: int = Field(default=0, ge=0, description="Total policy violations detected")
    average_feasibility: float = Field(default=0.0, ge=0.0, le=1.0, description="Average feasibility score")
    average_cost: float = Field(default=0.0, ge=0.0, description="Average estimated cost")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Average confidence score")
    portfolios_created: int = Field(default=0, ge=0, description="Total portfolios created")
    quality_assessments: int = Field(default=0, ge=0, description="Total quality assessments performed")
    justifications_created: int = Field(default=0, ge=0, description="Total justifications created")
    approval_readiness_ready: int = Field(default=0, ge=0, description="Total approval-ready assessments")
    approval_readiness_review_required: int = Field(default=0, ge=0, description="Total approval assessments requiring review")
    approval_readiness_blocked: int = Field(default=0, ge=0, description="Total approval assessments blocked")
    average_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Average quality score")
    portfolio_quality_assessments: int = Field(default=0, ge=0, description="Total portfolio quality assessments")
    trace_count: int = Field(default=0, ge=0, description="Total trace records")
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When metrics were collected")
