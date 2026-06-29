"""Reasoning Engine — AI Decision Layer component.

The Reasoning Engine is the core intelligence component of ADIP.
It consumes EvidencePackages from the Evidence Fusion Engine and
produces structured reasoning, hypotheses, inference paths, and
reasoning decisions that will later be transformed into
recommendations by downstream components.

Architecture:
    ReasoningService (ONLY public API)
        ↕
    ReasoningManager (internal facade)
        ↕
    ReasoningCoordinator (pipeline orchestrator)
        ↕
    HypothesisGenerator -> InferenceEngine -> ContradictionDetector
        ↕
    ReasoningPathBuilder -> ReasoningValidator -> ReasoningStrategy

Phases:
    Phase 1: Architecture, Contracts & Models (current)
    Phase 2: Execution Pipeline (deterministic placeholders)
    Phase 3: Enterprise Orchestration
    Phase 3.5: Enterprise Refinement & Interface Freeze
"""

from __future__ import annotations

# Events
from adip.reasoning.contracts.events import (
    ContradictionDetected,
    HypothesisGenerated,
    InferenceCompleted,
    ReasoningCompleted,
    ReasoningEvent,
    ReasoningStarted,
)

# Exceptions
from adip.reasoning.contracts.exceptions import (
    ContradictionException,
    HypothesisException,
    InferenceException,
    ReasoningException,
)

# Models
from adip.reasoning.contracts.models import (
    Contradiction,
    Hypothesis,
    HypothesisSet,
    Inference,
    InferenceChain,
    ReasoningConfidence,
    ReasoningContext,
    ReasoningDecision,
    ReasoningExplainabilityMetadata,
    ReasoningHealth,
    ReasoningMetadata,
    ReasoningMetrics,
    ReasoningPath,
    ReasoningRequest,
    ReasoningResult,
    ReasoningSession,
    ReasoningStep,
    ReasoningStrategyConfig,
    ReasoningTrace,
)

# DTOs
from adip.reasoning.dtos import ReasoningDecisionDTO, ReasoningRequestDTO, ReasoningResponseDTO

# Enums
from adip.reasoning.enums import (
    ContradictionResolutionStatus,
    ContradictionSeverity,
    HypothesisStatus,
    ReasoningDomain,
    ReasoningStatus,
    ReasoningStrategyType,
    TraceStage,
)

# Interfaces
from adip.reasoning.interfaces import (
    ContradictionDetector,
    HypothesisGenerator,
    InferenceEngine,
    ReasoningCoordinator,
    ReasoningManager,
    ReasoningPathBuilder,
    ReasoningService,
    ReasoningStrategy,
    ReasoningValidator,
)

__all__ = [
    # Enums
    "ReasoningDomain",
    "ReasoningStatus",
    "ReasoningStrategyType",
    "HypothesisStatus",
    "ContradictionSeverity",
    "ContradictionResolutionStatus",
    "TraceStage",
    # Models
    "ReasoningRequest",
    "ReasoningResult",
    "ReasoningDecision",
    "ReasoningSession",
    "ReasoningContext",
    "ReasoningMetadata",
    "ReasoningConfidence",
    "ReasoningExplainabilityMetadata",
    "ReasoningHealth",
    "ReasoningMetrics",
    "ReasoningTrace",
    "ReasoningPath",
    "ReasoningStep",
    "Hypothesis",
    "HypothesisSet",
    "Inference",
    "InferenceChain",
    "Contradiction",
    "ReasoningStrategyConfig",
    # Events
    "ReasoningEvent",
    "ReasoningStarted",
    "HypothesisGenerated",
    "InferenceCompleted",
    "ContradictionDetected",
    "ReasoningCompleted",
    # Exceptions
    "ReasoningException",
    "HypothesisException",
    "InferenceException",
    "ContradictionException",
    # DTOs
    "ReasoningRequestDTO",
    "ReasoningResponseDTO",
    "ReasoningDecisionDTO",
    # Interfaces
    "ReasoningService",
    "ReasoningManager",
    "ReasoningCoordinator",
    "ReasoningStrategy",
    "HypothesisGenerator",
    "InferenceEngine",
    "ContradictionDetector",
    "ReasoningValidator",
    "ReasoningPathBuilder",
]
