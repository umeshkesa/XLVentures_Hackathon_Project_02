"""Enumerations for the Explainability Engine.

Defines all enum types used across explainability domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class ExplanationDomain(StrEnum):
    """Domain classification for explanation operations.

    Values:
    - SYSTEM: System-level explanations (logs, metrics, telemetry)
    - ENERGY: Energy-related explanations (consumption, production, storage)
    - OPERATIONS: Operational explanations (processes, workflows, tasks)
    - MAINTENANCE: Maintenance-related explanations (repairs, inspections, schedules)
    - SAFETY: Safety-related explanations (incidents, hazards, compliance)
    - COMPLIANCE: Compliance explanations (regulations, audits, policies)
    - CUSTOMER: Customer-related explanations (feedback, behavior, preferences)
    - HEALTHCARE: Healthcare-related explanations (diagnoses, treatments, outcomes)
    - MANUFACTURING: Manufacturing-related explanations (production, quality, supply)
    """

    SYSTEM = "SYSTEM"
    ENERGY = "ENERGY"
    OPERATIONS = "OPERATIONS"
    MAINTENANCE = "MAINTENANCE"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    CUSTOMER = "CUSTOMER"
    HEALTHCARE = "HEALTHCARE"
    MANUFACTURING = "MANUFACTURING"


class ExplanationLayer(StrEnum):
    """Audience layer for explanation targeting.

    Values:
    - EXECUTIVE: Executive-level explanations (strategic overview, KPIs)
    - MANAGER: Manager-level explanations (operational summaries, trends)
    - ENGINEER: Engineer-level explanations (technical details, root causes)
    - OPERATOR: Operator-level explanations (actionable steps, alerts)
    - TECHNICIAN: Technician-level explanations (repair procedures, diagnostics)
    - AUDITOR: Auditor-level explanations (compliance evidence, policy adherence)
    - DEVELOPER: Developer-level explanations (system internals, API details)
    """

    EXECUTIVE = "EXECUTIVE"
    MANAGER = "MANAGER"
    ENGINEER = "ENGINEER"
    OPERATOR = "OPERATOR"
    TECHNICIAN = "TECHNICIAN"
    AUDITOR = "AUDITOR"
    DEVELOPER = "DEVELOPER"


class ExplanationStatus(StrEnum):
    """Lifecycle status for an explanation operation.

    Values:
    - INITIALIZED: Explanation has been initialized
    - COLLECTING: Collecting evidence and context for the explanation
    - BUILDING: Building narratives and citations
    - VALIDATED: Explanation has been validated
    - COMPLETED: Explanation completed successfully
    - FAILED: Explanation failed
    """

    INITIALIZED = "INITIALIZED"
    COLLECTING = "COLLECTING"
    BUILDING = "BUILDING"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class NarrativeType(StrEnum):
    """Type of narrative for explanation delivery.

    Values:
    - SUMMARY: Concise high-level summary
    - DETAILED: Comprehensive detailed explanation
    - TECHNICAL: Technical deep-dive explanation
    - BUSINESS: Business-oriented explanation
    - AUDIT: Audit-focused explanation with compliance evidence
    """

    SUMMARY = "SUMMARY"
    DETAILED = "DETAILED"
    TECHNICAL = "TECHNICAL"
    BUSINESS = "BUSINESS"
    AUDIT = "AUDIT"


class CitationType(StrEnum):
    """Type of citation source for explanation references.

    Values:
    - EVIDENCE: Citation from evidence data
    - REASONING: Citation from reasoning steps
    - RECOMMENDATION: Citation from recommendation output
    - POLICY: Citation from policy rules
    - METRIC: Citation from metric data
    """

    EVIDENCE = "EVIDENCE"
    REASONING = "REASONING"
    RECOMMENDATION = "RECOMMENDATION"
    POLICY = "POLICY"
    METRIC = "METRIC"
