"""Tests for Knowledge Manager DTOs."""

from __future__ import annotations

import uuid
from uuid import UUID

from adip.knowledge.dtos import (
    KnowledgeContextDTO,
    KnowledgeRequestDTO,
    KnowledgeResponseDTO,
    KnowledgeSearchDTO,
)
from adip.knowledge.enums import DocumentType, KnowledgeDomain, RetrievalType


class TestKnowledgeRequestDTO:
    def test_minimal(self) -> None:
        dto = KnowledgeRequestDTO(document_type=DocumentType.PDF)
        assert dto.title == ""
        assert dto.source == ""
        assert dto.content == ""
        assert dto.document_type == DocumentType.PDF
        assert dto.domain == KnowledgeDomain.SYSTEM
        assert dto.owner_id == ""
        assert dto.namespace == "default"
        assert dto.tags == []
        assert dto.metadata == {}

    def test_custom_values(self) -> None:
        dto = KnowledgeRequestDTO(
            title="Safety Report",
            source="upload.pdf",
            content="Full text...",
            document_type=DocumentType.PDF,
            domain=KnowledgeDomain.SAFETY,
            owner_id="user-1",
            tags=["safety"],
            metadata={"department": "EHS"},
        )
        assert dto.title == "Safety Report"
        assert dto.domain == KnowledgeDomain.SAFETY
        assert dto.metadata["department"] == "EHS"


class TestKnowledgeResponseDTO:
    def test_minimal(self) -> None:
        dto = KnowledgeResponseDTO(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        assert isinstance(dto.document_id, UUID)
        assert dto.document_type == DocumentType.PDF
        assert dto.status == "PENDING"
        assert dto.version == 1
        assert dto.title == ""

    def test_custom_values(self) -> None:
        dto = KnowledgeResponseDTO(
            document_id=uuid.uuid4(),
            title="Report",
            document_type=DocumentType.DOCX,
            domain=KnowledgeDomain.ENERGY,
            status="INDEXED",
            version=3,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-02T00:00:00Z",
        )
        assert dto.title == "Report"
        assert dto.domain == KnowledgeDomain.ENERGY
        assert dto.status == "INDEXED"
        assert dto.version == 3


class TestKnowledgeSearchDTO:
    def test_defaults(self) -> None:
        dto = KnowledgeSearchDTO()
        assert dto.query_text == ""
        assert dto.retrieval_type == RetrievalType.HYBRID
        assert dto.limit == 10
        assert dto.offset == 0
        assert dto.min_score == 0.0
        assert dto.domains == []
        assert dto.document_types == []

    def test_custom_values(self) -> None:
        dto = KnowledgeSearchDTO(
            query_text="safety protocols",
            retrieval_type=RetrievalType.VECTOR,
            domains=[KnowledgeDomain.SAFETY],
            document_types=[DocumentType.PDF],
            limit=5,
            min_score=0.7,
        )
        assert dto.query_text == "safety protocols"
        assert dto.retrieval_type == RetrievalType.VECTOR
        assert KnowledgeDomain.SAFETY in dto.domains
        assert dto.limit == 5
        assert dto.min_score == 0.7

    def test_limit_bounds(self) -> None:
        dto = KnowledgeSearchDTO(limit=1)
        assert dto.limit == 1
        dto = KnowledgeSearchDTO(limit=100)
        assert dto.limit == 100


class TestKnowledgeContextDTO:
    def test_defaults(self) -> None:
        dto = KnowledgeContextDTO()
        assert isinstance(dto.context_id, UUID)
        assert dto.query_text == ""
        assert dto.total_results == 0
        assert dto.domains == []
        assert dto.document_types == []
        assert dto.results == []
        assert dto.metadata == {}

    def test_custom_values(self) -> None:
        dto = KnowledgeContextDTO(
            query_text="safety protocols",
            total_results=5,
            domains=["SAFETY", "COMPLIANCE"],
            document_types=["PDF"],
            results=[{"chunk_id": "c1", "score": 0.95}],
            metadata={"timing_ms": 150},
        )
        assert dto.query_text == "safety protocols"
        assert dto.total_results == 5
        assert "SAFETY" in dto.domains
        assert dto.results[0]["score"] == 0.95
