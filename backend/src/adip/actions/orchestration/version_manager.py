"""ActionVersionManager — manages action plan versions.

Deterministic placeholder providing version tracking for
action plans. Supports creating versions, retrieving version
history, comparing versions, and marking active versions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ActionVersionRecord(BaseModel):
    """A version record for an action plan."""

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this version belongs to",
    )
    version_number: int = Field(
        default=1,
        ge=1,
        description="Sequential version number",
    )
    description: str = Field(
        default="",
        description="Description of this version",
    )
    is_active: bool = Field(
        default=False,
        description="Whether this is the active version",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the version was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional version metadata",
    )


class ActionVersionManager:
    """Manages versions of action plans.

    Provides version creation, retrieval, comparison,
    and active version management.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[ActionVersionRecord]] = {}

    def create_version(
        self,
        plan_id: str,
        description: str = "",
        correlation_id: str = "",
    ) -> ActionVersionRecord:
        """Create a new version for a plan.

        Args:
            plan_id: The plan ID to version.
            description: Description of this version.
            correlation_id: Optional correlation ID.

        Returns:
            The created ActionVersionRecord.
        """
        versions = self._versions.get(plan_id, [])
        version_number = len(versions) + 1

        for v in versions:
            v.is_active = False
        self._versions[plan_id] = versions

        record = ActionVersionRecord(
            plan_id=plan_id,
            version_number=version_number,
            description=description or f"Version {version_number}",
            is_active=True,
        )
        versions.append(record)
        self._versions[plan_id] = versions

        log.info(
            "version.created",
            plan_id=plan_id,
            version=version_number,
        )
        return record

    def get_versions(self, plan_id: str) -> list[ActionVersionRecord]:
        """Get all versions for a plan.

        Args:
            plan_id: The plan ID.

        Returns:
            List of ActionVersionRecords.
        """
        return list(self._versions.get(plan_id, []))

    def get_active_version(self, plan_id: str) -> ActionVersionRecord | None:
        """Get the active version for a plan.

        Args:
            plan_id: The plan ID.

        Returns:
            Active ActionVersionRecord if found, None otherwise.
        """
        versions = self._versions.get(plan_id, [])
        for v in versions:
            if v.is_active:
                return v
        return None

    def mark_active(
        self,
        plan_id: str,
        version_id: str,
    ) -> ActionVersionRecord | None:
        """Mark a specific version as active.

        Args:
            plan_id: The plan ID.
            version_id: The version ID to activate.

        Returns:
            The activated ActionVersionRecord if found, None otherwise.
        """
        versions = self._versions.get(plan_id, [])
        found: ActionVersionRecord | None = None
        for v in versions:
            if str(v.version_id) == version_id:
                v.is_active = True
                found = v
            else:
                v.is_active = False
        if found:
            log.info(
                "version.activated",
                plan_id=plan_id,
                version=found.version_number,
            )
        return found

    def compare_versions(
        self,
        plan_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """Compare two versions of a plan.

        Args:
            plan_id: The plan ID.
            version_a: First version number.
            version_b: Second version number.

        Returns:
            Dict with comparison result.
        """
        versions = self._versions.get(plan_id, [])
        va = next((v for v in versions if v.version_number == version_a), None)
        vb = next((v for v in versions if v.version_number == version_b), None)

        return {
            "plan_id": plan_id,
            "version_a": version_a,
            "version_b": version_b,
            "version_a_exists": va is not None,
            "version_b_exists": vb is not None,
            "version_a_active": va.is_active if va else False,
            "version_b_active": vb.is_active if vb else False,
            "version_a_created": str(va.created_at) if va else None,
            "version_b_created": str(vb.created_at) if vb else None,
        }

    def clear(self) -> None:
        """Clear all versions."""
        self._versions.clear()
