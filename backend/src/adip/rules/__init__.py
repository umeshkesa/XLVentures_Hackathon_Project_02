"""Rule Manager — enterprise policy platform for the ADIP framework.

The Rule Manager handles deterministic decision making, validation,
compliance, safety, approvals, and business logic enforcement.
RuleService is the ONLY public API for external modules (Planner,
Workflow Engine, Reasoning Engine, etc.).

Architecture:
    RuleService  →  RuleManager  →  RuleCoordinator
    (public API)     (lightweight)    (sub-component orchestration)
                                          ├── RuleValidator
                                          ├── RuleParser
                                          ├── RuleCompiler
                                          ├── RuleEvaluator
                                          ├── RuleVersionManager
                                          ├── RuleLifecycleManager
                                          ├── EvaluationStrategy
                                          ├── ConflictResolver
                                          ├── PriorityEngine
                                          ├── RuleCache
                                          ├── RulePolicyEngine
                                          ├── RuleTrace
                                          └── RuleMetricsCollector

Domain boundaries follow the ADIP Knowledge Manager pattern with
component-level interfaces and dependency injection throughout.
"""

from __future__ import annotations

from adip.rules.contracts.events import (
    EventVersion,
    RuleActivated,
    RuleArchived,
    RuleConflictDetected,
    RuleCreated,
    RuleEvaluated,
    RuleEvent,
    RuleUpdated,
)
from adip.rules.contracts.exceptions import (
    RuleConflictException,
    RuleEvaluationException,
    RuleException,
    RuleValidationException,
)
from adip.rules.contracts.models import (
    Rule,
    RuleAction,
    RuleCondition,
    RuleConfidence,
    RuleContext,
    RuleDecision,
    RuleEvaluation,
    RuleExplainabilityMetadata,
    RuleHealth,
    RuleMetrics,
    RulePolicy,
    RuleSession,
    RuleSet,
)
from adip.rules.dtos import (
    RuleEvaluationDTO,
    RuleRequestDTO,
    RuleResponseDTO,
)
from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
    RuleLifecycleStatus,
    RuleType,
)
from adip.rules.execution.cache import RuleCache
from adip.rules.execution.compiler import RuleCompiler
from adip.rules.execution.conflict_resolver import ConflictResolver
from adip.rules.execution.evaluator import RuleEvaluator
from adip.rules.execution.lifecycle import RuleLifecycleManager
from adip.rules.execution.metrics import RuleMetricsCollector
from adip.rules.execution.models import (
    CompiledRule,
    ConflictReport,
    LifecycleHistoryEntry,
    TraceRecord,
    VersionRecord,
)
from adip.rules.execution.parser import RuleParser
from adip.rules.execution.policy import RulePolicyEngine
from adip.rules.execution.priority_engine import PriorityEngine
from adip.rules.execution.strategies import (
    CompositeEvaluationStrategy,
    ConditionalEvaluationStrategy,
    EvaluationStrategy,
    PriorityEvaluationStrategy,
    SequentialEvaluationStrategy,
    get_strategy,
)
from adip.rules.execution.trace import RuleTrace
from adip.rules.execution.validator import RuleValidator
from adip.rules.execution.version_manager import RuleVersionManager
from adip.rules.interfaces import (
    CompositeEvaluation as AbstractCompositeEvaluation,
)
from adip.rules.interfaces import (
    ConditionalEvaluation as AbstractConditionalEvaluation,
)
from adip.rules.interfaces import (
    ConflictResolver as AbstractConflictResolver,
)
from adip.rules.interfaces import (
    EvaluationStrategy as AbstractEvaluationStrategy,
)
from adip.rules.interfaces import (
    PriorityEngine as AbstractPriorityEngine,
)
from adip.rules.interfaces import (
    PriorityEvaluation as AbstractPriorityEvaluation,
)
from adip.rules.interfaces import (
    RuleCache as AbstractRuleCache,
)
from adip.rules.interfaces import (
    RuleCompiler as AbstractRuleCompiler,
)
from adip.rules.interfaces import (
    RuleCoordinator as AbstractRuleCoordinator,
)
from adip.rules.interfaces import (
    RuleEvaluator as AbstractRuleEvaluator,
)
from adip.rules.interfaces import (
    RuleManager as AbstractRuleManager,
)
from adip.rules.interfaces import (
    RuleParser as AbstractRuleParser,
)
from adip.rules.interfaces import (
    RuleService as AbstractRuleService,
)
from adip.rules.interfaces import (
    RuleValidator as AbstractRuleValidator,
)
from adip.rules.interfaces import (
    SequentialEvaluation as AbstractSequentialEvaluation,
)

__all__ = [
    # Enums
    "RuleDomain",
    "RuleType",
    "RuleLifecycleStatus",
    "EvaluationStrategyType",
    # Models
    "Rule",
    "RuleSet",
    "RuleCondition",
    "RuleAction",
    "RuleContext",
    "RuleDecision",
    "RuleEvaluation",
    "RulePolicy",
    "RuleHealth",
    "RuleMetrics",
    "RuleSession",
    "RuleConfidence",
    "RuleExplainabilityMetadata",
    # DTOs
    "RuleRequestDTO",
    "RuleResponseDTO",
    "RuleEvaluationDTO",
    # Events
    "EventVersion",
    "RuleEvent",
    "RuleCreated",
    "RuleUpdated",
    "RuleActivated",
    "RuleEvaluated",
    "RuleConflictDetected",
    "RuleArchived",
    # Exceptions
    "RuleException",
    "RuleValidationException",
    "RuleConflictException",
    "RuleEvaluationException",
    # Interfaces (abstract)
    "AbstractRuleService",
    "AbstractRuleManager",
    "AbstractRuleCoordinator",
    "AbstractRuleValidator",
    "AbstractRuleParser",
    "AbstractRuleCompiler",
    "AbstractRuleEvaluator",
    "AbstractConflictResolver",
    "AbstractPriorityEngine",
    "AbstractRuleCache",
    "AbstractEvaluationStrategy",
    "AbstractSequentialEvaluation",
    "AbstractPriorityEvaluation",
    "AbstractConditionalEvaluation",
    "AbstractCompositeEvaluation",
    # Execution models
    "CompiledRule",
    "ConflictReport",
    "LifecycleHistoryEntry",
    "TraceRecord",
    "VersionRecord",
    # Execution components
    "RuleValidator",
    "RuleParser",
    "RuleCompiler",
    "RuleVersionManager",
    "RuleLifecycleManager",
    "RuleEvaluator",
    "EvaluationStrategy",
    "SequentialEvaluationStrategy",
    "PriorityEvaluationStrategy",
    "ConditionalEvaluationStrategy",
    "CompositeEvaluationStrategy",
    "get_strategy",
    "ConflictResolver",
    "PriorityEngine",
    "RuleCache",
    "RulePolicyEngine",
    "RuleTrace",
    "RuleMetricsCollector",
]
