"""Enumerations for the Recommendation Engine.

Defines all enum types used across recommendation domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class RecommendationStrategy(StrEnum):
    """Strategy type for generating recommendations.

    Values:
    - NEXT_BEST_ACTION: Next best action strategy
    - RISK_MITIGATION: Risk mitigation strategy
    - PREVENTIVE_MAINTENANCE: Preventive maintenance strategy
    - COST_OPTIMIZATION: Cost optimization strategy
    - ENERGY_OPTIMIZATION: Energy optimization strategy
    - SLA_RECOVERY: SLA recovery strategy
    - HYBRID_RECOMMENDATION: Hybrid recommendation strategy
    """

    NEXT_BEST_ACTION = "NEXT_BEST_ACTION"
    RISK_MITIGATION = "RISK_MITIGATION"
    PREVENTIVE_MAINTENANCE = "PREVENTIVE_MAINTENANCE"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"
    ENERGY_OPTIMIZATION = "ENERGY_OPTIMIZATION"
    SLA_RECOVERY = "SLA_RECOVERY"
    HYBRID_RECOMMENDATION = "HYBRID_RECOMMENDATION"


class RecommendationGoal(StrEnum):
    """Goal type for a recommendation.

    Values:
    - REDUCE_DOWNTIME: Reduce downtime goal
    - REDUCE_COST: Reduce cost goal
    - INCREASE_SAFETY: Increase safety goal
    - REDUCE_ENERGY_CONSUMPTION: Reduce energy consumption goal
    - MEET_SLA: Meet SLA goal
    - IMPROVE_CUSTOMER_SATISFACTION: Improve customer satisfaction goal
    - INCREASE_ASSET_RELIABILITY: Increase asset reliability goal
    """

    REDUCE_DOWNTIME = "REDUCE_DOWNTIME"
    REDUCE_COST = "REDUCE_COST"
    INCREASE_SAFETY = "INCREASE_SAFETY"
    REDUCE_ENERGY_CONSUMPTION = "REDUCE_ENERGY_CONSUMPTION"
    MEET_SLA = "MEET_SLA"
    IMPROVE_CUSTOMER_SATISFACTION = "IMPROVE_CUSTOMER_SATISFACTION"
    INCREASE_ASSET_RELIABILITY = "INCREASE_ASSET_RELIABILITY"


class RecommendationStatus(StrEnum):
    """Lifecycle status for a recommendation operation.

    Values:
    - INITIALIZED: Recommendation has been initialized
    - GENERATED: Recommendations have been generated
    - RANKED: Recommendations have been ranked
    - VALIDATED: Recommendations have been validated
    - APPROVED: Recommendations have been approved
    - COMPLETED: Recommendation completed successfully
    - FAILED: Recommendation failed
    """

    INITIALIZED = "INITIALIZED"
    GENERATED = "GENERATED"
    RANKED = "RANKED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RecommendationDomain(StrEnum):
    """Domain classification for recommendation operations.

    Values:
    - SYSTEM: System-level recommendations (logs, metrics, telemetry)
    - ENERGY: Energy-related recommendations (consumption, production, storage)
    - MAINTENANCE: Maintenance-related recommendations (repairs, inspections, schedules)
    - OPERATIONS: Operational recommendations (processes, workflows, tasks)
    - CUSTOMER: Customer-related recommendations (feedback, behavior, preferences)
    - SAFETY: Safety-related recommendations (incidents, hazards, compliance)
    - COMPLIANCE: Compliance recommendations (regulations, audits, policies)
    - WORKFLOW: Workflow-related recommendations (executions, states, transitions)
    - PLANNING: Planning-related recommendations (schedules, forecasts, resources)
    - GENERAL: General domain recommendations
    """

    SYSTEM = "SYSTEM"
    ENERGY = "ENERGY"
    MAINTENANCE = "MAINTENANCE"
    OPERATIONS = "OPERATIONS"
    CUSTOMER = "CUSTOMER"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    WORKFLOW = "WORKFLOW"
    PLANNING = "PLANNING"
    GENERAL = "GENERAL"


class RecommendationPriority(StrEnum):
    """Priority level for a recommendation.

    Values:
    - CRITICAL: Critical priority
    - HIGH: High priority
    - MEDIUM: Medium priority
    - LOW: Low priority
    - OPTIONAL: Optional priority
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    OPTIONAL = "OPTIONAL"


class ConstraintType(StrEnum):
    """Type of constraint for recommendations.

    Values:
    - HARD: Hard constraint (must be satisfied)
    - SOFT: Soft constraint (should be satisfied)
    - BUDGET: Budget constraint
    - TIME: Time constraint
    """

    HARD = "HARD"
    SOFT = "SOFT"
    BUDGET = "BUDGET"
    TIME = "TIME"


