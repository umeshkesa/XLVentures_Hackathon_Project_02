"""Recommendation Engine — Business Action Layer component.

The Recommendation Engine consumes validated ReasoningDecisions from the
Reasoning Engine and transforms them into actionable business recommendations.
It produces ranked, policy-aware, business-ready recommendations without
performing any reasoning itself.

Architecture:
    RecommendationService (ONLY public API)
        ↕
    RecommendationManager (internal facade)
        ↕
    RecommendationCoordinator (pipeline orchestrator)
        ↕
    RecommendationGenerator -> RecommendationRanker -> RecommendationValidator

Phases:
    Phase 1: Architecture, Contracts & Models (current)
    Phase 2: Execution Pipeline (deterministic placeholders)
    Phase 3: Enterprise Orchestration
    Phase 3.5: Enterprise Refinement & Interface Freeze
"""

from __future__ import annotations

# Events
from adip.recommendation.contracts.events import (
    RecommendationCompleted,
    RecommendationEvent,
    RecommendationGenerated,
    RecommendationRanked,
    RecommendationRequested,
    RecommendationValidated,
)

# Exceptions
from adip.recommendation.contracts.exceptions import (
    RecommendationException,
    RecommendationPolicyException,
    RecommendationRankingException,
    RecommendationValidationException,
)

# Models
from adip.recommendation.contracts.models import (
    RecommendationBenefit,
    RecommendationCandidate,
    RecommendationConfidence,
    RecommendationConstraint,
    RecommendationContext,
    RecommendationDecision,
    RecommendationExplainabilityMetadata,
    RecommendationHealth,
    RecommendationImpact,
    RecommendationMetadata,
    RecommendationMetrics,
    RecommendationPackage,
    RecommendationPolicy,
    RecommendationRequest,
    RecommendationResult,
    RecommendationRisk,
    RecommendationSession,
    RecommendationTrace,
)
from adip.recommendation.contracts.models import (
    RecommendationGoal as RecommendationGoalModel,
)
from adip.recommendation.contracts.models import (
    RecommendationPriority as RecommendationPriorityModel,
)
from adip.recommendation.contracts.models import (
    RecommendationStrategy as RecommendationStrategyModel,
)

# DTOs
from adip.recommendation.dtos import (
    RecommendationPackageDTO,
    RecommendationRequestDTO,
    RecommendationResponseDTO,
)

# Enums
from adip.recommendation.enums import (
    BenefitType,
    ConstraintType,
    FeasibilityLevel,
    FeasibilityStatus,
    ImplementationTimeline,
    RecommendationDomain,
    RecommendationGoal,
    RecommendationPriority,
    RecommendationReadinessStatus,
    RecommendationStatus,
    RecommendationStrategy,
    RecommendationTraceStage,
    TradeoffDimension,
)
from adip.recommendation.execution.cost_analyzer import CostAnalyzer
from adip.recommendation.execution.dependency_manager import DependencyManager
from adip.recommendation.execution.feasibility_analyzer import FeasibilityAnalyzer
from adip.recommendation.execution.generator import (
    RecommendationGenerator as ExecutionRecommendationGenerator,
)
from adip.recommendation.execution.implementation_plan_builder import ImplementationPlanBuilder
from adip.recommendation.execution.metrics import RecommendationMetricsCollector

# Execution Models
from adip.recommendation.execution.models import (
    CostEstimate,
    DependencyGraph,
    DependencyNode,
    FeasibilityAnalysis,
    ImplementationPlan,
    ImplementationStep,
    OutcomePrediction,
    PolicyEvalResult,
    RecommendationScore,
    TimelineEstimate,
    TraceRecord,
    TradeoffAnalysis,
)
from adip.recommendation.execution.models import (
    RecommendationMetrics as ExecutionRecommendationMetrics,
)
from adip.recommendation.execution.models import (
    RecommendationPortfolio as ExecutionRecommendationPortfolio,
)
from adip.recommendation.execution.outcome_predictor import OutcomePredictor
from adip.recommendation.execution.policy_evaluator import PolicyEvaluator
from adip.recommendation.execution.portfolio import (
    RecommendationPortfolio as ExecutionRecommendationPortfolioComponent,
)
from adip.recommendation.execution.ranker import (
    RecommendationRanker as ExecutionRecommendationRanker,
)
from adip.recommendation.execution.score_manager import ScoreManager

# Execution Components
from adip.recommendation.execution.strategy_selector import StrategySelector
from adip.recommendation.execution.timeline_manager import TimelineManager
from adip.recommendation.execution.trace import RecommendationTrace as ExecutionRecommendationTrace
from adip.recommendation.execution.tradeoff_analyzer import TradeoffAnalyzer

