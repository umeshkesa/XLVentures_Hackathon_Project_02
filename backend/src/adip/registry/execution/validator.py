"""RegistryValidator — validates registry entries and operations.

Ensures entries have valid metadata, namespaces are properly
configured, versions follow semantic versioning, lifecycle
transitions are valid, and scopes are within permitted ranges.
"""

from __future__ import annotations

import re
from typing import Any

import structlog

from adip.registry.contracts.models import RegistryEntry, RegistryMetadata, RegistryNamespace
from adip.registry.enums import RegistryLifecycleStatus, RegistryScope

log = structlog.get_logger(__name__)

_SEMVER_PATTERN: re.Pattern[str] = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

_VALID_SCOPES_BY_NAMESPACE: dict[str, list[RegistryScope]] = {
    "default": [RegistryScope.GLOBAL, RegistryScope.SYSTEM],
}


class RegistryValidator:
    """Validates registry entries, metadata, namespaces, versions,
    lifecycle transitions, and scopes."""

    def validate_entry(self, entry: RegistryEntry) -> list[str]:
        """Validate a complete registry entry. Returns list of violations."""
        log.info("registry_validator.validate_entry", entry_id=str(entry.entry_id), name=entry.name)
        violations: list[str] = []
        violations.extend(self._validate_name(entry.name))
        violations.extend(self._validate_version_string(entry.version))
        violations.extend(self._validate_tags(entry.tags))
        violations.extend(self._validate_metadata_dict(entry.metadata))
        return violations

    def validate_metadata(self, metadata: RegistryMetadata) -> list[str]:
        """Validate registry metadata. Returns list of violations."""
        log.info("registry_validator.validate_metadata")
        violations: list[str] = []
        if len(metadata.description) > 2000:
            violations.append("Metadata description exceeds 2000 characters")
        if len(metadata.display_name) > 256:
            violations.append("Metadata display_name exceeds 256 characters")
        return violations

    def validate_namespace(self, namespace: RegistryNamespace) -> list[str]:
        """Validate a registry namespace. Returns list of violations."""
        log.info("registry_validator.validate_namespace", name=namespace.name)
        violations: list[str] = []
        if not namespace.name:
            violations.append("Namespace name is required")
        elif len(namespace.name) > 128:
            violations.append("Namespace name exceeds 128 characters")
        elif not re.match(r"^[a-zA-Z0-9_-]+$", namespace.name):
            violations.append("Namespace name must contain only alphanumeric characters, underscores, and hyphens")
        if not namespace.enabled:
            violations.append("Namespace is disabled")
        return violations

    def validate_version(self, version: str) -> list[str]:
        """Validate a version string (semver). Returns list of violations."""
        log.info("registry_validator.validate_version", version=version)
        return self._validate_version_string(version)

    def validate_lifecycle_transition(
        self,
        current_status: RegistryLifecycleStatus,
        new_status: RegistryLifecycleStatus,
    ) -> list[str]:
        """Validate a lifecycle status transition. Returns list of violations."""
        log.info(
            "registry_validator.validate_lifecycle_transition",
            from_status=current_status.value,
            to_status=new_status.value,
        )
        violations: list[str] = []
        valid_next = _ALLOWED_TRANSITIONS.get(current_status, set())
        if new_status not in valid_next:
            violations.append(
                f"Transition from {current_status.value} to {new_status.value} is not allowed. "
                f"Valid next states: {[s.value for s in valid_next]}"
            )
        return violations

    def validate_scope(self, scope: RegistryScope, entry: RegistryEntry) -> list[str]:
        """Validate a scope assignment for an entry. Returns list of violations."""
        log.info("registry_validator.validate_scope", scope=scope.value, entry_id=str(entry.entry_id))
        violations: list[str] = []
        allowed = _VALID_SCOPES_BY_NAMESPACE.get(entry.namespace, list(RegistryScope))
        if scope not in allowed:
            violations.append(
                f"Scope {scope.value} is not allowed in namespace '{entry.namespace}'. "
                f"Allowed: {[s.value for s in allowed]}"
            )
        return violations

    # ── private helpers ──────────────────────────────────────────────

    def _validate_name(self, name: str) -> list[str]:
        violations: list[str] = []
        if not name:
            violations.append("Entry name is required")
        elif len(name) > 256:
            violations.append("Entry name exceeds 256 characters")
        elif not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$", name):
            violations.append(
                "Entry name must start with an alphanumeric character and contain only "
                "alphanumeric characters, underscores, dots, and hyphens"
            )
        return violations

    def _validate_version_string(self, version: str) -> list[str]:
        violations: list[str] = []
        if not version:
            violations.append("Version string is required")
        elif not _SEMVER_PATTERN.match(version):
            violations.append(f"Version '{version}' is not a valid semver string")
        return violations

    def _validate_tags(self, tags: list[str]) -> list[str]:
        violations: list[str] = []
        if len(tags) > 50:
            violations.append("Tag count exceeds maximum of 50")
        for tag in tags:
            if len(tag) > 64:
                violations.append(f"Tag '{tag}' exceeds 64 characters")
            elif not re.match(r"^[a-zA-Z0-9_.-]+$", tag):
                violations.append(
                    f"Tag '{tag}' must contain only alphanumeric characters, underscores, dots, and hyphens"
                )
        return violations

    def _validate_metadata_dict(self, metadata: dict[str, Any]) -> list[str]:
        violations: list[str] = []
        if len(metadata) > 100:
            violations.append("Metadata exceeds maximum of 100 entries")
        for key in metadata:
            if len(key) > 128:
                violations.append(f"Metadata key '{key}' exceeds 128 characters")
        return violations


_ALLOWED_TRANSITIONS: dict[RegistryLifecycleStatus, set[RegistryLifecycleStatus]] = {
    RegistryLifecycleStatus.REGISTERED: {RegistryLifecycleStatus.VALIDATED},
    RegistryLifecycleStatus.VALIDATED: {RegistryLifecycleStatus.ACTIVE, RegistryLifecycleStatus.REGISTERED},
    RegistryLifecycleStatus.ACTIVE: {RegistryLifecycleStatus.SUSPENDED, RegistryLifecycleStatus.DEPRECATED},
    RegistryLifecycleStatus.SUSPENDED: {RegistryLifecycleStatus.ACTIVE, RegistryLifecycleStatus.DEPRECATED},
    RegistryLifecycleStatus.DEPRECATED: {RegistryLifecycleStatus.REMOVED},
    RegistryLifecycleStatus.REMOVED: set(),
}
