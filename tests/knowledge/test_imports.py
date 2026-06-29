"""Tests for Knowledge Manager package imports and re-exports."""

from __future__ import annotations


class TestTopLevelImports:
    def test_all_imports(self) -> None:
        from adip.knowledge import (  # noqa: F811
            KnowledgeCreated,
            KnowledgeDocument,
            KnowledgeDomain,
            KnowledgeException,
            KnowledgeRequestDTO,
            KnowledgeService,
        )
        # Verify a few key names
        assert KnowledgeDomain is not None
        assert KnowledgeDocument is not None
        assert KnowledgeService is not None
        assert KnowledgeCreated is not None
        assert KnowledgeException is not None
        assert KnowledgeRequestDTO is not None


class TestContractsImports:
    def test_all_imports(self) -> None:
        from adip.knowledge.contracts import (  # noqa: F811
            KnowledgeDocument,
            KnowledgeHealth,
        )
        assert KnowledgeDocument is not None
        assert KnowledgeHealth is not None


class TestModuleContents:
    def test_enums_have_all_values(self) -> None:
        from adip.knowledge.enums import (
            DocumentType,
            KnowledgeDomain,
            KnowledgeStatus,
            RetrievalType,
        )
        assert len(KnowledgeDomain) == 13
        assert len(DocumentType) == 12
        assert len(RetrievalType) == 4
        assert len(KnowledgeStatus) == 6

    def test_events_have_all_types(self) -> None:
        from adip.knowledge.contracts.events import (
            EventVersion,
            KnowledgeCreated,
            KnowledgeDeleted,
            KnowledgeEvent,
        )
        assert EventVersion is not None
        assert KnowledgeCreated is not None
        assert KnowledgeDeleted is not None
        assert KnowledgeEvent is not None

    def test_exceptions_have_all_types(self) -> None:
        from adip.knowledge.contracts.exceptions import (
            EmbeddingException,
            KnowledgeException,
            RetrievalException,
        )
        assert KnowledgeException is not None
        assert RetrievalException is not None
        assert EmbeddingException is not None

    def test_interfaces_have_all_types(self) -> None:
        from adip.knowledge.interfaces import (
            KnowledgeCache,
            KnowledgeCoordinator,
            KnowledgeService,
        )
        assert KnowledgeService is not None
        assert KnowledgeCoordinator is not None
        assert KnowledgeCache is not None

    def test_dtos_have_all_types(self) -> None:
        from adip.knowledge.dtos import (
            KnowledgeContextDTO,
            KnowledgeRequestDTO,
        )
        assert KnowledgeRequestDTO is not None
        assert KnowledgeContextDTO is not None

    def test_all_names_in_all(self) -> None:
        from adip.knowledge import __all__ as top_all
        expected = {
            "KnowledgeDomain", "DocumentType", "RetrievalType", "KnowledgeStatus",
            "KnowledgeLifecycleStatus",
            "KnowledgeDocument", "KnowledgeChunk", "KnowledgeEmbedding",
            "KnowledgeMetadata", "KnowledgeProvenance", "KnowledgeIndex", "KnowledgeQuery",
            "KnowledgeResult", "KnowledgeContext", "KnowledgeHealth", "KnowledgeMetrics",
            "KnowledgeSession", "KnowledgeDecision", "KnowledgeConfidence",
            "ExplainabilityMetadata",
            "KnowledgeRequestDTO", "KnowledgeResponseDTO", "KnowledgeSearchDTO",
            "KnowledgeContextDTO",
            "EventVersion", "KnowledgeEvent", "KnowledgeCreated", "KnowledgeUpdated",
            "KnowledgeIndexed", "KnowledgeRetrieved", "KnowledgeArchived", "KnowledgeDeleted",
            "KnowledgeException", "KnowledgeValidationException", "RetrievalException",
            "IndexException", "EmbeddingException",
            "KnowledgeService", "KnowledgeManager", "KnowledgeCoordinator",
            "DocumentProcessor", "ChunkManager", "EmbeddingManager", "IndexManager",
            "Retriever", "Reranker", "ContextBuilder", "KnowledgeCache",
            "DefaultKnowledgeService", "DefaultKnowledgeManager",
            "DefaultKnowledgeCoordinator",
            "IntegrationHooks", "AuthResult", "hooks",
        }
        assert set(top_all) == expected
