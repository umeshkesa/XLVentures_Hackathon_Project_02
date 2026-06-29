"""Tests for Knowledge Manager interfaces."""

from __future__ import annotations

import abc

import pytest

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


class TestInterfacesAreAbstract:
    def test_knowledge_service_is_abstract(self) -> None:
        assert issubclass(KnowledgeService, abc.ABC)

    def test_knowledge_manager_is_abstract(self) -> None:
        assert issubclass(KnowledgeManager, abc.ABC)

    def test_knowledge_coordinator_is_abstract(self) -> None:
        assert issubclass(KnowledgeCoordinator, abc.ABC)

    def test_document_processor_is_abstract(self) -> None:
        assert issubclass(DocumentProcessor, abc.ABC)

    def test_chunk_manager_is_abstract(self) -> None:
        assert issubclass(ChunkManager, abc.ABC)

    def test_embedding_manager_is_abstract(self) -> None:
        assert issubclass(EmbeddingManager, abc.ABC)

    def test_index_manager_is_abstract(self) -> None:
        assert issubclass(IndexManager, abc.ABC)

    def test_retriever_is_abstract(self) -> None:
        assert issubclass(Retriever, abc.ABC)

    def test_reranker_is_abstract(self) -> None:
        assert issubclass(Reranker, abc.ABC)

    def test_context_builder_is_abstract(self) -> None:
        assert issubclass(ContextBuilder, abc.ABC)

    def test_knowledge_cache_is_abstract(self) -> None:
        assert issubclass(KnowledgeCache, abc.ABC)


class TestInterfacesCannotBeInstantiated:
    def test_knowledge_service(self) -> None:
        with pytest.raises(TypeError):
            KnowledgeService()  # type: ignore[abstract]

    def test_knowledge_manager(self) -> None:
        with pytest.raises(TypeError):
            KnowledgeManager()  # type: ignore[abstract]

    def test_knowledge_coordinator(self) -> None:
        with pytest.raises(TypeError):
            KnowledgeCoordinator()  # type: ignore[abstract]

    def test_document_processor(self) -> None:
        with pytest.raises(TypeError):
            DocumentProcessor()  # type: ignore[abstract]

    def test_chunk_manager(self) -> None:
        with pytest.raises(TypeError):
            ChunkManager()  # type: ignore[abstract]

    def test_embedding_manager(self) -> None:
        with pytest.raises(TypeError):
            EmbeddingManager()  # type: ignore[abstract]

    def test_index_manager(self) -> None:
        with pytest.raises(TypeError):
            IndexManager()  # type: ignore[abstract]

    def test_retriever(self) -> None:
        with pytest.raises(TypeError):
            Retriever()  # type: ignore[abstract]

    def test_reranker(self) -> None:
        with pytest.raises(TypeError):
            Reranker()  # type: ignore[abstract]

    def test_context_builder(self) -> None:
        with pytest.raises(TypeError):
            ContextBuilder()  # type: ignore[abstract]

    def test_knowledge_cache(self) -> None:
        with pytest.raises(TypeError):
            KnowledgeCache()  # type: ignore[abstract]
