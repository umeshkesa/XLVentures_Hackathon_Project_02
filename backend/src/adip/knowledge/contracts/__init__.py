"""Knowledge Manager contracts — models, events, and exceptions."""

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
    KnowledgeChunk,
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeEmbedding,
    KnowledgeHealth,
    KnowledgeIndex,
    KnowledgeMetadata,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeResult,
)

__all__ = [
    # Models
    "KnowledgeDocument",
    "KnowledgeChunk",
    "KnowledgeEmbedding",
    "KnowledgeMetadata",
    "KnowledgeIndex",
    "KnowledgeQuery",
    "KnowledgeResult",
    "KnowledgeContext",
    "KnowledgeHealth",
    "KnowledgeMetrics",
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
]
