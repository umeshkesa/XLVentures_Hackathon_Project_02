"""RegistryPolicyEngine — validates registry operations against policies.

Supports registration, namespace, version, scope, and permission
policy validation.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import RegistryEntry, RegistryNamespace
from adip.registry.enums import RegistryLifecycleStatus, RegistryScope, RegistryType

log = structlog.get_logger(__name__)


class RegistryPolicyEngine:
    """Validates registry operations against configured policies.

    Each policy check returns a list of violation strings. An empty
    list means the operation is permitted.
    """

    def __init__(self) -> None:
        self._max_entries_per_namespace: dict[str, int] = {}
        self._allowed_registry_types: set[RegistryType] = set(RegistryType)
        self._allowed_scopes: set[RegistryScope] = set(RegistryScope)

    def set_max_entries_per_namespace(self, namespace: str, max_entries: int) -> None:
        """Set the maximum number of entries allowed in a namespace."""
        self._max_entries_per_namespace[namespace] = max_entries

    def set_allowed_registry_types(self, types: set[RegistryType]) -> None:
        """Restrict which registry types are permitted."""
        self._allowed_registry_types = types

    def set_allowed_scopes(self, scopes: set[RegistryScope]) -> None:
        """Restrict which scopes are permitted."""
        self._allowed_scopes = scopes

    def check_registration_policy(self, entry: RegistryEntry, current_entries: list[RegistryEntry]) -> list[str]:
        """Check whether an entry can be registered."""
        log.info("registry_policy.check_registration", entry_id=str(entry.entry_id), name=entry.name)
        violations: list[str] = []
        if entry.registry_type not in self._allowed_registry_types:
            violations.append(f"Registry type {entry.registry_type.value} is not allowed")
        if entry.scope not in self._allowed_scopes:
            violations.append(f"Scope {entry.scope.value} is not allowed")
        max_entries = self._max_entries_per_namespace.get(entry.namespace, 0)
        if max_entries > 0:
            ns_count = sum(1 for e in current_entries if e.namespace == entry.namespace)
            if ns_count >= max_entries:
                violations.append(f"Namespace '{entry.namespace}' has reached its maximum of {max_entries} entries")
        return violations

    def check_namespace_policy(self, namespace: RegistryNamespace) -> list[str]:
        """Check whether a namespace operation is allowed."""
        log.info("registry_policy.check_namespace", name=namespace.name)
        violations: list[str] = []
        if not namespace.enabled:
            violations.append("Namespace is disabled")
        return violations

    def check_version_policy(self, entry: RegistryEntry, new_version: str) -> list[str]:
        """Check whether a version operation is allowed."""
        log.info("registry_policy.check_version", entry_id=str(entry.entry_id), new_version=new_version)
        violations: list[str] = []
        if entry.status == RegistryLifecycleStatus.REMOVED:
            violations.append("Cannot version a removed entry")
        if entry.status == RegistryLifecycleStatus.DEPRECATED:
            violations.append("Cannot version a deprecated entry")
        return violations

    def check_scope_policy(self, scope: RegistryScope, namespace: str = "") -> list[str]:
        """Check whether a scope is permitted."""
        log.info("registry_policy.check_scope", scope=scope.value, namespace=namespace)
        violations: list[str] = []
        if scope not in self._allowed_scopes:
            violations.append(f"Scope {scope.value} is not allowed")
        if namespace and scope == RegistryScope.GLOBAL and namespace != "default":
            violations.append("GLOBAL scope is only allowed in the 'default' namespace")
        return violations

    def check_permission_policy(self, entry: RegistryEntry, operation: str, user_id: str = "") -> list[str]:
        """Check whether a user has permission to perform an operation."""
        log.info("registry_policy.check_permission", entry_id=str(entry.entry_id), operation=operation, user_id=user_id)
        violations: list[str] = []
        if not user_id and operation in ("update", "delete", "deprecate"):
            violations.append("User ID is required for this operation")
        if entry.owner_id and user_id and entry.owner_id != user_id:
            if operation in ("delete", "deprecate"):
                violations.append(f"User '{user_id}' does not own entry '{entry.name}'")
        return violations