# Interfaces
from adip.recommendation.interfaces import (
    BenefitAnalyzer,
    ImpactEstimator,
    RecommendationCoordinator,
    RecommendationGenerator,
    RecommendationManager,
    RecommendationPolicyEngine,
    RecommendationRanker,
    RecommendationService,
    RecommendationValidator,
)
from adip.recommendation.orchestration.approval_readiness import (
    ApprovalReadinessResult,
    RecommendationApprovalReadiness,
)
from adip.recommendation.orchestration.confidence import RecommendationConfidenceCalculator
from adip.recommendation.orchestration.coordinator import RecommendationCoordinator
from adip.recommendation.orchestration.justification import (
    JustificationRecord,
    RecommendationJustification,
)
from adip.recommendation.orchestration.lineage import LineageEntry, RecommendationLineage
from adip.recommendation.orchestration.manager import RecommendationManager
from adip.recommendation.orchestration.portfolio_comparator import PortfolioComparator
from adip.recommendation.orchestration.portfolio_quality import (
    PortfolioQuality,
    PortfolioQualityResult,
)
from adip.recommendation.orchestration.quality import QualityResult, RecommendationQualityManager
from adip.recommendation.orchestration.readiness import RecommendationReadiness
from adip.recommendation.orchestration.review import RecommendationReview, ReviewResult

# Orchestration Components
from adip.recommendation.orchestration.session import RecommendationSessionManager
from adip.recommendation.orchestration.snapshot import RecommendationSnapshot, SnapshotRecord
from adip.recommendation.orchestration.version_manager import (
    RecommendationVersionManager,
    VersionRecord,
)

# Services
from adip.recommendation.services.hooks import IntegrationHooks, hooks
from adip.recommendation.services.service import DefaultRecommendationService

__all__ = [
    # Enums
    "RecommendationDomain",
    "RecommendationStatus",
    "RecommendationStrategy",
    "RecommendationGoal",
    "RecommendationPriority",
    "ConstraintType",
    "BenefitType",
    "ImplementationTimeline",
    "FeasibilityStatus",
    "TradeoffDimension",
    "FeasibilityLevel",
    "RecommendationTraceStage",
    # Models
    "RecommendationRequest",
    "RecommendationResult",
    "RecommendationDecision",
    "RecommendationPackage",
    "RecommendationCandidate",
    "RecommendationStrategyModel",
    "RecommendationGoalModel",
    "RecommendationContext",
    "RecommendationConstraint",
    "RecommendationPriorityModel",
    "RecommendationImpact",
    "RecommendationBenefit",
    "RecommendationRisk",
    "RecommendationPolicy",
    "RecommendationConfidence",
    "RecommendationMetadata",
    "RecommendationHealth",
    "RecommendationMetrics",
    "RecommendationSession",
    "RecommendationExplainabilityMetadata",
    "RecommendationTrace",
    "RecommendationScore",
    "FeasibilityAnalysis",
    "CostEstimate",
    "DependencyNode",
    "DependencyGraph",
    "ImplementationStep",
    "ImplementationPlan",
    "TimelineEstimate",
    "TradeoffAnalysis",
    "PolicyEvalResult",
    "OutcomePrediction",
    "ExecutionRecommendationPortfolio",
    "TraceRecord",
    "ExecutionRecommendationMetrics",
    # Execution Components
    "StrategySelector",
    "ExecutionRecommendationGenerator",
    "ExecutionRecommendationRanker",
    "ScoreManager",
    "FeasibilityAnalyzer",
    "CostAnalyzer",
    "DependencyManager",
    "ImplementationPlanBuilder",
    "TimelineManager",
    "TradeoffAnalyzer",
    "PolicyEvaluator",
    "OutcomePredictor",
    "ExecutionRecommendationPortfolioComponent",
    "ExecutionRecommendationTrace",
    "RecommendationMetricsCollector",
    # Events
    "RecommendationEvent",
    "RecommendationRequested",
    "RecommendationGenerated",
    "RecommendationRanked",
    "RecommendationValidated",
    "RecommendationCompleted",
    # Exceptions
    "RecommendationException",
    "RecommendationValidationException",
    "RecommendationRankingException",
    "RecommendationPolicyException",
    # DTOs
    "RecommendationRequestDTO",
    "RecommendationResponseDTO",
    "RecommendationPackageDTO",
    # Interfaces
    "RecommendationService",
    "RecommendationManager",
    "RecommendationCoordinator",
    "RecommendationGenerator",
    "RecommendationRanker",
    "RecommendationValidator",
    "RecommendationPolicyEngine",
    "ImpactEstimator",
    "BenefitAnalyzer",
    # Enums
    "RecommendationReadinessStatus",
    # Orchestration Components
    "RecommendationSessionManager",
    "RecommendationConfidenceCalculator",
    "RecommendationReview",
    "ReviewResult",
    "RecommendationVersionManager",
    "VersionRecord",
    "RecommendationReadiness",
    "RecommendationLineage",
    "LineageEntry",
    "RecommendationSnapshot",
    "SnapshotRecord",
    "PortfolioComparator",
    "RecommendationCoordinator",
    "RecommendationManager",
    # Services
    "IntegrationHooks",
    "hooks",
    "DefaultRecommendationService",
    # Phase 3.5 Components
    "RecommendationQualityManager",
    "QualityResult",
    "RecommendationJustification",
    "JustificationRecord",
    "RecommendationApprovalReadiness",
    "ApprovalReadinessResult",
    "PortfolioQuality",
    "PortfolioQualityResult",
]
