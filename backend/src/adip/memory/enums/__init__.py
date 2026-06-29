"""Memory Manager enums."""

from __future__ import annotations

from enum import StrEnum


class MemoryDomain(StrEnum):
    """Domains within the ADIP platform that own memory records.

    The domain indicates which platform module created or owns a
    memory record, enabling domain-aware orchestration, routing,
    policy, metrics, and explainability.
    """

    SYSTEM = "SYSTEM"
    PLANNER = "PLANNER"
    WORKFLOW = "WORKFLOW"
    KNOWLEDGE = "KNOWLEDGE"
    RULES = "RULES"
    EVIDENCE = "EVIDENCE"
    REASONING = "REASONING"
    RECOMMENDATION = "RECOMMENDATION"
    EXPLAINABILITY = "EXPLAINABILITY"
    ACTION = "ACTION"
    ENERGY = "ENERGY"
    CUSTOMER = "CUSTOMER"
    PLUGIN = "PLUGIN"

    HEALTHCARE = "HEALTHCARE"
    FINANCE = "FINANCE"
    MANUFACTURING = "MANUFACTURING"


class MemoryType(StrEnum):
    """Categories of memory stored by the Memory Manager."""
    SESSION = "SESSION"
    CONVERSATION = "CONVERSATION"
    WORKFLOW = "WORKFLOW"
    PLANNING = "PLANNING"
    RECOMMENDATION = "RECOMMENDATION"
    LEARNING = "LEARNING"
    USER = "USER"
    CACHE = "CACHE"


class MemoryTier(StrEnum):
    """Storage tier a memory record resides in."""
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"


class MemoryOperation(StrEnum):
    """Operations that can be performed on a memory record."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SEARCH = "SEARCH"
    ARCHIVE = "ARCHIVE"


class RetentionPolicy(StrEnum):
    """How long a memory record should be retained."""
    TEMPORARY = "TEMPORARY"
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    PERMANENT = "PERMANENT"


class MemoryLifecycleStatus(StrEnum):
    """Lifecycle states of a memory record.

    Every MemoryRecord maintains lifecycle state through a
    deterministic flow: CREATED → ACTIVE ↔ UPDATED → ARCHIVED → DELETED.
    Direct deletion (ACTIVE/UPDATED → DELETED) is also allowed.
    EXPIRED is a terminal state that may be reached from ACTIVE or UPDATED.
    """
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    UPDATED = "UPDATED"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"
    DELETED = "DELETED"
