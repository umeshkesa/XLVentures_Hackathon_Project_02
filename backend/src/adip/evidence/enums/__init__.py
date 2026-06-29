"""Enumerations for the Evidence Fusion Engine.

Defines all enum types used across evidence domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class EvidenceDomain(StrEnum):
    """Domain classification for evidence.

    Values:
    - SYSTEM: System-level evidence (logs, metrics, telemetry)
    - ENERGY: Energy-related evidence (consumption, production, storage)
    - OPERATIONS: Operational evidence (processes, workflows, tasks)
    - MAINTENANCE: Maintenance-related evidence (repairs, inspections, schedules)
    - SAFETY: Safety-related evidence (incidents, hazards, compliance)
    - CUSTOMER: Customer-related evidence (feedback, behavior, preferences)
    - COMPLIANCE: Compliance evidence (regulations, audits, policies)
    - SECURITY: Security-related evidence (threats, vulnerabilities, access)
    - WORKFLOW: Workflow-related evidence (executions, states, transitions)
    - PLANNING: Planning-related evidence (schedules, forecasts, resources)
    """

    SYSTEM = "SYSTEM"
    ENERGY = "ENERGY"
    OPERATIONS = "OPERATIONS"
    MAINTENANCE = "MAINTENANCE"
    SAFETY = "SAFETY"
    CUSTOMER = "CUSTOMER"
    COMPLIANCE = "COMPLIANCE"
    SECURITY = "SECURITY"
    WORKFLOW = "WORKFLOW"
    PLANNING = "PLANNING"


class EvidenceType(StrEnum):
    """Type classification for evidence sources.

    Values:
    - KNOWLEDGE: Evidence retrieved from the Knowledge Manager
    - MEMORY: Evidence retrieved from the Memory Manager
    - RULE: Evidence derived from the Rule Manager
    - WORKFLOW: Evidence from workflow executions
    - PLANNER: Evidence from the Planner
    - SENSOR: Evidence from IoT sensors and telemetry
    - INCIDENT: Evidence from incident reports
    - MAINTENANCE: Evidence from maintenance logs
    - CUSTOMER: Evidence from customer interactions
    - CRM: Evidence from CRM systems
    - EMAIL: Evidence from email communications
    - REPORT: Evidence from generated reports
    """

    KNOWLEDGE = "KNOWLEDGE"
    MEMORY = "MEMORY"
    RULE = "RULE"
    WORKFLOW = "WORKFLOW"
    PLANNER = "PLANNER"
    SENSOR = "SENSOR"
    INCIDENT = "INCIDENT"
    MAINTENANCE = "MAINTENANCE"
    CUSTOMER = "CUSTOMER"
    CRM = "CRM"
    EMAIL = "EMAIL"
    REPORT = "REPORT"


class EvidenceStatus(StrEnum):
    """Lifecycle status for evidence processing.

    Values:
    - COLLECTED: Evidence has been collected from its source
    - VALIDATED: Evidence has passed validation checks
    - NORMALIZED: Evidence has been normalized to a standard format
    - CORRELATED: Evidence has been correlated with other evidence
    - FUSED: Evidence has been fused into a unified representation
    - READY: Evidence is ready for consumption by the Reasoning Engine
    """

    COLLECTED = "COLLECTED"
    VALIDATED = "VALIDATED"
    NORMALIZED = "NORMALIZED"
    CORRELATED = "CORRELATED"
    FUSED = "FUSED"
    READY = "READY"


class EvidenceClassification(StrEnum):
    """Classification of evidence based on its role in analysis.

    Values:
    - PRIMARY: Primary evidence that directly supports a conclusion
    - SECONDARY: Secondary evidence that provides additional context
    - SUPPORTING: Supporting evidence that reinforces other evidence
    - CONTRADICTORY: Evidence that contradicts other evidence
    - HISTORICAL: Historical evidence from past events
    - REAL_TIME: Real-time evidence collected now
    - PREDICTIVE: Predictive evidence about future events
    - DERIVED: Evidence derived from analysis of other evidence
    """

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    SUPPORTING = "SUPPORTING"
    CONTRADICTORY = "CONTRADICTORY"
    HISTORICAL = "HISTORICAL"
    REAL_TIME = "REAL_TIME"
    PREDICTIVE = "PREDICTIVE"
    DERIVED = "DERIVED"


class EvidencePriority(StrEnum):
    """Priority level for evidence.

    Values:
    - CRITICAL: Critical evidence requiring immediate attention
    - HIGH: High priority evidence
    - MEDIUM: Medium priority evidence
    - LOW: Low priority evidence
    - INFORMATIONAL: Informational evidence, no action required
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class RelationshipType(StrEnum):
    """Type of relationship between evidence nodes.

    Values:
    - SUPPORTS: Evidence supports another piece of evidence
    - CONTRADICTS: Evidence contradicts another piece of evidence
    - CAUSES: Evidence is caused by another piece of evidence
    - DEPENDS_ON: Evidence depends on another piece of evidence
    - DERIVED_FROM: Evidence is derived from another piece of evidence
    - REFERENCES: Evidence references another piece of evidence
    - TEMPORALLY_FOLLOWS: Evidence temporally follows another piece of evidence
    """

    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CAUSES = "CAUSES"
    DEPENDS_ON = "DEPENDS_ON"
    DERIVED_FROM = "DERIVED_FROM"
    REFERENCES = "REFERENCES"
    TEMPORALLY_FOLLOWS = "TEMPORALLY_FOLLOWS"


class ConsensusLevel(StrEnum):
    """Consensus level for evidence fusion.

    Values:
    - HIGH: Strong agreement with minimal conflicts
    - MEDIUM: Moderate agreement with some conflicts
    - LOW: Weak agreement with significant conflicts
    """

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FusionPolicyType(StrEnum):
    """Fusion policy for evidence processing.

    Values:
    - STRICT: Strict fusion — requires high confidence and consensus
    - BALANCED: Balanced fusion — moderate thresholds
    - PERMISSIVE: Permissive fusion — accepts lower confidence
    - EMERGENCY: Emergency fusion — bypasses normal checks
    """

    STRICT = "STRICT"
    BALANCED = "BALANCED"
    PERMISSIVE = "PERMISSIVE"
    EMERGENCY = "EMERGENCY"


class BundleType(StrEnum):
    """Type of evidence bundle grouping.

    Values:
    - ASSET: Evidence grouped by asset
    - INCIDENT: Evidence grouped by incident
    - CUSTOMER: Evidence grouped by customer
    - FACILITY: Evidence grouped by facility
    - WORKFLOW: Evidence grouped by workflow
    - INVESTIGATION: Evidence grouped by investigation
    """

    ASSET = "ASSET"
    INCIDENT = "INCIDENT"
    CUSTOMER = "CUSTOMER"
    FACILITY = "FACILITY"
    WORKFLOW = "WORKFLOW"
    INVESTIGATION = "INVESTIGATION"
