"""PluginService — the ONLY public API for enterprise plugin operations.

Responsible for:
• Request validation
• Authentication & authorisation hooks
• Audit hook
• Logging & metrics
• Correlation ID propagation
• Session management
• Delegation to PluginManager

All external modules (Planner, Workflow Engine, Memory Manager,
Knowledge Manager, Rule Manager, Capability Registry, Agent Registry,
Tool Registry, Evidence Fusion Engine, Reasoning Engine,
Recommendation Engine, Action Engine) MUST go through PluginService.
PluginManager is internal-only.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.plugins.contracts.models import (
    Plugin,
    PluginDecision,
    PluginHealth,
    PluginMetrics,
    PluginSandbox,
    PluginSession,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType
from adip.plugins.execution.metrics import PluginMetricsCollector
from adip.plugins.execution.models import DiscoveryResult, LoaderResult
from adip.plugins.orchestration.manager import PluginManager
from adip.plugins.orchestration.session import PluginSessionManager
from adip.plugins.services.hooks import IntegrationHooks
from adip.plugins.services.hooks import hooks as default_hooks

log = structlog.get_logger(__name__)


class AuthResult:
    """Result of an authentication/authorisation check."""

    def __init__(self, allowed: bool = True, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class PluginService:
    """Enterprise facade for all plugin operations.

    This is the ONLY public API. External modules MUST use this class
    to interact with the Plugin Manager.

    PluginService must never call processing components directly.
    """

    def __init__(
        self,
        manager: PluginManager | None = None,
        hooks: IntegrationHooks | None = None,
        session_manager: PluginSessionManager | None = None,
        metrics_collector: PluginMetricsCollector | None = None,
        auth_callback: Callable[[str, str], AuthResult] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or PluginManager()
        self._hooks = hooks or default_hooks
        self._session_manager = session_manager or PluginSessionManager()
        self._metrics = metrics_collector or PluginMetricsCollector()
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def _audit(self, operation: str, entity_id: str, user_id: str, details: dict[str, Any]) -> None:
        """Record an audit entry if an audit callback is configured."""
        if self._audit_callback:
            try:
                self._audit_callback(operation, entity_id, user_id, details)
            except Exception:
                log.exception("service.audit.error", operation=operation)

    # ── Discover ────────────────────────────────────────────────────────────

    def discover_plugin(
        self,
        source: str,
        source_type: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> DiscoveryResult:
        """Validate, authorise, and discover a new plugin."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.discover", source=source, user_id=user_id, correlation_id=correlation_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "discover")
            if not auth.allowed:
                raise PermissionError(f"Discover not allowed: {auth.reason}")

        self._hooks.invoke_pre_discover(source)
        result = self._manager.discover_plugin(source, source_type)
        self._audit("discover", source, user_id, {"correlation_id": correlation_id, "source_type": source_type})
        return result

    # ── Install ─────────────────────────────────────────────────────────────

    def install_plugin(
        self,
        plugin: Plugin,
        user_id: str = "",
        correlation_id: str = "",
    ) -> PluginDecision:
        """Validate, authorise, and install a plugin.

        Returns a PluginDecision with full pipeline outcome.
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.install", plugin=plugin.name, user_id=user_id, correlation_id=correlation_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "install")
            if not auth.allowed:
                raise PermissionError(f"Install not allowed: {auth.reason}")

        session = self._session_manager.create_session(
            plugin_id=str(plugin.plugin_id),
            operation="install",
            user_id=user_id,
            correlation_id=correlation_id,
        )
        self._hooks.invoke_session_started(session)

        try:
            self._hooks.invoke_pre_install(plugin)
            decision = self._manager.install_plugin(plugin)
            self._hooks.invoke_post_install(decision)

            if decision.allowed:
                self._session_manager.complete_session(str(session.session_id))
                self._metrics.increment_load_successes()
            else:
                self._session_manager.fail_session(str(session.session_id), error_message=decision.reason)
                self._metrics.increment_load_failures()
        except Exception as e:
            self._session_manager.fail_session(str(session.session_id), error_message=str(e))
            self._hooks.invoke_error("install", e)
            self._audit("install_error", str(plugin.plugin_id), user_id, {"correlation_id": correlation_id})
            raise

        self._hooks.invoke_session_completed(session)
        self._audit("install", str(plugin.plugin_id), user_id, {
            "correlation_id": correlation_id,
            "allowed": decision.allowed,
            "decision": decision.decision,
        })
        return decision

    # ── Get Plugin ──────────────────────────────────────────────────────────

    def get_plugin(
        self,
        plugin_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Plugin | None:
        """Retrieve a plugin by identifier."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.get_plugin", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "read")
            if not auth.allowed:
                raise PermissionError(f"Read not allowed: {auth.reason}")

        plugin = self._manager.get_plugin(plugin_id)
        self._audit("read", plugin_id, user_id, {"correlation_id": correlation_id})
        return plugin

    # ── List Plugins ────────────────────────────────────────────────────────

    def list_plugins(
        self,
        domain: PluginDomain | None = None,
        plugin_type: PluginType | None = None,
        status: PluginLifecycleStatus | None = None,
        user_id: str = "",
        correlation_id: str = "",
    ) -> list[Plugin]:
        """List plugins matching the given filters."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.list_plugins", user_id=user_id, correlation_id=correlation_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "list")
            if not auth.allowed:
                raise PermissionError(f"List not allowed: {auth.reason}")

        results = self._manager.list_plugins(domain=domain, plugin_type=plugin_type, status=status)
        self._audit("list", "", user_id, {"correlation_id": correlation_id, "results": len(results)})
        return results

    # ── Activate ────────────────────────────────────────────────────────────

    def activate_plugin(
        self,
        plugin_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Plugin:
        """Activate a plugin."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.activate", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "activate")
            if not auth.allowed:
                raise PermissionError(f"Activate not allowed: {auth.reason}")

        session = self._session_manager.create_session(plugin_id=plugin_id, operation="activate", user_id=user_id)
        self._hooks.invoke_session_started(session)

        plugin = self._manager.get_plugin(plugin_id)
        if plugin is None:
            self._session_manager.fail_session(str(session.session_id), error_message="Plugin not found")
            raise ValueError(f"Plugin not found: {plugin_id}")

        try:
            self._hooks.invoke_pre_activate(plugin)
            result = self._manager.activate_plugin(plugin_id)
            if result:
                self._hooks.invoke_post_activate(result)
            self._session_manager.complete_session(str(session.session_id))
        except Exception as e:
            self._session_manager.fail_session(str(session.session_id), error_message=str(e))
            self._hooks.invoke_error("activate", e)
            raise

        self._hooks.invoke_session_completed(session)
        self._audit("activate", plugin_id, user_id, {"correlation_id": correlation_id})
        return result  # type: ignore[return-value]

    # ── Suspend ─────────────────────────────────────────────────────────────

    def suspend_plugin(
        self,
        plugin_id: str,
        reason: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> Plugin:
        """Suspend a plugin."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.suspend", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "suspend")
            if not auth.allowed:
                raise PermissionError(f"Suspend not allowed: {auth.reason}")

        session = self._session_manager.create_session(plugin_id=plugin_id, operation="suspend", user_id=user_id)
        self._hooks.invoke_session_started(session)

        plugin = self._manager.get_plugin(plugin_id)
        if plugin is None:
            self._session_manager.fail_session(str(session.session_id), error_message="Plugin not found")
            raise ValueError(f"Plugin not found: {plugin_id}")

        try:
            self._hooks.invoke_pre_suspend(plugin)
            result = self._manager.suspend_plugin(plugin_id, reason=reason)
            if result:
                self._hooks.invoke_post_suspend(result)
            self._session_manager.complete_session(str(session.session_id))
        except Exception as e:
            self._session_manager.fail_session(str(session.session_id), error_message=str(e))
            self._hooks.invoke_error("suspend", e)
            raise

        self._hooks.invoke_session_completed(session)
        self._audit("suspend", plugin_id, user_id, {"correlation_id": correlation_id, "reason": reason})
        return result  # type: ignore[return-value]

    # ── Load ────────────────────────────────────────────────────────────────

    def load_plugin(
        self,
        plugin_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> LoaderResult:
        """Load a plugin into memory."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.load", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "load")
            if not auth.allowed:
                raise PermissionError(f"Load not allowed: {auth.reason}")

        session = self._session_manager.create_session(plugin_id=plugin_id, operation="load", user_id=user_id)
        self._hooks.invoke_session_started(session)

        try:
            self._hooks.invoke_pre_load(plugin_id)  # type: ignore[arg-type]
            result = self._manager.load_plugin(plugin_id)
            if result is None:
                self._session_manager.fail_session(str(session.session_id), error_message="Plugin not found")
                raise ValueError(f"Plugin not found: {plugin_id}")
            if result.success:
                self._hooks.invoke_post_load(plugin_id)  # type: ignore[arg-type]
            self._session_manager.complete_session(str(session.session_id))
        except Exception as e:
            self._session_manager.fail_session(str(session.session_id), error_message=str(e))
            self._hooks.invoke_error("load", e)
            raise

        self._hooks.invoke_session_completed(session)
        self._audit("load", plugin_id, user_id, {"correlation_id": correlation_id})
        return result

    # ── Unload ──────────────────────────────────────────────────────────────

    def unload_plugin(
        self,
        plugin_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Plugin:
        """Unload a plugin from memory."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.unload", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "unload")
            if not auth.allowed:
                raise PermissionError(f"Unload not allowed: {auth.reason}")

        plugin = self._manager.get_plugin(plugin_id)
        if plugin is None:
            raise ValueError(f"Plugin not found: {plugin_id}")

        self._hooks.invoke_pre_unload(plugin)
        result = self._manager.unload_plugin(plugin_id)
        if result:
            self._hooks.invoke_post_unload(result)

        self._audit("unload", plugin_id, user_id, {"correlation_id": correlation_id})
        return result  # type: ignore[return-value]

    # ── Delete / Uninstall ──────────────────────────────────────────────────

    def uninstall_plugin(
        self,
        plugin_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Uninstall and remove a plugin."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.uninstall", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "delete")
            if not auth.allowed:
                raise PermissionError(f"Delete not allowed: {auth.reason}")

        self._hooks.invoke_pre_delete(plugin_id)
        success = self._manager.delete_plugin(plugin_id)
        self._hooks.invoke_post_delete(plugin_id, success)
        self._audit("delete", plugin_id, user_id, {"correlation_id": correlation_id, "success": success})
        return success

    # ── Sandbox ─────────────────────────────────────────────────────────────

    def create_sandbox(
        self,
        plugin_id: str,
        config: dict | None = None,
        user_id: str = "",
        correlation_id: str = "",
    ) -> PluginSandbox:
        """Create an execution sandbox for a plugin."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.create_sandbox", plugin_id=plugin_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "sandbox")
            if not auth.allowed:
                raise PermissionError(f"Sandbox creation not allowed: {auth.reason}")

        sandbox = self._manager.create_sandbox(plugin_id, config)
        if sandbox is None:
            raise ValueError(f"Plugin not found: {plugin_id}")

        self._hooks.invoke_sandbox_created(sandbox)
        self._audit("create_sandbox", plugin_id, user_id, {"correlation_id": correlation_id,
                                                             "sandbox_id": str(sandbox.sandbox_id)})
        return sandbox

    def destroy_sandbox(
        self,
        sandbox_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Destroy an execution sandbox."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.destroy_sandbox", sandbox_id=sandbox_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "sandbox")
            if not auth.allowed:
                raise PermissionError(f"Sandbox destruction not allowed: {auth.reason}")

        success = self._manager.destroy_sandbox(sandbox_id)
        if success:
            self._hooks.invoke_sandbox_destroyed(sandbox_id)
        self._audit("destroy_sandbox", sandbox_id, user_id, {"correlation_id": correlation_id, "success": success})
        return success

    def get_sandbox(
        self,
        sandbox_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> PluginSandbox | None:
        """Retrieve a sandbox by ID."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.get_sandbox", sandbox_id=sandbox_id, user_id=user_id)
        return self._manager.get_sandbox(sandbox_id)

    # ── Health & Metrics ────────────────────────────────────────────────────

    def health(self) -> PluginHealth:
        """Return the current health status of the plugin platform."""
        log.info("service.health")
        return self._manager.get_health()

    def get_metrics(self) -> PluginMetrics:
        """Return aggregated plugin platform metrics."""
        log.info("service.get_metrics")
        return self._manager.get_metrics()

    def get_session(self, session_id: str) -> PluginSession | None:
        """Get a session by ID."""
        return self._session_manager.get_session(session_id)
