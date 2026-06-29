"""Enumerations for the Reasoning Engine.

Defines all enum types used across reasoning domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class ReasoningDomain(StrEnum):
    """Domain classification for reasoning operations.

    Values:
    - SYSTEM: System-level reasoning (logs, metrics, telemetry)
    - ENERGY: Energy-related reasoning (consumption, production, storage)
    - MAINTENANCE: Maintenance-related reasoning (repairs, inspections, schedules)
    - OPERATIONS: Operational reasoning (processes, workflows, tasks)
    - CUSTOMER: Customer-related reasoning (feedback, behavior, preferences)
    - SAFETY: Safety-related reasoning (incidents, hazards, compliance)
    - COMPLIANCE: Compliance reasoning (regulations, audits, policies)
    - WORKFLOW: Workflow-related reasoning (executions, states, transitions)
    - PLANNING: Planning-related reasoning (schedules, forecasts, resources)
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


class ReasoningStatus(StrEnum):
    """Lifecycle status for a reasoning operation.

    Values:
    - INITIALIZED: Reasoning has been initialised with a request
    - ANALYZING: Evidence is being analysed
    - GENERATING_HYPOTHESES: Hypotheses are being generated
    - EVALUATING: Hypotheses and inferences are being evaluated
    - VALIDATED: Reasoning results have been validated
    - COMPLETED: Reasoning operation completed successfully
    - FAILED: Reasoning operation failed
    """

    INITIALIZED = "INITIALIZED"
    ANALYZING = "ANALYZING"
    GENERATING_HYPOTHESES = "GENERATING_HYPOTHESES"
    EVALUATING = "EVALUATING"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReasoningStrategyType(StrEnum):
    """Type of reasoning strategy to apply.

    Values:
    - RULE_BASED: Rule-based reasoning using defined rules
    - EVIDENCE_BASED: Evidence-driven reasoning from fused evidence
    - HYPOTHESIS: Hypothesis-driven reasoning with generate-and-test
    - CONSTRAINT: Constraint-based reasoning with satisfaction checks
    - MULTI_STEP: Multi-step reasoning with intermediate conclusions
    - HYBRID: Hybrid reasoning combining multiple strategies
    """

    RULE_BASED = "RULE_BASED"
    EVIDENCE_BASED = "EVIDENCE_BASED"
    HYPOTHESIS = "HYPOTHESIS"
    CONSTRAINT = "CONSTRAINT"
    MULTI_STEP = "MULTI_STEP"
    HYBRID = "HYBRID"


class HypothesisStatus(StrEnum):
    """Status of a hypothesis during reasoning.

    Values:
    - PROPOSED: Hypothesis has been proposed
    - SUPPORTED: Hypothesis has supporting evidence
    - CONTRADICTED: Hypothesis has contradicting evidence
    - VALIDATED: Hypothesis has been validated
    - REJECTED: Hypothesis has been rejected
    """

    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


