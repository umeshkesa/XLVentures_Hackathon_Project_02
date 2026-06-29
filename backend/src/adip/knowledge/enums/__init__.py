"""Enumerations for the Knowledge Manager.

Defines all enum types used across knowledge domain models, events,
interfaces, and DTOs.
"""

from __future__ import annotations

from enum import StrEnum


class KnowledgeDomain(StrEnum):
    """Enterprise knowledge domains.

    Values represent the ADIP platform knowledge domains that
    documents and knowledge can belong to.

    Future-ready domains (HEALTHCARE, FINANCE, MANUFACTURING) are
    pre-defined for extensibility without breaking changes.
    """

    SYSTEM = "SYSTEM"
    ENERGY = "ENERGY"
    OPERATIONS = "OPERATIONS"
    MAINTENANCE = "MAINTENANCE"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    CUSTOMER = "CUSTOMER"
    PRODUCT = "PRODUCT"
    PLAYBOOK = "PLAYBOOK"
    POLICY = "POLICY"
    HEALTHCARE = "HEALTHCARE"
    FINANCE = "FINANCE"
    MANUFACTURING = "MANUFACTURING"


class DocumentType(StrEnum):
    """Supported document types for ingestion.

    Covers common enterprise document formats including structured
    data (PDF, DOCX, TXT, CSV, JSON), communications (EMAIL,
    CRM_NOTE, MEETING_NOTE), and operational knowledge (PLAYBOOK,
    SOP, MANUAL, ARTICLE).
    """

    PDF = "PDF"
    DOCX = "DOCX"
    TXT = "TXT"
    CSV = "CSV"
    JSON = "JSON"
    EMAIL = "EMAIL"
    CRM_NOTE = "CRM_NOTE"
    MEETING_NOTE = "MEETING_NOTE"
    PLAYBOOK = "PLAYBOOK"
    SOP = "SOP"
    MANUAL = "MANUAL"
    ARTICLE = "ARTICLE"


class RetrievalType(StrEnum):
    """Supported knowledge retrieval strategies.

    VECTOR — embedding-based semantic search.
    KEYWORD — traditional keyword/full-text search.
    METADATA — filter-only metadata search.
    HYBRID — combined vector and keyword retrieval.
    """

    VECTOR = "VECTOR"
    KEYWORD = "KEYWORD"
    METADATA = "METADATA"
    HYBRID = "HYBRID"


class KnowledgeStatus(StrEnum):
    """Lifecycle status of a knowledge document.

    PENDING — ingested but not yet processed.
    PROCESSING — being chunked and embedded.
    INDEXED — fully processed and available for retrieval.
    FAILED — processing failed.
    ARCHIVED — removed from active retrieval.
    DELETED — permanently removed.
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class KnowledgeLifecycleStatus(StrEnum):
    """Lifecycle status for knowledge document versioning and review.

    DRAFT — initial creation, not yet reviewed.
    UNDER_REVIEW — submitted for review.
    APPROVED — reviewed and approved.
    PUBLISHED — published and available for retrieval.
    DEPRECATED — superseded by a newer version.
    ARCHIVED — no longer active but retained for audit.
    """

    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
