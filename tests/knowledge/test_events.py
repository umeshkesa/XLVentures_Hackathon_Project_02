"""Tests for Knowledge Manager events."""

from __future__ import annotations

import uuid
from uuid import UUID

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
from adip.knowledge.enums import DocumentType, KnowledgeDomain, KnowledgeStatus


class TestEventVersion:
    def test_version_is_string(self) -> None:
        assert isinstance(EventVersion, str)
        assert EventVersion == "1.0.0"


class TestKnowledgeEvent:
    def test_base_event_fields(self) -> None:
        event = KnowledgeEvent(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        assert isinstance(event.event_id, UUID)
        assert event.document_type == DocumentType.PDF
        assert event.domain == KnowledgeDomain.SYSTEM
        assert event.correlation_id == ""
        assert event.payload == {}

    def test_custom_fields(self) -> None:
        event = KnowledgeEvent(
            document_id=uuid.uuid4(),
            document_type=DocumentType.DOCX,
            domain=KnowledgeDomain.ENERGY,
            correlation_id="corr-123",
            payload={"key": "value"},
        )
        assert event.domain == KnowledgeDomain.ENERGY
        assert event.correlation_id == "corr-123"
        assert event.payload == {"key": "value"}

    def test_timestamp_auto_set(self) -> None:
        event = KnowledgeEvent(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        assert event.timestamp is not None

    def test_inheritance(self) -> None:
        assert issubclass(KnowledgeCreated, KnowledgeEvent)
        assert issubclass(KnowledgeUpdated, KnowledgeEvent)
        assert issubclass(KnowledgeIndexed, KnowledgeEvent)
        assert issubclass(KnowledgeRetrieved, KnowledgeEvent)
        assert issubclass(KnowledgeArchived, KnowledgeEvent)
        assert issubclass(KnowledgeDeleted, KnowledgeEvent)


class TestKnowledgeCreated:
    def test_minimal(self) -> None:
        event = KnowledgeCreated(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        assert isinstance(event.event_id, UUID)
        assert event.document_type == DocumentType.PDF


class TestKnowledgeUpdated:
    def test_default_previous_version(self) -> None:
        event = KnowledgeUpdated(
            document_id=uuid.uuid4(),
            document_type=DocumentType.TXT,
        )
        assert event.previous_version == 0

    def test_custom_previous_version(self) -> None:
        event = KnowledgeUpdated(
            document_id=uuid.uuid4(),
            document_type=DocumentType.TXT,
            previous_version=3,
        )
        assert event.previous_version == 3


class TestKnowledgeIndexed:
    def test_defaults(self) -> None:
        event = KnowledgeIndexed(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        assert event.status == KnowledgeStatus.INDEXED
        assert event.chunk_count == 0

    def test_custom_values(self) -> None:
        event = KnowledgeIndexed(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
            status=KnowledgeStatus.FAILED,
            chunk_count=15,
        )
        assert event.status == KnowledgeStatus.FAILED
        assert event.chunk_count == 15


class TestKnowledgeRetrieved:
    def test_defaults(self) -> None:
        event = KnowledgeRetrieved(
            document_id=uuid.uuid4(),
            document_type=DocumentType.ARTICLE,
        )
        assert event.query_text == ""
        assert event.result_count == 0
        assert event.retrieval_type == ""

    def test_custom_values(self) -> None:
        event = KnowledgeRetrieved(
            document_id=uuid.uuid4(),
            document_type=DocumentType.ARTICLE,
            query_text="safety protocols",
            result_count=5,
            retrieval_type="HYBRID",
        )
        assert event.query_text == "safety protocols"
        assert event.result_count == 5
        assert event.retrieval_type == "HYBRID"


class TestKnowledgeArchived:
    def test_default_reason(self) -> None:
        event = KnowledgeArchived(
            document_id=uuid.uuid4(),
            document_type=DocumentType.SOP,
        )
        assert event.reason == ""

    def test_custom_reason(self) -> None:
        event = KnowledgeArchived(
            document_id=uuid.uuid4(),
            document_type=DocumentType.SOP,
            reason="Outdated version",
        )
        assert event.reason == "Outdated version"


class TestKnowledgeDeleted:
    def test_default_reason(self) -> None:
        event = KnowledgeDeleted(
            document_id=uuid.uuid4(),
            document_type=DocumentType.MANUAL,
        )
        assert event.reason == ""

    def test_custom_reason(self) -> None:
        event = KnowledgeDeleted(
            document_id=uuid.uuid4(),
            document_type=DocumentType.MANUAL,
            reason="User request",
        )
        assert event.reason == "User request"
