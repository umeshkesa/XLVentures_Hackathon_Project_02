"""Tests for Knowledge Manager exceptions."""

from __future__ import annotations

from adip.knowledge.contracts.exceptions import (
    EmbeddingException,
    IndexException,
    KnowledgeException,
    KnowledgeValidationException,
    RetrievalException,
)


class TestKnowledgeException:
    def test_base_exception(self) -> None:
        exc = KnowledgeException()
        assert exc.message == "Knowledge error"
        assert str(exc) == "Knowledge error"

    def test_custom_message(self) -> None:
        exc = KnowledgeException("Custom error")
        assert exc.message == "Custom error"

    def test_is_exception(self) -> None:
        assert issubclass(KnowledgeException, Exception)


class TestKnowledgeValidationException:
    def test_default_message(self) -> None:
        exc = KnowledgeValidationException()
        assert exc.message == "Knowledge validation error"

    def test_custom_message(self) -> None:
        exc = KnowledgeValidationException("Invalid domain")
        assert exc.message == "Invalid domain"

    def test_inheritance(self) -> None:
        assert issubclass(KnowledgeValidationException, KnowledgeException)


class TestRetrievalException:
    def test_default_message(self) -> None:
        exc = RetrievalException()
        assert exc.message == "Knowledge retrieval failed"
        assert exc.query == ""

    def test_with_query(self) -> None:
        exc = RetrievalException(query="safety protocol")
        assert exc.query == "safety protocol"
        assert "safety protocol" in exc.message

    def test_custom_message(self) -> None:
        exc = RetrievalException(query="test", message="Custom retrieval error")
        assert exc.message == "Custom retrieval error"
        assert exc.query == "test"

    def test_inheritance(self) -> None:
        assert issubclass(RetrievalException, KnowledgeException)


class TestIndexException:
    def test_default_message(self) -> None:
        exc = IndexException()
        assert exc.message == "Indexing failed"
        assert exc.document_id == ""

    def test_with_document_id(self) -> None:
        exc = IndexException(document_id="doc-123")
        assert exc.document_id == "doc-123"
        assert "doc-123" in exc.message

    def test_custom_message(self) -> None:
        exc = IndexException(document_id="doc-1", message="Custom index error")
        assert exc.message == "Custom index error"

    def test_inheritance(self) -> None:
        assert issubclass(IndexException, KnowledgeException)


class TestEmbeddingException:
    def test_default_message(self) -> None:
        exc = EmbeddingException()
        assert exc.message == "Embedding generation failed"
        assert exc.chunk_id == ""

    def test_with_chunk_id(self) -> None:
        exc = EmbeddingException(chunk_id="chunk-456")
        assert exc.chunk_id == "chunk-456"
        assert "chunk-456" in exc.message

    def test_custom_message(self) -> None:
        exc = EmbeddingException(chunk_id="c1", message="Custom embedding error")
        assert exc.message == "Custom embedding error"

    def test_inheritance(self) -> None:
        assert issubclass(EmbeddingException, KnowledgeException)
