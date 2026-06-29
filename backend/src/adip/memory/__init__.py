"""ADIP Memory Manager Module — central abstraction for all memory operations.

No module should access Redis, PostgreSQL, or ChromaDB directly.
All memory access must flow through the Memory Manager.

MemoryService is the ONLY public API.

Architecture:
    MemoryService → MemoryManager → MemoryCoordinator → (Phase 2 components)
"""

from adip.memory.contracts.events import (
    EVENT_VERSION,
    MemoryArchived,
    MemoryCached,
    MemoryCreated,
    MemoryDeleted,
    MemoryEvicted,
    MemoryExpired,
    MemoryLifecycleChanged,
    MemoryRestored,
    MemoryRetrieved,
    MemoryUpdated,
)
from adip.memory.contracts.exceptions import (
    MemoryException,
    MemoryExpiredException,
    MemoryNotFoundException,
    MemoryPolicyException,
    MemoryValidationException,
    StorageException,
)
from adip.memory.contracts.models import (
    CacheMemory,
    ConversationMemory,
    ExplainabilityMetadata,
    LearningMemory,
    MemoryContext,
    MemoryMetrics,
    MemoryPolicy,
    MemoryRecord,
    PlanningMemory,
    RecommendationMemory,
    SessionMemory,
    UserMemory,
    WorkflowMemory,
)
from adip.memory.enums import (
    MemoryLifecycleStatus,
    MemoryOperation,
    MemoryTier,
    MemoryType,
    RetentionPolicy,
)
from adip.memory.execution.adapters import (
    ChromaAdapter,
    PlaceholderStorageAdapter,
    PostgresAdapter,
    RedisAdapter,
)
from adip.memory.execution.audit_manager import AuditManager
from adip.memory.execution.cache_manager import CacheManager
from adip.memory.execution.lifecycle import MemoryLifecycleManager
from adip.memory.execution.metrics import MetricsCollector
from adip.memory.execution.models import (
    AuditRecord,
    CacheEntry,
    MemoryLifecycleHistory,
    MemoryTrace,
    PolicyDecision,
    SearchQuery,
    VersionHistory,
)
from adip.memory.execution.policy_engine import MemoryPolicyEngine
from adip.memory.execution.router import MemoryRouter
from adip.memory.execution.search import MemorySearchService
from adip.memory.execution.stores import (
    CacheStore,
    ConversationMemoryStore,
    LearningMemoryStore,
    PlanningMemoryStore,
    RecommendationMemoryStore,
    SessionMemoryStore,
    UserMemoryStore,
    WorkflowMemoryStore,
)
from adip.memory.execution.trace import TraceManager
from adip.memory.execution.validator import MemoryValidator
from adip.memory.execution.version_manager import VersionManager
from adip.memory.interfaces import (
    MemoryManager,
    MemoryService,
    StorageAdapter,
)
from adip.memory.interfaces import (
    MemoryRouter as MemoryRouterInterface,
)
from adip.memory.orchestration import (
    AggregatedTracing,
    IntegrationHooks,
    MemoryCoordinator,
    MemoryDomain,
    MemoryHealth,
    MemoryOperationPipeline,
    MemorySession,
    MemoryTransaction,
    MetricsAggregator,
)
from adip.memory.services.dtos import (
    MemoryRequestDTO,
    MemoryResponseDTO,
    MemorySearchRequestDTO,
    MemorySearchResponseDTO,
)
from adip.memory.services.manager import DefaultMemoryManager
from adip.memory.services.service import DefaultMemoryService

__all__ = [
    "AggregatedTracing",
    "AuditManager",
    "AuditRecord",
    "CacheEntry",
    "CacheManager",
    "CacheMemory",
    "CacheStore",
    "ChromaAdapter",
    "ConversationMemory",
    "ConversationMemoryStore",
    "DefaultMemoryManager",
    "DefaultMemoryService",
    "EVENT_VERSION",
    "ExplainabilityMetadata",
    "IntegrationHooks",
    "LearningMemory",
    "LearningMemoryStore",
    "MemoryArchived",
    "MemoryCached",
    "MemoryContext",
    "MemoryCoordinator",
    "MemoryCreated",
    "MemoryDeleted",
    "MemoryDomain",
    "MemoryEvent",
    "MemoryEvicted",
    "MemoryException",
    "MemoryExpired",
    "MemoryExpiredException",
    "MemoryHealth",
    "MemoryLifecycleChanged",
    "MemoryLifecycleHistory",
    "MemoryLifecycleManager",
    "MemoryLifecycleStatus",
    "MemoryManager",
    "MemoryMetrics",
    "MemoryNotFoundException",
    "MemoryOperation",
    "MemoryOperationPipeline",
    "MemoryPolicy",
    "MemoryPolicyEngine",
    "MemoryPolicyException",
    "MemoryRecord",
    "MemoryRequestDTO",
    "MemoryResponseDTO",
    "MemoryRestored",
    "MemoryRetrieved",
    "MemoryRouter",
    "MemoryRouterInterface",
    "MemorySearchRequestDTO",
    "MemorySearchResponseDTO",
    "MemorySearchService",
    "MemoryService",
    "MemorySession",
    "MemoryTier",
    "MemoryTrace",
    "MemoryTransaction",
    "MemoryType",
    "MemoryUpdated",
    "MemoryValidationException",
    "MemoryValidator",
    "MetricsAggregator",
    "MetricsCollector",
    "PlaceholderStorageAdapter",
    "PlanningMemory",
    "PlanningMemoryStore",
    "PolicyDecision",
    "PostgresAdapter",
    "RecommendationMemory",
    "RecommendationMemoryStore",
    "RedisAdapter",
    "RetentionPolicy",
    "SearchQuery",
    "SessionMemory",
    "SessionMemoryStore",
    "StorageAdapter",
    "StorageException",
    "TraceManager",
    "UserMemory",
    "UserMemoryStore",
    "VersionHistory",
    "VersionManager",
    "WorkflowMemory",
    "WorkflowMemoryStore",
]
