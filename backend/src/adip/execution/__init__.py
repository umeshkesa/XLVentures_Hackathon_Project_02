"""Action Engine — Execution, Monitoring, Retry & Compensation.

Phase 1: Architecture, Contracts & Models
Phase 2: Execution Runtime & Monitoring Pipeline
Phase 3: Enterprise Orchestration

Re-exports all public interfaces, enums, DTOs, models, and
execution components.
"""

from adip.execution.contracts import models as execution_models
from adip.execution.dtos import ExecutionRequestDTO, ExecutionResponseDTO, ExecutionResultDTO
from adip.execution.enums import ExecutionMode, ExecutionPriority, ExecutionState
from adip.execution.execution import (  # noqa: F401
    AuditTrail,
    CheckpointManager,
    ExecutionGraph,
    ExecutionMetricsCollector,
    ExecutionPolicyEngine,
    ExecutionProgressTracker,
    ExecutionReportGenerator,
    ExecutionStateMachine,
    ExecutionTelemetry,
    ExecutionTrace,
    FailureClassifier,
    ParallelTaskExecutor,
    ResourceMonitor,
    RuntimeEventBus,
)
from adip.execution.execution import (
    CompensationManager as CompensationRuntime,
)
from adip.execution.execution import (
    ExecutionMonitor as ExecutionMonitorRuntime,
)
from adip.execution.execution import (
    ExecutionScheduler as ExecutionSchedulerRuntime,
)
from adip.execution.execution import (
    RetryManager as RetryRuntime,
)
from adip.execution.interfaces import (  # noqa: F401
    CompensationManager,
    ExecutionAdapter,
    ExecutionCoordinator,
    ExecutionManager,
    ExecutionMonitor,
    ExecutionScheduler,
    ExecutionService,
    RetryManager,
    SandboxExecutor,
    TaskExecutor,
)
from adip.execution.orchestration import (  # noqa: F401
    ExecutionAdapterRegistry,
    ExecutionConfidenceCalculator,
    ExecutionContextManager,
    ExecutionCoordinatorImpl,
    ExecutionHealthManager,
    ExecutionLineage,
    ExecutionManagerImpl,
    ExecutionManifestBuilder,
    ExecutionQualityManager,
    ExecutionReadinessManager,
    ExecutionReview,
    ExecutionSessionManager,
    ExecutionSnapshot,
    ExecutionVersionManager,
)
from adip.execution.services import (  # noqa: F401
    DefaultExecutionService,
    IntegrationHooks,
    global_hooks,
)

__all__ = [
    # Enums
    "ExecutionState",
    "ExecutionMode",
    "ExecutionPriority",
    # Models
    "execution_models",
    # DTOs
    "ExecutionRequestDTO",
    "ExecutionResponseDTO",
    "ExecutionResultDTO",
    # Interfaces
    "ExecutionService",
    "ExecutionManager",
    "ExecutionCoordinator",
    "TaskExecutor",
    "RetryManager",
    "CompensationManager",
    "ExecutionMonitor",
    "ExecutionScheduler",
    "SandboxExecutor",
    "ExecutionAdapter",
    # Phase 2 Execution Components
    "ExecutionGraph",
    "ParallelTaskExecutor",
    "ExecutionPolicyEngine",
    "ExecutionSchedulerRuntime",
    "CheckpointManager",
    "RetryRuntime",
    "CompensationRuntime",
    "AuditTrail",
    "ExecutionTelemetry",
    "ResourceMonitor",
    "RuntimeEventBus",
    "ExecutionStateMachine",
    "ExecutionReportGenerator",
    "ExecutionTrace",
    "ExecutionMetricsCollector",
    "ExecutionProgressTracker",
    "ExecutionMonitorRuntime",
    "FailureClassifier",
    # Phase 3 Orchestration Components
    "ExecutionSessionManager",
    "ExecutionConfidenceCalculator",
    "ExecutionReadinessManager",
    "ExecutionReview",
    "ExecutionVersionManager",
    "ExecutionLineage",
    "ExecutionSnapshot",
    "ExecutionHealthManager",
    "ExecutionQualityManager",
    "ExecutionManifestBuilder",
    "ExecutionAdapterRegistry",
    "ExecutionContextManager",
    "ExecutionCoordinatorImpl",
    "ExecutionManagerImpl",
    # Phase 3 Services
    "DefaultExecutionService",
    "IntegrationHooks",
    "global_hooks",
]
