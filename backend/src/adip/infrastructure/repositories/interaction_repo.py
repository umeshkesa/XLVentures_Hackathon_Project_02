"""Interaction repository — sync CRUD against the interactions table."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from adip.models.interaction import InteractionRecord


def save_interaction(session: Session, **kwargs: Any) -> None:
    """Upsert an interaction to the database."""
    stmt = select(InteractionRecord).where(
        InteractionRecord.entity_id == kwargs["entity_id"]
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
    else:
        session.add(InteractionRecord(**kwargs))
    session.flush()


def get_interaction(session: Session, entity_id: str) -> dict[str, Any] | None:
    """Retrieve an interaction by entity_id."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return None
    stmt = select(InteractionRecord).where(
        InteractionRecord.entity_id == uid
    )
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return None
    return _record_to_dict(record)


def get_all_interactions(session: Session) -> list[dict[str, Any]]:
    """Return all stored interactions as dicts."""
    records = session.execute(select(InteractionRecord)).scalars().all()
    return [_record_to_dict(r) for r in records]


def count_interactions(session: Session) -> int:
    """Return total interaction count."""
    return session.execute(select(InteractionRecord)).scalar() or 0


def delete_interaction(session: Session, entity_id: str) -> bool:
    """Delete an interaction by entity_id."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return False
    stmt = select(InteractionRecord).where(
        InteractionRecord.entity_id == uid
    )
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    session.delete(record)
    session.flush()
    return True


def _record_to_dict(r: InteractionRecord) -> dict[str, Any]:
    return {
        "id": str(r.entity_id),
        "type": r.interaction_type,
        "subject": r.title,
        "content": r.description,
        "status": r.status,
        "priority": r.priority,
        "date": r.interaction_timestamp.isoformat() if r.interaction_timestamp else r.created_at.isoformat() if r.created_at else None,
        "customerId": r.customer_id,
        "customerName": r.customer_name,
        "relatedEvidence": r.related_evidence_ids or [],
        "relatedRecommendations": r.related_recommendation_ids or [],
        "agent": "",
        "relatedAssets": [],
        "relatedPlannerRun": None,
        "attachments": [],
    }
