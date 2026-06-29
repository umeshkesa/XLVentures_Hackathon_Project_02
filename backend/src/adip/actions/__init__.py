"""Action Manager — Action Planning & Execution Readiness.

Phase 1: Architecture, Contracts & Models
Phase 2: Planning, Optimization & Execution Preparation Pipeline
Phase 3: Enterprise Orchestration

Re-exports all public interfaces, execution components,
and orchestration components.
"""

from adip.actions.contracts import models as action_models
from adip.actions.dtos import ActionPlanDTO, ActionRequestDTO, ActionResponseDTO
from adip.actions.enums import ActionPriority, ActionType, ExecutionReadiness
from adip.actions.execution import (
    ActionCostEstimator,
    ActionFeasibilityAnalyzer,
    ActionGraphBuilder,
    ActionMetrics,
    ActionOptimizationEngine,
    ActionPlanner,
    ActionPolicyEngine,
    ActionRiskEvaluator,
    ActionTrace,
    CompensationStrategyManager,
    CriticalPathAnalyzer,
    DependencyResolver,
    ExecutionTimeline,
    ExecutionWindowManager,
    ParallelActionPlanner,
    ResourceAllocator,
    ResourceConflictDetector,
)
from adip.actions.interfaces import (
    ActionCoordinator,
    ActionManager,
    ActionService,
    ReadinessValidator,
    RollbackPlanner,
    SchedulePlanner,
)
from adip.actions.interfaces import (
    ActionPlanner as ActionPlannerInterface,
)
from adip.actions.interfaces import (
    DependencyResolver as DependencyResolverInterface,
)
from adip.actions.interfaces import (
    ResourceAllocator as ResourceAllocatorInterface,
)
from adip.actions.orchestration import (
    ActionConfidenceCalculator,
    ActionExecutionReadiness,
    ActionLineage,
    ActionPolicyCompliance,
    ActionReview,
    ActionSessionManager,
    ActionSnapshot,
    ActionVersionManager,
    ExecutionContextBuilder,
    ExecutionHealth,
    ExecutionPackageBuilder,
    PlanQualityManager,
)
from adip.actions.orchestration.coordinator import (
    ActionCoordinator as ActionCoordinatorImpl,
)
from adip.actions.orchestration.manager import (
    ActionManager as ActionManagerImpl,
)
from adip.actions.services import (
    DefaultActionService,
    IntegrationHooks,
)

__all__ = [
    # Enums
    "ActionType",
    "ActionPriority",
    "ExecutionReadiness",
    # Models
    "action_models",
    # DTOs
    "ActionRequestDTO",
    "ActionPlanDTO",
    "ActionResponseDTO",
    # Interfaces
    "ActionService",
    "ActionManager",
    "ActionCoordinator",
    "ActionPlannerInterface",
    "DependencyResolverInterface",
    "ResourceAllocatorInterface",
    "SchedulePlanner",
    "RollbackPlanner",
    "ReadinessValidator",
    # Phase 2 Execution Components
    "ActionPlanner",
    "ActionGraphBuilder",
    "ParallelActionPlanner",
    "CriticalPathAnalyzer",
    "DependencyResolver",
    "ResourceAllocator",
    "ResourceConflictDetector",
    "ExecutionWindowManager",
    "CompensationStrategyManager",
    "ActionCostEstimator",
    "ActionRiskEvaluator",
    "ActionPolicyEngine",
    "ExecutionTimeline",
    "ActionOptimizationEngine",
    "ActionFeasibilityAnalyzer",
    "ActionTrace",
    "ActionMetrics",
    # Phase 3 Orchestration Components
    "ActionSessionManager",
    "ActionConfidenceCalculator",
    "ActionExecutionReadiness",
    "ActionReview",
    "PlanQualityManager",
    "ExecutionPackageBuilder",
    "ActionVersionManager",
    "ActionLineage",
    "ActionSnapshot",
    "ExecutionHealth",
    "ActionPolicyCompliance",
    "ExecutionContextBuilder",
    "ActionCoordinatorImpl",
    "ActionManagerImpl",
    "DefaultActionService",
    "IntegrationHooks",
]
