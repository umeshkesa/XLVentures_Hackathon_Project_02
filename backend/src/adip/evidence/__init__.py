"""Evidence Fusion Engine — AI Decision Layer component.

The Evidence Fusion Engine collects evidence from multiple platform
services, normalizes it, correlates it, validates it, scores it,
and produces unified EvidencePackages for the Reasoning Engine.

Architecture:
    EvidenceService (ONLY public API)
        ↕
    EvidenceManager (internal facade)
        ↕
    EvidenceCoordinator (pipeline orchestrator)
        ↕
    Collector -> Validator -> Normalizer -> Correlator -> Scorer
        ↕
    GraphBuilder -> PackageBuilder

Phases:
    Phase 1 (current): Architecture, Contracts & Models
    Phase 2: Execution Pipeline (deterministic placeholders)
    Phase 3: Enterprise Orchestration
    Phase 3.5: Enterprise Refinement & Interface Freeze
"""

from __future__ import annotations

# Events
from adip.evidence.contracts.events import (
    EvidenceCollected,
    EvidenceCorrelated,
    EvidenceEvent,
    EvidenceFused,
    EvidenceNormalized,
    EvidencePackaged,
    EvidenceValidated,
)

# Exceptions
from adip.evidence.contracts.exceptions import (
    EvidenceCorrelationException,
    EvidenceException,
    EvidenceFusionException,
    EvidenceValidationException,
)

# Models
from adip.evidence.contracts.models import (
    Evidence,
    EvidenceConfidence,
    EvidenceContext,
    EvidenceDecision,
    EvidenceEdge,
    EvidenceExplainabilityMetadata,
    EvidenceGraph,
    EvidenceHealth,
    EvidenceLineage,
    EvidenceMetadata,
    EvidenceMetrics,
    EvidenceNode,
    EvidencePackage,
    EvidenceProvenance,
    EvidenceQuality,
    EvidenceSession,
    EvidenceSnapshot,
    EvidenceSource,
)

# DTOs
from adip.evidence.dtos import EvidencePackageDTO, EvidenceRequestDTO, EvidenceResponseDTO

# Enums
from adip.evidence.enums import (
    BundleType,
    ConsensusLevel,
    EvidenceClassification,
    EvidenceDomain,
    EvidencePriority,
    EvidenceStatus,
    EvidenceType,
    FusionPolicyType,
    RelationshipType,
)
from adip.evidence.execution.consensus_manager import EvidenceConsensusManager

# Execution-layer models (Phase 2)
from adip.evidence.execution.models import (
    ConflictReport,
    CorrelationResult,
    CorrelationScore,
    EvidenceBundle,
    FreshnessThreshold,
    SourceReliability,
    Timeline,
    TimelineEntry,
    TraceRecord,
    TrustScore,
)

# Trace stages
from adip.evidence.execution.trace import TraceStage

# Phase 3.5 execution components
from adip.evidence.execution.weight_manager import EvidenceWeightManager

# Interfaces
from adip.evidence.interfaces import (
    EvidenceCollector,
    EvidenceCoordinator,
    EvidenceCorrelator,
    EvidenceGraphBuilder,
    EvidenceManager,
    EvidenceNormalizer,
    EvidencePackageBuilder,
    EvidenceScorer,
    EvidenceService,
    EvidenceValidator,
)

# Phase 3 — Orchestration
from adip.evidence.orchestration import (
    EvidenceConfidenceCalculator,
    EvidenceCoordinator,
    EvidenceManager,
    EvidenceSessionManager,
)

# Phase 3 — Services
from adip.evidence.services import (
    AuthResult,
    EvidenceService,
    IntegrationHooks,
    hooks,
)

__all__ = [
    # Enums
    "EvidenceDomain",
    "EvidenceType",
    "EvidenceStatus",
    "EvidenceClassification",
    "EvidencePriority",
    "RelationshipType",
    "BundleType",
    "ConsensusLevel",
    "FusionPolicyType",
    # Models
    "Evidence",
    "EvidenceSource",
    "EvidenceMetadata",
    "EvidenceProvenance",
    "EvidenceQuality",
    "EvidenceNode",
    "EvidenceEdge",
    "EvidenceGraph",
    "EvidencePackage",
    "EvidenceHealth",
    "EvidenceMetrics",
    "EvidenceSession",
    "EvidenceDecision",
    "EvidenceConfidence",
    "EvidenceExplainabilityMetadata",
    "EvidenceContext",
    "EvidenceLineage",
    "EvidenceSnapshot",
    # Events
    "EvidenceEvent",
    "EvidenceCollected",
    "EvidenceValidated",
    "EvidenceNormalized",
    "EvidenceCorrelated",
    "EvidenceFused",
    "EvidencePackaged",
    # Exceptions
    "EvidenceException",
    "EvidenceValidationException",
    "EvidenceCorrelationException",
    "EvidenceFusionException",
    # DTOs
    "EvidenceRequestDTO",
    "EvidenceResponseDTO",
    "EvidencePackageDTO",
    # Interfaces
    "EvidenceService",
    "EvidenceManager",
    "EvidenceCoordinator",
    "EvidenceCollector",
    "EvidenceValidator",
    "EvidenceNormalizer",
    "EvidenceCorrelator",
    "EvidenceScorer",
    "EvidenceGraphBuilder",
    "EvidencePackageBuilder",
    # Phase 2 execution models
    "CorrelationResult",
    "ConflictReport",
    "CorrelationScore",
    "EvidenceBundle",
    "FreshnessThreshold",
    "SourceReliability",
    "Timeline",
    "TimelineEntry",
    "TraceRecord",
    "TrustScore",
    "TraceStage",
    # Phase 3.5 execution components
    "EvidenceWeightManager",
    "EvidenceConsensusManager",
    # Phase 3 — Orchestration
    "EvidenceConfidenceCalculator",
    "EvidenceCoordinator",
    "EvidenceManager",
    "EvidenceSessionManager",
    # Phase 3 — Services
    "AuthResult",
    "EvidenceService",
    "IntegrationHooks",
    "hooks",
]
