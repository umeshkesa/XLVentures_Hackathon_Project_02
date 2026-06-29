"""MemoryPolicyEngine — validates records against MemoryPolicy.

Checks TTL, retention, encryption, compression, replication, audit,
and lifecycle rules.  Returns a PolicyDecision with violations.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.memory.contracts.models import MemoryPolicy, MemoryRecord
from adip.memory.enums import MemoryLifecycleStatus, RetentionPolicy
from adip.memory.execution.models import PolicyDecision

log = structlog.get_logger(__name__)


class MemoryPolicyEngine:
    """Validates memory records against a MemoryPolicy.

    Each validation method checks a single policy rule and appends
    violations to the decision.
    """

    async def validate(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy,
    ) -> PolicyDecision:
        """Run all policy checks.  Returns a PolicyDecision."""
        violations: list[str] = []
        warnings: list[str] = []

        self._check_ttl(record, policy, violations, warnings)
        self._check_retention(record, policy, violations, warnings)
        self._check_encryption(policy, violations, warnings)
        self._check_compression(policy, violations, warnings)
        self._check_replication(policy, violations, warnings)
        self._check_audit(policy, violations, warnings)
        self._check_lifecycle(record, violations, warnings)

        decision = PolicyDecision(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            policy_name="default",
        )

        if not decision.valid:
            log.warning(
                "policy.violations",
                memory_id=str(record.memory_id),
                violations=violations,
            )
        else:
            log.debug("policy.valid", memory_id=str(record.memory_id))

        return decision

    # ── Individual checks ─────────────────────────────────────────────────

    @staticmethod
    def _check_ttl(
        record: MemoryRecord,
        policy: MemoryPolicy,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        if record.expires_at and record.expires_at < datetime.now(UTC):
            violations.append("Record has already expired based on expires_at")
        if policy.ttl and record.expires_at is None:
            warnings.append("Policy specifies TTL but record has no expires_at")

    @staticmethod
    def _check_retention(
        record: MemoryRecord,
        policy: MemoryPolicy,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        if policy.retention_policy == RetentionPolicy.TEMPORARY:
            if record.expires_at is None:
                warnings.append(
                    "Temporary retention policy recommended but no TTL set",
                )

    @staticmethod
    def _check_encryption(
        policy: MemoryPolicy,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        if policy.encryption_required:
            encrypted = False  # placeholder check
            if not encrypted:
                warnings.append("Encryption required by policy but not yet implemented")

    @staticmethod
    def _check_compression(
        policy: MemoryPolicy,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        if policy.compression_enabled:
            warnings.append("Compression enabled by policy but not yet implemented")

    @staticmethod
    def _check_replication(
        policy: MemoryPolicy,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        if policy.replication_required:
            warnings.append("Replication required by policy but not yet implemented")

    @staticmethod
    def _check_audit(
        policy: MemoryPolicy,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        if not policy.audit_enabled:
            warnings.append("Audit is disabled by policy")

    @staticmethod
    def _check_lifecycle(
        record: MemoryRecord,
        violations: list[str],
        warnings: list[str],
    ) -> None:
        raw = record.metadata.get("lifecycle_status")
        if raw:
            try:
                status = MemoryLifecycleStatus(raw)
                if MemoryLifecycleManager.is_terminal(status):
                    warnings.append(f"Operation on terminal lifecycle state: {status.value}")
            except ValueError:
                violations.append(f"Invalid lifecycle status in metadata: {raw}")


# Late import to avoid circular dependency in the static method
from adip.memory.execution.lifecycle import MemoryLifecycleManager  # noqa: E402, F811
