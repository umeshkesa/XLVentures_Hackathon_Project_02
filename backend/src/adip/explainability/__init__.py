"""Explainability Engine — Explanation Layer component.

The Explainability Engine consumes outputs from the Evidence Fusion,
Reasoning, and Recommendation engines and produces structured,
multi-audience explanations without performing reasoning itself.
"""

from __future__ import annotations

# Events
from adip.explainability.contracts.events import (
    ExplanationCompleted,
    ExplanationEvent,
    ExplanationGenerated,
    ExplanationRequested,
    ExplanationValidated,
)

# Exceptions
from adip.explainability.contracts.exceptions import (
    CitationException,
    ExplainabilityException,
    NarrativeException,
    TraceException,
)

# Models
from adip.explainability.contracts.models import (
    ExplanationAudience,
    ExplanationCitation,
    ExplanationConfidence,
    ExplanationContext,
    ExplanationDecision,
    ExplanationHealth,
    ExplanationMetadata,
    ExplanationMetrics,
    ExplanationNarrative,
    ExplanationPackage,
    ExplanationPolicy,
    ExplanationRequest,
    ExplanationResult,
    ExplanationSession,
    ExplanationTrace,
)
from adip.explainability.contracts.models import (
    ExplanationLayer as ExplanationLayerModel,
)

# DTOs
from adip.explainability.dtos import (
    ExplanationPackageDTO,
    ExplanationRequestDTO,
    ExplanationResponseDTO,
)

# Enums
from adip.explainability.enums import (
    CitationType,
    ExplanationDomain,
    ExplanationLayer,
    ExplanationStatus,
    NarrativeType,
)
from adip.explainability.execution.audience_formatter import (
    AudienceFormatter as ExecutionAudienceFormatter,
)
from adip.explainability.execution.audience_validator import AudienceValidator
from adip.explainability.execution.builder import ExplanationBuilder
from adip.explainability.execution.citation_manager import CitationManager
from adip.explainability.execution.metrics import ExplainabilityMetricsCollector

# Execution Models
from adip.explainability.execution.models import (
    AudienceFormat,
    ExplanationSection,
    ExplanationTimeline,
    NarrativeTemplate,
    PolicyRule,
    QualityScore,
    SectionContent,
    TraceRecord,
)
from adip.explainability.execution.models import (
    ExplainabilityMetrics as ExecutionExplainabilityMetrics,
)

# Execution Components
from adip.explainability.execution.narrative_builder import (
    NarrativeBuilder as ExecutionNarrativeBuilder,
)
from adip.explainability.execution.policy_engine import PolicyEngine
from adip.explainability.execution.quality_manager import ExplanationQualityManager
from adip.explainability.execution.sections import ExplanationSections
from adip.explainability.execution.template_manager import TemplateManager
from adip.explainability.execution.timeline_builder import TimelineBuilder
from adip.explainability.execution.trace import ExplainabilityTrace
from adip.explainability.execution.trace_aggregator import TraceAggregator

# Interfaces
from adip.explainability.interfaces import (
    AudienceFormatter,
    CitationBuilder,
    ExplainabilityCoordinator,
    ExplainabilityManager,
    ExplainabilityService,
    ExplanationValidator,
    NarrativeBuilder,
    TraceBuilder,
)
from adip.explainability.orchestration.audit_package import ExplanationAuditPackage
from adip.explainability.orchestration.compliance import ExplanationCompliance
from adip.explainability.orchestration.confidence import ExplanationConfidenceCalculator
from adip.explainability.orchestration.coordinator import ExplainabilityCoordinatorImpl
from adip.explainability.orchestration.export_profiles import ExplanationExportProfiles
from adip.explainability.orchestration.justification import ExplanationJustification
from adip.explainability.orchestration.lineage import ExplanationLineage
from adip.explainability.orchestration.manager import ExplainabilityManagerImpl
from adip.explainability.orchestration.readiness import ExplanationReadiness
from adip.explainability.orchestration.review import ExplanationReview

# Orchestration Components
from adip.explainability.orchestration.session import ExplanationSessionManager
from adip.explainability.orchestration.snapshot import ExplanationSnapshot
from adip.explainability.orchestration.version_manager import ExplanationVersionManager

# Service Components
from adip.explainability.services.hooks import IntegrationHooks, hooks
from adip.explainability.services.service import DefaultExplainabilityService

__all__ = [
    # Enums
    "ExplanationDomain",
    "ExplanationLayer",
    "ExplanationStatus",
    "NarrativeType",
    "CitationType",
    # Models
    "ExplanationRequest",
    "ExplanationResult",
    "ExplanationPackage",
    "ExplanationNarrative",
    "ExplanationContext",
    "ExplanationAudience",
    "ExplanationPolicy",
    "ExplanationTrace",
    "ExplanationCitation",
    "ExplanationLayerModel",
    "ExplanationConfidence",
    "ExplanationMetadata",
    "ExplanationHealth",
    "ExplanationMetrics",
    "ExplanationSession",
    "ExplanationDecision",
    # Events
    "ExplanationEvent",
    "ExplanationRequested",
    "ExplanationGenerated",
    "ExplanationValidated",
    "ExplanationCompleted",
    # Exceptions
    "ExplainabilityException",
    "NarrativeException",
    "CitationException",
    "TraceException",
    # DTOs
    "ExplanationRequestDTO",
    "ExplanationResponseDTO",
    "ExplanationPackageDTO",
    # Interfaces
    "ExplainabilityService",
    "ExplainabilityManager",
    "ExplainabilityCoordinator",
    "NarrativeBuilder",
    "CitationBuilder",
    "TraceBuilder",
    "AudienceFormatter",
    "ExplanationValidator",
    # Execution Models
    "AudienceFormat",
    "ExplanationSection",
    "ExplanationTimeline",
    "NarrativeTemplate",
    "PolicyRule",
    "QualityScore",
    "SectionContent",
    "TraceRecord",
    # Execution Components
    "ExecutionNarrativeBuilder",
    "ExecutionAudienceFormatter",
    "CitationManager",
    "ExplanationBuilder",
    "TraceAggregator",
    "ExplanationSections",
    "ExplanationQualityManager",
    "TimelineBuilder",
    "TemplateManager",
    "PolicyEngine",
    "ExplainabilityTrace",
    "ExplainabilityMetricsCollector",
    "AudienceValidator",
    # Orchestration
    "ExplanationSessionManager",
    "ExplanationConfidenceCalculator",
    "ExplainabilityCoordinatorImpl",
    "ExplainabilityManagerImpl",
    "ExplanationReview",
    "ExplanationVersionManager",
    "ExplanationReadiness",
    "ExplanationLineage",
    "ExplanationSnapshot",
    "ExplanationJustification",
    "ExplanationCompliance",
    "ExplanationAuditPackage",
    "ExplanationExportProfiles",
    # Service
    "IntegrationHooks",
    "hooks",
    "DefaultExplainabilityService",
]
