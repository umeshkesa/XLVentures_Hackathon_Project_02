"""MemorySession — represents one logical memory transaction.

Every interaction with MemoryService creates a MemorySession that
tracks operations, records, policy, and statistics for audit and
observability.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.memory.enums import MemoryDomain


class MemorySession(BaseModel):
    """A logical memory transaction — one interaction with MemoryService.

    Tracks all operations performed within the session along with
    statistics for audit, metrics, and explainability.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this session",
    )
    owner_id: str = Field(
        default="",
        description="The owner or caller that initiated this session",
    )
    memory_domain: MemoryDomain = Field(
        default=MemoryDomain.SYSTEM,
        description="The domain this session is scoped to",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session was completed",
    )
    operations: list[str] = Field(
        default_factory=list,
        description="Ordered list of operation names performed",
    )
    created_records: list[str] = Field(
        default_factory=list,
        description="Memory IDs of records created in this session",
    )
    updated_records: list[str] = Field(
        default_factory=list,
        description="Memory IDs of records updated in this session",
    )
    deleted_records: list[str] = Field(
        default_factory=list,
        description="Memory IDs of records deleted in this session",
    )
    policy_used: str = Field(
        default="",
        description="Name of the policy applied during this session",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregated session statistics",
    )

    def complete(self) -> None:
        """Mark the session as completed."""
        self.completed_at = datetime.now(UTC)

    def record_operation(self, operation: str, memory_id: str | None = None) -> None:
        """Record an operation and optionally associate a memory ID."""
        self.operations.append(operation)
        if memory_id and memory_id not in self.created_records + self.updated_records + self.deleted_records:
            if operation in ("create", "store"):
                self.created_records.append(memory_id)
            elif operation in ("update",):
                self.updated_records.append(memory_id)
            elif operation in ("delete", "remove"):
                self.deleted_records.append(memory_id)
