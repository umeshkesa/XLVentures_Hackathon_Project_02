"""ExecutionAuditPackage — creates immutable audit packages.

Deterministic placeholder that packages execution audit data
into immutable records with hash verification for compliance
and regulatory purposes. Phase 3.5.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class AuditPackage(BaseModel):
    """An immutable audit package for execution."""

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audit package identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this audit package belongs to",
    )
    request_id: str = Field(
        default="",
        description="The request ID this audit package covers",
    )
    package_type: str = Field(
        default="execution",
        description="Type of audit package (execution, compliance, recovery, decision)",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="The audit data contained in this package",
    )
    checksum: str = Field(
        default="",
        description="SHA-256 checksum of the package data",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was created",
    )


class ExecutionAuditPackage:
    """Creates immutable audit packages for execution operations.

    Packages execution data into immutable records with SHA-256
    checksums for compliance, regulatory, and forensic analysis.
    """

    def __init__(self) -> None:
        self._packages: dict[str, AuditPackage] = {}

    def create_package(
        self,
        session_id: str,
        request_id: str = "",
        package_type: str = "execution",
        data: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> AuditPackage:
        """Create an immutable audit package.

        Args:
            session_id: The session to package.
            request_id: The request ID.
            package_type: Type of audit package.
            data: The data to include in the package.
            correlation_id: Optional correlation ID.

        Returns:
            The created AuditPackage with checksum.
        """
        package_data = data or {}
        # Deterministic serialisation for checksum
        serialised = json.dumps(package_data, sort_keys=True, default=str)
        checksum = hashlib.sha256(serialised.encode("utf-8")).hexdigest()

        package = AuditPackage(
            session_id=session_id,
            request_id=request_id,
            package_type=package_type,
            data=package_data,
            checksum=checksum,
        )
        self._packages[str(package.package_id)] = package

        log.info(
            "audit_package.created",
            session_id=session_id,
            package_type=package_type,
            checksum=checksum[:16],
            cid=correlation_id,
        )
        return package

    def verify_package(self, package_id: str) -> bool:
        """Verify the integrity of an audit package.

        Recalculates the checksum and compares it with the stored value.

        Args:
            package_id: The package identifier.

        Returns:
            True if the package is intact, False otherwise.
        """
        package = self._packages.get(package_id)
        if not package:
            return False
        serialised = json.dumps(package.data, sort_keys=True, default=str)
        expected_checksum = hashlib.sha256(serialised.encode("utf-8")).hexdigest()
        return package.checksum == expected_checksum

    def get_package(self, package_id: str) -> AuditPackage | None:
        """Retrieve an audit package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            AuditPackage if found, None otherwise.
        """
        return self._packages.get(package_id)

    def get_packages_for_session(self, session_id: str) -> list[AuditPackage]:
        """Get all audit packages for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of AuditPackage objects.
        """
        return [p for p in self._packages.values() if p.session_id == session_id]

    def get_package_count(self) -> int:
        """Get total number of audit packages.

        Returns:
            Package count.
        """
        return len(self._packages)
