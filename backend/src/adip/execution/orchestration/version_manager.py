"""ExecutionVersionManager — manages execution plan versions.

Deterministic placeholder providing version tracking for
execution packages. Supports creating versions, retrieving
version history, and marking active versions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ExecutionVersionRecord(BaseModel):
    """A version record for an execution plan."""

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version identifier",
    )
    package_id: str = Field(
        default="",
        description="The package this version belongs to",
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


class ExecutionVersionManager:
    """Manages versions of execution packages.

    Provides version creation, retrieval, and active version
    management.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[ExecutionVersionRecord]] = {}

    def create_version(
        self,
        package_id: str,
        description: str = "",
        correlation_id: str = "",
    ) -> ExecutionVersionRecord:
        """Create a new version for a package.

        Args:
            package_id: The package ID to version.
            description: Description of this version.
            correlation_id: Optional correlation ID.

        Returns:
            The created ExecutionVersionRecord.
        """
        versions = self._versions.get(package_id, [])
        version_number = len(versions) + 1

        for v in versions:
            v.is_active = False
        self._versions[package_id] = versions

        record = ExecutionVersionRecord(
            package_id=package_id,
            version_number=version_number,
            description=description or f"Version {version_number}",
            is_active=True,
        )
        versions.append(record)
        self._versions[package_id] = versions

        log.info(
            "version.created",
            package_id=package_id,
            version=version_number,
            cid=correlation_id,
        )
        return record

    def get_versions(self, package_id: str) -> list[ExecutionVersionRecord]:
        """Get all versions for a package.

        Args:
            package_id: The package identifier.

        Returns:
            List of ExecutionVersionRecord objects.
        """
        return list(self._versions.get(package_id, []))

    def get_active_version(
        self,
        package_id: str,
    ) -> ExecutionVersionRecord | None:
        """Get the active version for a package.

        Args:
            package_id: The package identifier.

        Returns:
            Active ExecutionVersionRecord if found, None otherwise.
        """
        versions = self._versions.get(package_id, [])
        for v in versions:
            if v.is_active:
                return v
        return None

    def compare_versions(
        self,
        package_id: str,
        version_a: int,
        version_b: int,
    ) -> dict[str, Any]:
        """Compare two versions of a package.

        Args:
            package_id: The package identifier.
            version_a: First version number.
            version_b: Second version number.

        Returns:
            Dict with comparison details.
        """
        versions = self._versions.get(package_id, [])
        va = next((v for v in versions if v.version_number == version_a), None)
        vb = next((v for v in versions if v.version_number == version_b), None)

        return {
            "package_id": package_id,
            "version_a": version_a,
            "version_b": version_b,
            "version_a_exists": va is not None,
            "version_b_exists": vb is not None,
            "version_a_active": va.is_active if va else False,
            "version_b_active": vb.is_active if vb else False,
            "version_a_created": str(va.created_at) if va else None,
            "version_b_created": str(vb.created_at) if vb else None,
            "has_differences": (
                (va.description != vb.description) if va and vb else True
            ),
        }

    def get_all_version_count(self) -> int:
        """Get total number of versions across all packages.

        Returns:
            Total version count.
        """
        total = 0
        for versions in self._versions.values():
            total += len(versions)
        return total
