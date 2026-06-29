"""MemoryTransaction — preparation for distributed memory transactions.

Provides the transaction abstraction without rollback implementation.
Future phases will add real distributed transaction support.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field


class MemoryTransaction(BaseModel):
    """Represents a memory transaction spanning multiple operations.

    Preparation only — no rollback implementation.  Future phases
    will add distributed transaction support with commit and
    rollback capabilities.
    """

    transaction_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this transaction",
    )
    session_id: str = Field(
        default="",
        description="The session ID this transaction belongs to",
    )
    operations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Ordered list of operations within this transaction",
    )
    status: str = Field(
        default="PENDING",
        description="Current transaction status: PENDING, COMMITTED, or FAILED",
    )
    rollback_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata that would be used for rollback (placeholder)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transaction was created",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the transaction was completed",
    )

    def complete(self, status: str = "COMMITTED") -> None:
        """Mark the transaction as completed with the given status."""
        self.status = status
        self.completed_at = datetime.now(UTC)
