"""Rule repository — sync CRUD against the rules table."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from adip.models.rule import RuleRecord
from adip.rules.contracts.models import Rule, RuleSet


def _rule_to_record(rule: Rule) -> dict[str, Any]:
    """Convert a Rule domain model to ORM record kwargs."""
    return {
        "entity_id": rule.rule_id,
        "name": rule.name,
        "description": rule.description,
        "domain": rule.domain.value if hasattr(rule.domain, "value") else str(rule.domain),
        "rule_type": rule.rule_type.value if hasattr(rule.rule_type, "value") else str(rule.rule_type),
        "status": rule.status.value if hasattr(rule.status, "value") else str(rule.status),
        "conditions": [c.model_dump() if hasattr(c, "model_dump") else {} for c in (rule.conditions or [])],
        "actions": [a.model_dump() if hasattr(a, "model_dump") else {} for a in (rule.actions or [])],
        "priority": rule.priority,
        "version": rule.version,
        "tags": list(rule.tags) if rule.tags else [],
        "owner_id": rule.owner_id,
        "namespace": rule.namespace,
        "category": rule.category if hasattr(rule, "category") else "",
        "scope": rule.scope if hasattr(rule, "scope") else "",
        "serialized": rule.model_dump() if hasattr(rule, "model_dump") else None,
    }


def save_rule(session: Session, rule: Rule) -> None:
    """Upsert a Rule to the database."""
    kwargs = _rule_to_record(rule)
    stmt = select(RuleRecord).where(RuleRecord.entity_id == rule.rule_id)
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
    else:
        session.add(RuleRecord(**kwargs))
    session.flush()


def get_rule(session: Session, entity_id: str) -> Rule | None:
    """Retrieve a Rule by its UUID string."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return None
    stmt = select(RuleRecord).where(RuleRecord.entity_id == uid)
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return None
    if record.serialized:
        return Rule(**record.serialized)
    return None


def get_all_rules(session: Session) -> list[Rule]:
    """Return all stored Rules."""
    records = session.execute(select(RuleRecord)).scalars().all()
    result: list[Rule] = []
    for r in records:
        if r.serialized:
            result.append(Rule(**r.serialized))
    return result


def count_rules(session: Session) -> int:
    """Return total rule count."""
    return session.execute(select(RuleRecord)).scalar() or 0


def delete_rule(session: Session, entity_id: str) -> bool:
    """Delete a rule by entity_id."""
    import uuid
    try:
        uid = uuid.UUID(entity_id)
    except ValueError:
        return False
    stmt = select(RuleRecord).where(RuleRecord.entity_id == uid)
    record = session.execute(stmt).scalar_one_or_none()
    if record is None:
        return False
    session.delete(record)
    session.flush()
    return True
