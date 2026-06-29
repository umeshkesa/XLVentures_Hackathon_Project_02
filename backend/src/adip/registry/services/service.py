"""RegistryService — the ONLY public API for registry operations.

Provides validation, authentication, authorisation, audit, structured
logging, metrics, correlation ID propagation, and session management.
All external ADIP modules MUST interact with the registry through this
service — never through RegistryManager or RegistryCoordinator directly.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import structlog

from adip.registry.contracts.models import (
    RegistryEntry,
    RegistryFilter,
    RegistryHealth,
    RegistryMetrics,
    RegistrySearchResult,
    RegistrySession,
)
from adip.registry.orchestration.manager import RegistryManager
from adip.registry.services.hooks import IntegrationHooks
from adip.registry.services.hooks import hooks as default_hooks

log = structlog.get_logger(__name__)


@dataclass
class AuthResult:
    """Result of an authentication/authorisation check."""

    authenticated: bool = True
    authorised: bool = True
    user_id: str = ""
    message: str = ""


class RegistryService:
    """Enterprise facade for all registry operations.

    This is the ONLY public API for registry operations. External
    modules (Planner, Workflow Engine, Memory Manager, etc.) MUST
    go through this service.

    Responsibilities:
        • Request validation
        • Authentication (via configurable auth_callback)
        • Authorisation (via configurable auth_callback)
        • Audit (via configurable audit_callback)
        • Structured logging
        • Metrics
        • Correlation IDs
        • RegistrySession management
        • Integration hooks
        • Delegation to RegistryManager
    """

    def __init__(
        self,
        manager: RegistryManager | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[[str, str], AuthResult] | None = None,
        audit_callback: Callable[[str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.manager = manager or RegistryManager()
        self.hooks = hooks or default_hooks
        self.auth_callback = auth_callback or self._default_auth
        self.audit_callback = audit_callback or self._default_audit

    # ─────────────────────────────────────────────────────────────────
    # Registration
    # ─────────────────────────────────────────────────────────────────

    def register_entry(
        self,
        entry: RegistryEntry,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Register a new entry with full enterprise pipeline.

        Validates auth, invokes pre/post hooks, delegates to manager,
        records audit, and returns the registered entry on success.
        """
        corr_id = correlation_id or str(uuid.uuid4())
        log.info(
            "registry_service.register_entry",
            name=entry.name,
            user_id=user_id,
            correlation_id=corr_id,
        )

        # Auth
        auth = self.auth_callback(user_id, "register")
        if not auth.authenticated or not auth.authorised:
            log.warning("registry_service.register_entry.auth_failed", user_id=user_id)
            self.audit_callback("register", entry.name, {
                "status": "DENIED",
                "reason": auth.message,
                "correlation_id": corr_id,
            })
            return None

        # Session
        session = RegistrySession(
            registry_type=entry.registry_type,
            operation="register",
            user_id=user_id,
            namespace=entry.namespace,
            correlation_id=corr_id,
        )

        # Pre-hooks
        self.hooks.invoke_pre_register(entry=entry, session=session, correlation_id=corr_id)
        self.hooks.invoke_session_started(session=session, correlation_id=corr_id)

        try:
            # Delegate
            decision = self.manager.create_entry(entry, performed_by=user_id, correlation_id=corr_id)
            result = self.manager.read_entry(str(entry.entry_id), correlation_id=corr_id) if decision.allowed else None

            # Audit
            self.audit_callback("register", entry.name, {
                "entry_id": str(entry.entry_id),
                "allowed": decision.allowed,
                "reasoning": decision.reasoning,
                "correlation_id": corr_id,
            })

            # Post-hooks
            session.status = "COMPLETED" if decision.allowed else "FAILED"
            self.hooks.invoke_session_completed(session=session, correlation_id=corr_id)
            self.hooks.invoke_post_register(
                entry=entry, decision=decision, session=session, correlation_id=corr_id,
            )

            return result
        except Exception as exc:
            log.exception("registry_service.register_entry.error", correlation_id=corr_id)
            self.hooks.invoke_error(operation="register", error=exc, correlation_id=corr_id)
            self.audit_callback("register", entry.name, {
                "status": "ERROR",
                "error": str(exc),
                "correlation_id": corr_id,
            })
            session.status = "FAILED"
            raise

    # ─────────────────────────────────────────────────────────────────
    # Lookup
    # ─────────────────────────────────────────────────────────────────

    def get_entry(
        self,
        entry_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Retrieve a registry entry by its identifier."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info("registry_service.get_entry", entry_id=entry_id, correlation_id=corr_id)

        auth = self.auth_callback(user_id, "read")
        if not auth.authenticated or not auth.authorised:
            return None

        self.hooks.invoke_pre_lookup(entry_id=entry_id, correlation_id=corr_id)

        try:
            entry = self.manager.read_entry(entry_id, correlation_id=corr_id)
            self.hooks.invoke_post_lookup(entry=entry, correlation_id=corr_id)
            self.audit_callback("read", entry_id, {
                "found": entry is not None,
                "correlation_id": corr_id,
            })
            return entry
        except Exception as exc:
            self.hooks.invoke_error(operation="read", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────────────────────────

    def update_entry(
        self,
        entry: RegistryEntry,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Update an existing entry."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info("registry_service.update_entry", entry_id=str(entry.entry_id), correlation_id=corr_id)

        auth = self.auth_callback(user_id, "update")
        if not auth.authenticated or not auth.authorised:
            self.audit_callback("update", str(entry.entry_id), {
                "status": "DENIED",
                "correlation_id": corr_id,
            })
            return None

        self.hooks.invoke_pre_update(entry=entry, correlation_id=corr_id)

        try:
            decision = self.manager.update_entry(entry, performed_by=user_id, correlation_id=corr_id)
            result = self.manager.read_entry(str(entry.entry_id), correlation_id=corr_id) if decision.allowed else None

            self.audit_callback("update", str(entry.entry_id), {
                "allowed": decision.allowed,
                "reasoning": decision.reasoning,
                "correlation_id": corr_id,
            })
            self.hooks.invoke_post_update(entry=entry, decision=decision, correlation_id=corr_id)
            return result
        except Exception as exc:
            self.hooks.invoke_error(operation="update", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────────────────────────

    def delete_entry(
        self,
        entry_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Delete a registry entry."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info("registry_service.delete_entry", entry_id=entry_id, correlation_id=corr_id)

        auth = self.auth_callback(user_id, "delete")
        if not auth.authenticated or not auth.authorised:
            self.audit_callback("delete", entry_id, {
                "status": "DENIED",
                "correlation_id": corr_id,
            })
            return False

        self.hooks.invoke_pre_delete(entry_id=entry_id, correlation_id=corr_id)

        try:
            decision = self.manager.delete_entry(entry_id, performed_by=user_id, correlation_id=corr_id)
            self.audit_callback("delete", entry_id, {
                "allowed": decision.allowed,
                "reasoning": decision.reasoning,
                "correlation_id": corr_id,
            })
            self.hooks.invoke_post_delete(entry_id=entry_id, decision=decision, correlation_id=corr_id)
            return decision.allowed
        except Exception as exc:
            self.hooks.invoke_error(operation="delete", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────────────────────────

    def search_entries(
        self,
        filter: RegistryFilter,
        user_id: str = "",
        correlation_id: str = "",
    ) -> list[RegistrySearchResult]:
        """Search for entries matching the given filter."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info("registry_service.search_entries", query=filter.query, correlation_id=corr_id)

        auth = self.auth_callback(user_id, "search")
        if not auth.authenticated or not auth.authorised:
            return []

        self.hooks.invoke_pre_search(query=filter.query, correlation_id=corr_id)

        try:
            results = self.manager.search_entries(
                query=filter.query,
                registry_type=filter.registry_type,
                scope=filter.scope,
                status=filter.status,
                tags=filter.tags,
                namespace=filter.namespace,
                limit=filter.limit,
                offset=filter.offset,
                correlation_id=corr_id,
            )
            self.hooks.invoke_post_search(results=results, correlation_id=corr_id)
            self.audit_callback("search", filter.query, {
                "result_count": len(results),
                "correlation_id": corr_id,
            })
            return results
        except Exception as exc:
            self.hooks.invoke_error(operation="search", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Lifecycle operations
    # ─────────────────────────────────────────────────────────────────

    def activate_entry(
        self,
        entry_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Activate a registry entry."""
        corr_id = correlation_id or str(uuid.uuid4())

        auth = self.auth_callback(user_id, "activate")
        if not auth.authenticated or not auth.authorised:
            return None

        try:
            decision = self.manager.activate_entry(entry_id, performed_by=user_id, correlation_id=corr_id)
            self.audit_callback("activate", entry_id, {
                "allowed": decision.allowed,
                "correlation_id": corr_id,
            })
            return self.manager.read_entry(entry_id, correlation_id=corr_id) if decision.allowed else None
        except Exception as exc:
            self.hooks.invoke_error(operation="activate", error=exc, correlation_id=corr_id)
            raise

    def suspend_entry(
        self,
        entry_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Suspend a registry entry."""
        corr_id = correlation_id or str(uuid.uuid4())

        auth = self.auth_callback(user_id, "suspend")
        if not auth.authenticated or not auth.authorised:
            return None

        try:
            decision = self.manager.suspend_entry(entry_id, performed_by=user_id, correlation_id=corr_id)
            self.audit_callback("suspend", entry_id, {
                "allowed": decision.allowed,
                "correlation_id": corr_id,
            })
            return self.manager.read_entry(entry_id, correlation_id=corr_id) if decision.allowed else None
        except Exception as exc:
            self.hooks.invoke_error(operation="suspend", error=exc, correlation_id=corr_id)
            raise

    def deprecate_entry(
        self,
        entry_id: str,
        user_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Deprecate a registry entry."""
        corr_id = correlation_id or str(uuid.uuid4())

        auth = self.auth_callback(user_id, "deprecate")
        if not auth.authenticated or not auth.authorised:
            return None

        try:
            decision = self.manager.deprecate_entry(
                entry_id, performed_by=user_id, reason=reason, correlation_id=corr_id,
            )
            self.audit_callback("deprecate", entry_id, {
                "allowed": decision.allowed,
                "reason": reason,
                "correlation_id": corr_id,
            })
            return self.manager.read_entry(entry_id, correlation_id=corr_id) if decision.allowed else None
        except Exception as exc:
            self.hooks.invoke_error(operation="deprecate", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Health & Metrics
    # ─────────────────────────────────────────────────────────────────

    def health(self) -> RegistryHealth:
        """Return the current health status of the registry platform."""
        return self.manager.get_health()

    def get_metrics(self) -> RegistryMetrics:
        """Return aggregated registry platform metrics."""
        metrics = self.manager.get_metrics()
        # Increment metrics read counter on the underlying collector
        try:
            self.manager.coordinator.metrics_collector.increment_lookups()
        except AttributeError:
            pass
        return metrics

    # ── Defaults ────────────────────────────────────────────────────

    @staticmethod
    def _default_auth(user_id: str, operation: str) -> AuthResult:
        """Default auth — allows all operations."""
        return AuthResult(authenticated=True, authorised=True, user_id=user_id)

    @staticmethod
    def _default_audit(operation: str, target: str, details: dict[str, Any]) -> None:
        """Default audit — logs to structlog."""
        log.info("registry_service.audit", operation=operation, target=target, details=details)
