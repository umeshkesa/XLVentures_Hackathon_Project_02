"""Tests for Knowledge Manager enums."""

from __future__ import annotations

from enum import StrEnum

from adip.knowledge.enums import DocumentType, KnowledgeDomain, KnowledgeStatus, RetrievalType


class TestKnowledgeDomain:
    def test_values(self) -> None:
        assert KnowledgeDomain.SYSTEM.value == "SYSTEM"
        assert KnowledgeDomain.ENERGY.value == "ENERGY"
        assert KnowledgeDomain.OPERATIONS.value == "OPERATIONS"
        assert KnowledgeDomain.MAINTENANCE.value == "MAINTENANCE"
        assert KnowledgeDomain.SAFETY.value == "SAFETY"
        assert KnowledgeDomain.COMPLIANCE.value == "COMPLIANCE"
        assert KnowledgeDomain.CUSTOMER.value == "CUSTOMER"
        assert KnowledgeDomain.PRODUCT.value == "PRODUCT"
        assert KnowledgeDomain.PLAYBOOK.value == "PLAYBOOK"
        assert KnowledgeDomain.POLICY.value == "POLICY"

    def test_future_ready_domains(self) -> None:
        assert KnowledgeDomain.HEALTHCARE.value == "HEALTHCARE"
        assert KnowledgeDomain.FINANCE.value == "FINANCE"
        assert KnowledgeDomain.MANUFACTURING.value == "MANUFACTURING"

    def test_is_str_enum(self) -> None:
        assert issubclass(KnowledgeDomain, StrEnum)

    def test_domain_membership(self) -> None:
        domains = {d.value for d in KnowledgeDomain}
        expected = {
            "SYSTEM", "ENERGY", "OPERATIONS", "MAINTENANCE",
            "SAFETY", "COMPLIANCE", "CUSTOMER", "PRODUCT",
            "PLAYBOOK", "POLICY", "HEALTHCARE", "FINANCE",
            "MANUFACTURING",
        }
        assert domains == expected

    def test_from_string(self) -> None:
        assert KnowledgeDomain("ENERGY") == KnowledgeDomain.ENERGY
        assert KnowledgeDomain("SAFETY") == KnowledgeDomain.SAFETY


class TestDocumentType:
    def test_values(self) -> None:
        assert DocumentType.PDF.value == "PDF"
        assert DocumentType.DOCX.value == "DOCX"
        assert DocumentType.TXT.value == "TXT"
        assert DocumentType.CSV.value == "CSV"
        assert DocumentType.JSON.value == "JSON"
        assert DocumentType.EMAIL.value == "EMAIL"
        assert DocumentType.CRM_NOTE.value == "CRM_NOTE"
        assert DocumentType.MEETING_NOTE.value == "MEETING_NOTE"
        assert DocumentType.PLAYBOOK.value == "PLAYBOOK"
        assert DocumentType.SOP.value == "SOP"
        assert DocumentType.MANUAL.value == "MANUAL"
        assert DocumentType.ARTICLE.value == "ARTICLE"

    def test_is_str_enum(self) -> None:
        assert issubclass(DocumentType, StrEnum)

    def test_all_types_present(self) -> None:
        types = {t.value for t in DocumentType}
        expected = {
            "PDF", "DOCX", "TXT", "CSV", "JSON",
            "EMAIL", "CRM_NOTE", "MEETING_NOTE",
            "PLAYBOOK", "SOP", "MANUAL", "ARTICLE",
        }
        assert types == expected


class TestRetrievalType:
    def test_values(self) -> None:
        assert RetrievalType.VECTOR.value == "VECTOR"
        assert RetrievalType.KEYWORD.value == "KEYWORD"
        assert RetrievalType.METADATA.value == "METADATA"
        assert RetrievalType.HYBRID.value == "HYBRID"

    def test_is_str_enum(self) -> None:
        assert issubclass(RetrievalType, StrEnum)

    def test_all_types_present(self) -> None:
        types = {t.value for t in RetrievalType}
        expected = {"VECTOR", "KEYWORD", "METADATA", "HYBRID"}
        assert types == expected


class TestKnowledgeStatus:
    def test_values(self) -> None:
        assert KnowledgeStatus.PENDING.value == "PENDING"
        assert KnowledgeStatus.PROCESSING.value == "PROCESSING"
        assert KnowledgeStatus.INDEXED.value == "INDEXED"
        assert KnowledgeStatus.FAILED.value == "FAILED"
        assert KnowledgeStatus.ARCHIVED.value == "ARCHIVED"
        assert KnowledgeStatus.DELETED.value == "DELETED"

    def test_is_str_enum(self) -> None:
        assert issubclass(KnowledgeStatus, StrEnum)

    def test_all_statuses_present(self) -> None:
        statuses = {s.value for s in KnowledgeStatus}
        expected = {"PENDING", "PROCESSING", "INDEXED", "FAILED", "ARCHIVED", "DELETED"}
        assert statuses == expected