class BenefitType(StrEnum):
    """Type of benefit associated with a recommendation.

    Values:
    - COST_SAVING: Cost saving benefit
    - EFFICIENCY_GAIN: Efficiency gain benefit
    - SAFETY_IMPROVEMENT: Safety improvement benefit
    - RISK_REDUCTION: Risk reduction benefit
    - RELIABILITY_IMPROVEMENT: Reliability improvement benefit
    """

    COST_SAVING = "COST_SAVING"
    EFFICIENCY_GAIN = "EFFICIENCY_GAIN"
    SAFETY_IMPROVEMENT = "SAFETY_IMPROVEMENT"
    RISK_REDUCTION = "RISK_REDUCTION"
    RELIABILITY_IMPROVEMENT = "RELIABILITY_IMPROVEMENT"


class ImplementationTimeline(StrEnum):
    """Timeframe for implementing a recommendation.

    Values:
    - IMMEDIATE: Implement immediately (within minutes)
    - TODAY: Implement today (within hours)
    - WITHIN_24_HOURS: Implement within 24 hours
    - MAINTENANCE_WINDOW: Implement during next maintenance window
    - PLANNED_FUTURE: Implement as part of planned future work
    """
    IMMEDIATE = "IMMEDIATE"
    TODAY = "TODAY"
    WITHIN_24_HOURS = "WITHIN_24_HOURS"
    MAINTENANCE_WINDOW = "MAINTENANCE_WINDOW"
    PLANNED_FUTURE = "PLANNED_FUTURE"


class FeasibilityStatus(StrEnum):
    """Feasibility status for a recommendation.

    Values:
    - FEASIBLE: Recommendation is feasible
    - PARTIALLY_FEASIBLE: Recommendation is partially feasible
    - NOT_FEASIBLE: Recommendation is not feasible
    - UNKNOWN: Feasibility cannot be determined
    """
    FEASIBLE = "FEASIBLE"
    PARTIALLY_FEASIBLE = "PARTIALLY_FEASIBLE"
    NOT_FEASIBLE = "NOT_FEASIBLE"
    UNKNOWN = "UNKNOWN"


class TradeoffDimension(StrEnum):
    """Dimension for trade-off analysis.

    Values:
    - COST: Cost dimension
    - RISK: Risk dimension
    - DOWNTIME: Downtime dimension
    - ENERGY: Energy consumption dimension
    - SAFETY: Safety dimension
    - SLA: SLA compliance dimension
    - TIME: Time dimension
    - QUALITY: Quality dimension
    """
    COST = "COST"
    RISK = "RISK"
    DOWNTIME = "DOWNTIME"
    ENERGY = "ENERGY"
    SAFETY = "SAFETY"
    SLA = "SLA"
    TIME = "TIME"
    QUALITY = "QUALITY"


class FeasibilityLevel(StrEnum):
    """Level of feasibility assessment.

    Values:
    - HIGH: High feasibility
    - MEDIUM: Medium feasibility
    - LOW: Low feasibility
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendationTraceStage(StrEnum):
    """Stages in the recommendation pipeline for tracing."""
    STRATEGY = "STRATEGY"
    GENERATION = "GENERATION"
    RANKING = "RANKING"
    SCORING = "SCORING"
    FEASIBILITY = "FEASIBILITY"
    COST = "COST"
    DEPENDENCY = "DEPENDENCY"
    PLAN = "PLAN"
    TIMELINE = "TIMELINE"
    TRADEOFF = "TRADEOFF"
    POLICY = "POLICY"
    OUTCOME = "OUTCOME"
    PORTFOLIO = "PORTFOLIO"
    VALIDATION = "VALIDATION"
    REVIEW = "REVIEW"
    CONFIDENCE = "CONFIDENCE"
    VERSION = "VERSION"
    READINESS = "READINESS"
    LINEAGE = "LINEAGE"
    SNAPSHOT = "SNAPSHOT"
    COMPLETED = "COMPLETED"
    QUALITY = "QUALITY"
    JUSTIFICATION = "JUSTIFICATION"
    APPROVAL_READINESS = "APPROVAL_READINESS"
    PORTFOLIO_QUALITY = "PORTFOLIO_QUALITY"


class RecommendationReadinessStatus(StrEnum):
    """Readiness status for a recommendation decision.

    Values:
    - READY: Recommendation is ready for deployment
    - REQUIRES_REVIEW: Recommendation needs further review
    - BLOCKED: Recommendation is blocked by unresolved issues
    """
    READY = "READY"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    BLOCKED = "BLOCKED"
