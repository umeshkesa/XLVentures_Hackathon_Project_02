"""Enumerations for the Rule Manager.

Defines all enum types used across rule domain models, events,
interfaces, and DTOs.
"""

from __future__ import annotations

from enum import StrEnum


class RuleDomain(StrEnum):
    """Enterprise rule domains.

    Values represent the ADIP platform domains that rules can
    be defined for. Each domain corresponds to an ADIP component
    or business capability.
    """

    SYSTEM = "SYSTEM"
    PLANNER = "PLANNER"
    WORKFLOW = "WORKFLOW"
    MEMORY = "MEMORY"
    KNOWLEDGE = "KNOWLEDGE"
    REASONING = "REASONING"
    EVIDENCE = "EVIDENCE"
    ACTION = "ACTION"
    ENERGY = "ENERGY"
    CUSTOMER = "CUSTOMER"
    PLUGIN = "PLUGIN"


class RuleType(StrEnum):
    """Supported rule types for the enterprise policy platform.

    Business — core business logic and decision rules.
    Safety — safety constraints and guardrails.
    Compliance — regulatory and policy compliance rules.
    Maintenance — system maintenance and operational rules.
    Approval — approval workflow rules.
    Energy — energy management and optimisation rules.
    Customer — customer-facing business rules.
    Security — security policy and access control rules.
    Workflow — workflow orchestration and routing rules.
    Planning — planning and scheduling rules.
    """

    BUSINESS = "BUSINESS"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    MAINTENANCE = "MAINTENANCE"
    APPROVAL = "APPROVAL"
    ENERGY = "ENERGY"
    CUSTOMER = "CUSTOMER"
    SECURITY = "SECURITY"
    WORKFLOW = "WORKFLOW"
    PLANNING = "PLANNING"


class RuleLifecycleStatus(StrEnum):
    """Lifecycle status of a rule.

    DRAFT — initial creation, not yet reviewed.
    UNDER_REVIEW — submitted for review.
    APPROVED — reviewed and approved.
    ACTIVE — active and enforcing decisions.
    DEPRECATED — superseded by a newer rule version.
    ARCHIVED — no longer active but retained for audit.
    """

    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class EvaluationStrategyType(StrEnum):
    """Supported rule evaluation strategies.

    SEQUENTIAL — evaluate rules in order; stop at first match.
    PRIORITY — evaluate rules by priority; highest priority wins.
    CONDITIONAL — evaluate rules based on condition evaluation.
    COMPOSITE — combine multiple strategies for complex evaluation.
    PARALLEL — evaluate rules concurrently (future).
    """

    SEQUENTIAL = "SEQUENTIAL"
    PRIORITY = "PRIORITY"
    CONDITIONAL = "CONDITIONAL"
    COMPOSITE = "COMPOSITE"
    PARALLEL = "PARALLEL"