class ContradictionSeverity(StrEnum):
    """Severity level for contradictions.

    Values:
    - LOW: Low severity contradiction
    - MEDIUM: Medium severity contradiction
    - HIGH: High severity contradiction
    - CRITICAL: Critical contradiction requiring resolution
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContradictionResolutionStatus(StrEnum):
    """Resolution status for contradictions.

    Values:
    - UNRESOLVED: Contradiction has not been resolved
    - INVESTIGATING: Contradiction is being investigated
    - RESOLVED: Contradiction has been resolved
    - DISMISSED: Contradiction has been dismissed
    """

    UNRESOLVED = "UNRESOLVED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ReasoningGoalType(StrEnum):
    """Type of reasoning goal.

    Values:
    - ROOT_CAUSE_ANALYSIS: Identify root causes of issues
    - NEXT_BEST_ACTION: Determine the next best action to take
    - RISK_ASSESSMENT: Assess risks of decisions or scenarios
    - MAINTENANCE_PLANNING: Plan maintenance activities
    - ENERGY_OPTIMIZATION: Optimise energy consumption and production
    - COMPLIANCE_VERIFICATION: Verify compliance with policies and regulations
    - ANOMALY_INVESTIGATION: Investigate anomalies in data or processes
    """

    ROOT_CAUSE_ANALYSIS = "ROOT_CAUSE_ANALYSIS"
    NEXT_BEST_ACTION = "NEXT_BEST_ACTION"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    MAINTENANCE_PLANNING = "MAINTENANCE_PLANNING"
    ENERGY_OPTIMIZATION = "ENERGY_OPTIMIZATION"
    COMPLIANCE_VERIFICATION = "COMPLIANCE_VERIFICATION"
    ANOMALY_INVESTIGATION = "ANOMALY_INVESTIGATION"


class ConstraintType(StrEnum):
    """Type of constraint for reasoning.

    Values:
    - BUDGET: Budget constraints
    - TIME: Time constraints
    - SAFETY: Safety constraints
    - COMPLIANCE: Compliance constraints
    - SLA: Service Level Agreement constraints
    - RESOURCES: Resource constraints
    - BUSINESS_POLICIES: Business policy constraints
    """

    BUDGET = "BUDGET"
    TIME = "TIME"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    SLA = "SLA"
    RESOURCES = "RESOURCES"
    BUSINESS_POLICIES = "BUSINESS_POLICIES"


class AssumptionStatus(StrEnum):
    """Status of an assumption during reasoning.

    Values:
    - ACTIVE: Assumption is active and being tracked
    - VALIDATED: Assumption has been validated
    - INVALIDATED: Assumption has been invalidated
    - SUSPENDED: Assumption has been suspended
    """

    ACTIVE = "ACTIVE"
    VALIDATED = "VALIDATED"
    INVALIDATED = "INVALIDATED"
    SUSPENDED = "SUSPENDED"


class AlternativeStatus(StrEnum):
    """Status of a decision alternative.

    Values:
    - CANDIDATE: Alternative is a candidate for selection
    - EVALUATED: Alternative has been evaluated
    - SELECTED: Alternative has been selected
    - REJECTED: Alternative has been rejected
    """

    CANDIDATE = "CANDIDATE"
    EVALUATED = "EVALUATED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class PolicyType(StrEnum):
    """Policy type for reasoning decisions.

    Values:
    - STRICT: Strict policy enforcement
    - BALANCED: Balanced policy enforcement
    - CONSERVATIVE: Conservative policy enforcement
    - AGGRESSIVE: Aggressive policy enforcement
    - EMERGENCY: Emergency policy — bypasses normal checks
    """

    STRICT = "STRICT"
    BALANCED = "BALANCED"
    CONSERVATIVE = "CONSERVATIVE"
    AGGRESSIVE = "AGGRESSIVE"
    EMERGENCY = "EMERGENCY"


class DecisionReadinessStatus(StrEnum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MORE_INFORMATION_REQUIRED = "MORE_INFORMATION_REQUIRED"


class TraceStage(StrEnum):
    """Stage names for reasoning pipeline tracing.

    Values:
    - CONTEXT: Context building stage
    - GOAL: Goal selection stage
    - CONSTRAINT: Constraint evaluation stage
    - ASSUMPTION: Assumption tracking stage
    - STRATEGY: Strategy selection stage
    - HYPOTHESIS: Hypothesis generation stage
    - INFERENCE: Inference stage
    - CONTRADICTION: Contradiction detection stage
    - GRAPH: Graph building stage
    - ALTERNATIVE: Alternative evaluation stage
    - WEIGHT: Weight assignment stage
    - SCORE: Scoring stage
    - POLICY: Policy checking stage
    - DECISION: Decision stage
    - VALIDATION: Validation stage
    - CONFIDENCE: Confidence calculation stage
    - COMPLETED: Pipeline completed stage
    """

    CONTEXT = "CONTEXT"
    GOAL = "GOAL"
    CONSTRAINT = "CONSTRAINT"
    ASSUMPTION = "ASSUMPTION"
    STRATEGY = "STRATEGY"
    HYPOTHESIS = "HYPOTHESIS"
    INFERENCE = "INFERENCE"
    CONTRADICTION = "CONTRADICTION"
    GRAPH = "GRAPH"
    ALTERNATIVE = "ALTERNATIVE"
    WEIGHT = "WEIGHT"
    SCORE = "SCORE"
    POLICY = "POLICY"
    DECISION = "DECISION"
    VALIDATION = "VALIDATION"
    CONFIDENCE = "CONFIDENCE"
    COMPLETED = "COMPLETED"
    REVIEW = "REVIEW"
    RANKING = "RANKING"
    READINESS = "READINESS"
