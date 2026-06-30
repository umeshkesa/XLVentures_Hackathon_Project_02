"""Recommendation repository — sync CRUD against the recommendations table."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from adip.models.recommendation import RecommendationRecord


def save_recommendation_dict(session: Session, **kwargs: Any) -> None:
    """Upsert a recommendation using raw ORM kwargs."""
    stmt = select(RecommendationRecord).where(
        RecommendationRecord.entity_id == kwargs["entity_id"]
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
    else:
        session.add(RecommendationRecord(**kwargs))
    session.flush()


def get_recommendation(session: Session, entity_id: str) -> dict[str, Any] | None:
    """Retrieve a recommendation record by entity_id."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return None
    stmt = select(RecommendationRecord).where(
        RecommendationRecord.entity_id == uid
    )
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return None
    return _record_to_dict(record)


def get_all_recommendations(session: Session) -> list[dict[str, Any]]:
    """Return all stored recommendations as dicts."""
    records = session.execute(select(RecommendationRecord)).scalars().all()
    return [_record_to_dict(r) for r in records]


def count_recommendations(session: Session) -> int:
    """Return total recommendation count."""
    return session.execute(select(RecommendationRecord)).scalar() or 0


def delete_recommendation(session: Session, entity_id: str) -> bool:
    """Delete a recommendation by entity_id."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return False
    stmt = select(RecommendationRecord).where(
        RecommendationRecord.entity_id == uid
    )
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    session.delete(record)
    session.flush()
    return True


def _record_to_dict(r: RecommendationRecord) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "entity_id": str(r.entity_id),
        "status": r.status,
        "priority": r.priority,
        "recommendation_type": r.recommendation_type,
        "source": r.source,
        "title": r.title,
        "description": r.description,
        "domain": r.domain,
        "confidence": r.confidence,
        "estimated_cost": r.estimated_cost,
        "estimated_savings": r.estimated_savings,
        "action": r.action,
        "reasoning_session_id": r.reasoning_session_id,
        "serialized": r.serialized,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }
