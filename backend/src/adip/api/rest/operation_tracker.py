"""Operation Tracker — tracks pending, running, and completed operations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

from adip.api.rest.enums import OperationStatus

logger = structlog.get_logger(__name__)


class TrackedOperation:
    """Represents a single tracked operation."""

    def __init__(self, operation_id: UUID, operation_type: str, params: dict[str, Any] | None = None) -> None:
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.params = params or {}
        self.status = OperationStatus.PENDING
        self.progress: float = 0.0
        self.created_at = datetime.now(UTC)
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.result: Any = None
        self.error: str | None = None

    def start(self) -> None:
        self.status = OperationStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def complete(self, result: Any = None) -> None:
        self.status = OperationStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.progress = 1.0
        self.result = result

    def fail(self, error: str) -> None:
        self.status = OperationStatus.FAILED
        self.completed_at = datetime.now(UTC)
        self.error = error

    def cancel(self) -> None:
        self.status = OperationStatus.CANCELLED
        self.completed_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": str(self.operation_id),
            "operation_type": self.operation_type,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


class OperationTracker:
    """Tracks async operations through their lifecycle."""

    def __init__(self) -> None:
        self._operations: dict[str, TrackedOperation] = {}

    def create_operation(self, operation_type: str, params: dict[str, Any] | None = None) -> TrackedOperation:
        operation_id = uuid4()
        operation = TrackedOperation(operation_id, operation_type, params)
        self._operations[str(operation_id)] = operation
        logger.info("operation.created", operation_id=str(operation_id), operation_type=operation_type)
        return operation

    def get_operation(self, operation_id: str) -> TrackedOperation | None:
        return self._operations.get(operation_id)

    def get_operations_by_status(self, status: OperationStatus) -> list[TrackedOperation]:
        return [op for op in self._operations.values() if op.status == status]

    def get_pending_operations(self) -> list[TrackedOperation]:
        return self.get_operations_by_status(OperationStatus.PENDING)

    def get_running_operations(self) -> list[TrackedOperation]:
        return self.get_operations_by_status(OperationStatus.RUNNING)

    def get_completed_operations(self) -> list[TrackedOperation]:
        return self.get_operations_by_status(OperationStatus.COMPLETED)

    def get_failed_operations(self) -> list[TrackedOperation]:
        return self.get_operations_by_status(OperationStatus.FAILED)

    def cancel_operation(self, operation_id: str) -> bool:
        operation = self._operations.get(operation_id)
        if operation and operation.status in (OperationStatus.PENDING, OperationStatus.RUNNING):
            operation.cancel()
            logger.info("operation.cancelled", operation_id=operation_id)
            return True
        return False

    def start_operation(self, operation_id: str) -> bool:
        operation = self._operations.get(operation_id)
        if operation and operation.status == OperationStatus.PENDING:
            operation.start()
            return True
        return False

    def complete_operation(self, operation_id: str, result: Any = None) -> bool:
        operation = self._operations.get(operation_id)
        if operation and operation.status == OperationStatus.RUNNING:
            operation.complete(result)
            return True
        return False

    def fail_operation(self, operation_id: str, error: str) -> bool:
        operation = self._operations.get(operation_id)
        if operation:
            operation.fail(error)
            return True
        return False

    def list_operations(self) -> list[dict[str, Any]]:
        return [op.to_dict() for op in self._operations.values()]

    def count_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for op in self._operations.values():
            key = op.status.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def clear(self) -> None:
        self._operations.clear()
        logger.info("operation_tracker.cleared")
