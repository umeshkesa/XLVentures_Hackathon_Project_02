"""Knowledge Manager — enterprise knowledge platform for the ADIP framework.

The Knowledge Manager handles document ingestion, processing, indexing,
retrieval, and context generation. KnowledgeService is the ONLY public
API for external modules (Planner, Reasoning Engine, etc.).

Architecture:
    KnowledgeService  →  KnowledgeManager  →  KnowledgeCoordinator
        (public API)       (lightweight)       (sub-component orchestration)
                                                     ├── DocumentValidator
                                                     ├── DocumentCleaner
                                                     ├── OCRProcessor
                                                     ├── ChunkManager
                                                     ├── EmbeddingManager
                                                     ├── IndexManager
                                                     ├── VersionManager
                                                     ├── LifecycleManager
                                                     ├── ProvenanceManager
                                                     ├── PolicyEngine
                                                     ├── RetrievalStrategy
                                                     ├── HybridRetriever
                                                     ├── ResultFusion
                                                     ├── Reranker
                                                     ├── ContextBuilder
                                                     ├── KnowledgeCache
                                                     ├── SessionManager
                                                     ├── Trace
                                                     └── MetricsCollector

Domain boundaries follow the ADIP Memory Manager pattern with
component-level interfaces and dependency injection throughout.
"""

from __future__ import annotations

from adip.knowledge.contracts.events import (
    EventVersion,
    KnowledgeArchived,
    KnowledgeCreated,
    KnowledgeDeleted,
    KnowledgeEvent,
    KnowledgeIndexed,
    KnowledgeRetrieved,
    KnowledgeUpdated,
)
from adip.knowledge.contracts.exceptions import (
    EmbeddingException,
    IndexException,
    KnowledgeException,
    KnowledgeValidationException,
    RetrievalException,
)
from adip.knowledge.contracts.models import (
    ExplainabilityMetadata,
    KnowledgeChunk,
    KnowledgeConfidence,
    KnowledgeContext,
    KnowledgeDecision,
    KnowledgeDocument,
    KnowledgeEmbedding,
    KnowledgeHealth,
    KnowledgeIndex,
    KnowledgeMetadata,
    KnowledgeMetrics,
    KnowledgeProvenance,
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeSession,
)
from adip.knowledge.dtos import (
    KnowledgeContextDTO,
    KnowledgeRequestDTO,
    KnowledgeResponseDTO,
    KnowledgeSearchDTO,
)
from adip.knowledge.enums import (
    DocumentType,
    KnowledgeDomain,
    KnowledgeLifecycleStatus,
    KnowledgeStatus,
    RetrievalType,
)
from adip.knowledge.interfaces import (
    ChunkManager,
    ContextBuilder,
    DocumentProcessor,
    EmbeddingManager,
    IndexManager,
    KnowledgeCache,
    KnowledgeCoordinator,
    KnowledgeManager,
    KnowledgeService,
    Reranker,
    Retriever,
)
from adip.knowledge.orchestration import (
    KnowledgeCoordinator as DefaultKnowledgeCoordinator,
)
from adip.knowledge.orchestration import (
    KnowledgeManager as DefaultKnowledgeManager,
)
from adip.knowledge.services import (
    AuthResult,
    IntegrationHooks,
    hooks,
)
from adip.knowledge.services import (
    KnowledgeService as DefaultKnowledgeService,
)

__all__ = [
    # Enums
    "KnowledgeDomain",
    "DocumentType",
    "RetrievalType",
    "KnowledgeStatus",
    "KnowledgeLifecycleStatus",
    # Models
    "KnowledgeDocument",
    "KnowledgeChunk",
    "KnowledgeEmbedding",
    "KnowledgeMetadata",
    "KnowledgeProvenance",
    "KnowledgeIndex",
    "KnowledgeQuery",
    "KnowledgeResult",
    "KnowledgeContext",
    "KnowledgeHealth",
    "KnowledgeMetrics",
    "KnowledgeSession",
    "KnowledgeDecision",
    "KnowledgeConfidence",
    "ExplainabilityMetadata",
    # DTOs
    "KnowledgeRequestDTO",
    "KnowledgeResponseDTO",
    "KnowledgeSearchDTO",
    "KnowledgeContextDTO",
    # Events
    "EventVersion",
    "KnowledgeEvent",
    "KnowledgeCreated",
    "KnowledgeUpdated",
    "KnowledgeIndexed",
    "KnowledgeRetrieved",
    "KnowledgeArchived",
    "KnowledgeDeleted",
    # Exceptions
    "KnowledgeException",
    "KnowledgeValidationException",
    "RetrievalException",
    "IndexException",
    "EmbeddingException",
    # Interfaces
    "KnowledgeService",
    "KnowledgeManager",
    "KnowledgeCoordinator",
    "DocumentProcessor",
    "ChunkManager",
    "EmbeddingManager",
    "IndexManager",
    "Retriever",
    "Reranker",
    "ContextBuilder",
    "KnowledgeCache",
    # Default implementations
    "DefaultKnowledgeService",
    "DefaultKnowledgeManager",
    "DefaultKnowledgeCoordinator",
    "IntegrationHooks",
    "AuthResult",
    "hooks",
]
