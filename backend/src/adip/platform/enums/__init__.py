"""Enumerations for the Platform Integration module."""

from __future__ import annotations

from enum import StrEnum


class ModuleName(StrEnum):
    """Names of all ADIP platform modules.

    Used for service registry keys, health checks, and tracing.
    """

    PLANNER = "planner"
    WORKFLOW = "workflow"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    RULES = "rules"
    PLUGINS = "plugins"
    REGISTRY = "registry"
    EVIDENCE = "evidence"
    REASONING = "reasoning"
    RECOMMENDATION = "recommendation"
    EXPLAINABILITY = "explainability"
    DECISION_REVIEW = "decision_review"
    ACTION_MANAGER = "action_manager"
    ACTION_ENGINE = "action_engine"
    ENERGY = "energy"
    API = "api"
    AUTH = "auth"


class PipelineStage(StrEnum):
    """Stages in the platform request pipeline.

    Each stage corresponds to a module in the end-to-end pipeline.
    """

    VALIDATION = "validation"
    PLANNER = "planner"
    WORKFLOW = "workflow"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    RULES = "rules"
    EVIDENCE = "evidence"
    REASONING = "reasoning"
    RECOMMENDATION = "recommendation"
    EXPLAINABILITY = "explainability"
    DECISION_REVIEW = "decision_review"
    ACTION_MANAGER = "action_manager"
    ACTION_ENGINE = "action_engine"
    ENERGY = "energy"
    RESPONSE = "response"


class PipelineStatus(StrEnum):
    """Status of a pipeline execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ModuleHealthStatus(StrEnum):
    """Health status of a single module."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
