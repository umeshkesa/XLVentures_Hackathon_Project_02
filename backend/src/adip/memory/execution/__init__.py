"""Memory Manager execution layer — internal subsystem components.

Contains the Memory Lifecycle Manager, Router, Storage Adapters,
Memory Stores, Policy Engine, Validator, Cache Manager, Version
Manager, Audit Manager, Search Service, Trace Manager, and Metrics
Collector.

These components form the internal Memory Platform that will be
orchestrated by the MemoryManager (Phase 3).
"""

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

__all__ = [
    "AuditManager",
    "AuditRecord",
    "CacheEntry",
    "CacheManager",
    "CacheStore",
    "ChromaAdapter",
    "ConversationMemoryStore",
    "LearningMemoryStore",
    "MemoryLifecycleHistory",
    "MemoryLifecycleManager",
    "MemoryPolicyEngine",
    "MemoryRouter",
    "MemorySearchService",
    "MemoryTrace",
    "MemoryValidator",
    "MetricsCollector",
    "PlanningMemoryStore",
    "PlaceholderStorageAdapter",
    "PolicyDecision",
    "PostgresAdapter",
    "RecommendationMemoryStore",
    "RedisAdapter",
    "SearchQuery",
    "SessionMemoryStore",
    "TraceManager",
    "UserMemoryStore",
    "VersionHistory",
    "VersionManager",
    "WorkflowMemoryStore",
]
