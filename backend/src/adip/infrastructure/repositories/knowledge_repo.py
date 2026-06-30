"""Knowledge repository — sync CRUD against the knowledge_documents table."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from adip.knowledge.contracts.models import KnowledgeDocument
from adip.models.knowledge import KnowledgeDocumentRecord


def _document_to_record(doc: KnowledgeDocument) -> dict[str, Any]:
    """Convert a KnowledgeDocument domain model to ORM record kwargs."""
    return {
        "entity_id": doc.document_id,
        "document_type": doc.document_type.value if hasattr(doc.document_type, "value") else str(doc.document_type),
        "domain": doc.domain.value if hasattr(doc.domain, "value") else str(doc.domain),
        "title": doc.title,
        "source": doc.source,
        "content": doc.content,
        "status": doc.status.value if hasattr(doc.status, "value") else str(doc.status),
        "metadata_": doc.metadata.model_dump() if hasattr(doc.metadata, "model_dump") else {},
        "tags": list(doc.tags) if doc.tags else [],
        "owner_id": doc.owner_id,
        "namespace": doc.namespace,
        "version": doc.version,
        "serialized": doc.model_dump() if hasattr(doc, "model_dump") else None,
    }


def save_document(session: Session, doc: KnowledgeDocument) -> None:
    """Upsert a KnowledgeDocument to the database."""
    kwargs = _document_to_record(doc)
    stmt = select(KnowledgeDocumentRecord).where(
        KnowledgeDocumentRecord.entity_id == doc.document_id
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
    else:
        session.add(KnowledgeDocumentRecord(**kwargs))
    session.flush()


def get_document(session: Session, entity_id: str) -> KnowledgeDocument | None:
    """Retrieve a KnowledgeDocument by its UUID string."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return None
    stmt = select(KnowledgeDocumentRecord).where(
        KnowledgeDocumentRecord.entity_id == uid
    )
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return None
    if record.serialized:
        return KnowledgeDocument(**record.serialized)
    return None


def get_all_documents(session: Session) -> list[KnowledgeDocument]:
    """Return all stored KnowledgeDocuments."""
    records = session.execute(select(KnowledgeDocumentRecord)).scalars().all()
    result: list[KnowledgeDocument] = []
    for r in records:
        if r.serialized:
            result.append(KnowledgeDocument(**r.serialized))
    return result


def count_documents(session: Session) -> int:
    """Return total document count."""
    return session.execute(select(KnowledgeDocumentRecord)).scalar() or 0


def delete_document(session: Session, entity_id: str) -> bool:
    """Delete a document by entity_id."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return False
    stmt = select(KnowledgeDocumentRecord).where(
        KnowledgeDocumentRecord.entity_id == uid
    )
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    session.delete(record)
    session.flush()
    return True
