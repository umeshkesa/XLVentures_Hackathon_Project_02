"""MemoryValidator — validates memory records before storage.

Checks required fields, ownership, namespace, lifecycle, TTL,
retention, metadata, and version constraints.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.memory.contracts.models import MemoryRecord

log = structlog.get_logger(__name__)


class MemoryValidator:
    """Validates a MemoryRecord before any storage operation.

    Returns a list of error messages (empty = valid).
    """

    def validate(self, record: MemoryRecord) -> list[str]:
        """Run all validation checks.  Raises ValueError on failure."""
        errors: list[str] = []

        self._check_required_fields(record, errors)
        self._check_ownership(record, errors)
        self._check_namespace(record, errors)
        self._check_lifecycle(record, errors)
        self._check_ttl(record, errors)
        self._check_retention(record, errors)
        self._check_metadata(record, errors)
        self._check_version(record, errors)

        if errors:
            log.warning(
                "validator.failed",
                memory_id=str(record.memory_id),
                errors=errors,
            )
            raise ValueError(f"Memory validation failed: {'; '.join(errors)}")

        log.debug("validator.passed", memory_id=str(record.memory_id))
        return errors

    # ── Individual checks ─────────────────────────────────────────────────

    @staticmethod
    def _check_required_fields(record: MemoryRecord, errors: list[str]) -> None:
        if not record.memory_type:
            errors.append("memory_type is required")

    @staticmethod
    def _check_ownership(record: MemoryRecord, errors: list[str]) -> None:
        if not record.owner_id:
            errors.append("owner_id is required")

    @staticmethod
    def _check_namespace(record: MemoryRecord, errors: list[str]) -> None:
        if not record.namespace:
            errors.append("namespace is required")
        if not record.namespace.strip():
            errors.append("namespace cannot be blank")

    @staticmethod
    def _check_lifecycle(record: MemoryRecord, errors: list[str]) -> None:
        raw = record.metadata.get("lifecycle_status")
        if raw is not None:
            from adip.memory.enums import MemoryLifecycleStatus
            try:
                MemoryLifecycleStatus(raw)
            except ValueError:
                errors.append(f"Invalid lifecycle_status: {raw}")

    @staticmethod
    def _check_ttl(record: MemoryRecord, errors: list[str]) -> None:
        if record.expires_at and record.expires_at < datetime.now(UTC):
            errors.append("expires_at is in the past")

    @staticmethod
    def _check_retention(record: MemoryRecord, errors: list[str]) -> None:
        pass  # retention policy is validated by PolicyEngine

    @staticmethod
    def _check_metadata(record: MemoryRecord, errors: list[str]) -> None:
        if record.metadata is None:
            errors.append("metadata cannot be None")

    @staticmethod
    def _check_version(record: MemoryRecord, errors: list[str]) -> None:
        if record.version < 1:
            errors.append("version must be >= 1")
