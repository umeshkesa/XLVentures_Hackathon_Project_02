"""Evidence repository — sync CRUD against the evidence table."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from adip.evidence.contracts.models import Evidence
from adip.models.evidence import EvidenceRecord


def _evidence_to_record(evidence: Evidence) -> dict[str, Any]:
    """Convert an Evidence domain model to ORM record kwargs."""
    return {
        "entity_id": evidence.evidence_id,
        "evidence_type": evidence.evidence_type.value if hasattr(evidence.evidence_type, "value") else str(evidence.evidence_type),
        "domain": evidence.domain.value if hasattr(evidence.domain, "value") else str(evidence.domain),
        "status": evidence.status.value if hasattr(evidence.status, "value") else str(evidence.status),
        "source": evidence.source.model_dump() if hasattr(evidence.source, "model_dump") else {},
        "metadata_": evidence.metadata.model_dump() if hasattr(evidence.metadata, "model_dump") else {},
        "provenance": evidence.provenance.model_dump() if hasattr(evidence.provenance, "model_dump") else {},
        "quality": evidence.quality.model_dump() if hasattr(evidence.quality, "model_dump") else {},
        "payload": evidence.payload or {},
        "evidence_timestamp": evidence.timestamp,
        "serialized": evidence.model_dump() if hasattr(evidence, "model_dump") else None,
    }


def save_evidence(session: Session, evidence: Evidence) -> None:
    """Upsert an Evidence item to the database."""
    kwargs = _evidence_to_record(evidence)
    stmt = select(EvidenceRecord).where(
        EvidenceRecord.entity_id == evidence.evidence_id
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
    else:
        session.add(EvidenceRecord(**kwargs))
    session.flush()


def get_evidence(session: Session, entity_id: str) -> Evidence | None:
    """Retrieve an Evidence domain model by its UUID string."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return None
    stmt = select(EvidenceRecord).where(EvidenceRecord.entity_id == uid)
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return None
    if record.serialized:
        return Evidence(**record.serialized)
    return None


def get_all_evidence(session: Session) -> list[Evidence]:
    """Return all stored Evidence domain models."""
    records = session.execute(select(EvidenceRecord)).scalars().all()
    result: list[Evidence] = []
    for r in records:
        if r.serialized:
            result.append(Evidence(**r.serialized))
    return result


def count_evidence(session: Session) -> int:
    """Return the total number of evidence records."""
    return session.execute(select(EvidenceRecord)).scalar() or 0


def delete_evidence(session: Session, entity_id: str) -> bool:
    """Delete an evidence record by its entity_id. Returns True if deleted."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return False
    stmt = select(EvidenceRecord).where(EvidenceRecord.entity_id == uid)
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    session.delete(record)
    session.flush()
    return True
