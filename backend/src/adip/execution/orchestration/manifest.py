"""ExecutionManifestBuilder — builds execution manifests for packages.

Deterministic placeholder that creates a manifest declaring what
capabilities, adapters, sandboxes, and policies an execution
package requires.
"""

from __future__ import annotations

import structlog

from adip.execution.contracts.models import ExecutionManifest

log = structlog.get_logger(__name__)


class ExecutionManifestBuilder:
    """Builds execution manifests from execution packages.

    Creates a manifest that declares required adapters, sandbox
    requirements, resource limits, and policy constraints.
    """

    def __init__(self) -> None:
        self._manifests: dict[str, ExecutionManifest] = {}

    def build(
        self,
        package_id: str,
        required_adapters: list[str] | None = None,
        requires_sandbox: bool = False,
        resource_limits: dict[str, float] | None = None,
        timeout_seconds: int = 300,
        requires_compensation: bool = False,
        policy_tags: list[str] | None = None,
        correlation_id: str = "",
    ) -> ExecutionManifest:
        """Build an execution manifest.

        Args:
            package_id: The execution package ID.
            required_adapters: List of required adapter types.
            requires_sandbox: Whether sandbox execution is needed.
            resource_limits: Resource limit requirements.
            timeout_seconds: Maximum execution timeout.
            requires_compensation: Whether compensation is needed.
            policy_tags: Policy tags for validation.
            correlation_id: Optional correlation ID.

        Returns:
            The created ExecutionManifest.
        """
        manifest = ExecutionManifest(
            package_id=package_id,
            required_adapters=required_adapters or [],
            required_sandbox=requires_sandbox,
            resource_limits=resource_limits or {},
            timeout_seconds=timeout_seconds,
            compensation_required=requires_compensation,
            policy_tags=policy_tags or [],
        )
        self._manifests[str(manifest.manifest_id)] = manifest
        log.info(
            "manifest.built",
            package_id=package_id,
            manifest_id=str(manifest.manifest_id),
            adapters=len(manifest.required_adapters),
            cid=correlation_id,
        )
        return manifest

    def get_manifest(self, manifest_id: str) -> ExecutionManifest | None:
        """Retrieve a manifest by ID.

        Args:
            manifest_id: The manifest identifier.

        Returns:
            ExecutionManifest if found, None otherwise.
        """
        return self._manifests.get(manifest_id)
