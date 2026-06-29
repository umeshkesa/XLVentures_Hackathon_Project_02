"""APISnapshot — stores immutable snapshots of request/response state.

Phase 3.5: added timestamp, decision_id to snapshot metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class Snapshot:
    """An immutable snapshot of API request/response state."""

    def __init__(self) -> None:
        self.snapshot_id: UUID = uuid4()
        self.created_at: datetime = datetime.now(UTC)
        self.timestamp: datetime = self.created_at
        self.decision_id: str | None = None
        self.request: dict[str, Any] = {}
        self.response: dict[str, Any] = {}
        self.headers: dict[str, str] = {}
        self.parameters: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": str(self.snapshot_id),
            "created_at": self.created_at.isoformat(),
            "timestamp": self.timestamp.isoformat(),
            "decision_id": self.decision_id,
            "request": self.request,
            "response": self.response,
            "headers": self.headers,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


class APISnapshot:
    """Manages immutable snapshots of API request/response state."""

    def __init__(self) -> None:
        self._snapshots: dict[str, Snapshot] = {}

    def create_snapshot(
        self,
        request: dict[str, Any] | None = None,
        response: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        decision_id: str | None = None,
    ) -> Snapshot:
        snapshot = Snapshot()
        snapshot.decision_id = decision_id
        snapshot.request = request or {}
        snapshot.response = response or {}
        snapshot.headers = headers or {}
        snapshot.parameters = parameters or {}
        snapshot.metadata = metadata or {}
        self._snapshots[str(snapshot.snapshot_id)] = snapshot
        logger.info("snapshot.created", snapshot_id=str(snapshot.snapshot_id), decision_id=decision_id)
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Snapshot | None:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self._snapshots.values()]

    def count(self) -> int:
        return len(self._snapshots)

    def clear(self) -> None:
        self._snapshots.clear()
