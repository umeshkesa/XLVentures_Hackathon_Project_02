"""IntegrationHooks — extension points for ADIP platform modules.

All hooks are no-op by default. Downstream modules (Planner,
Workflow Engine, Memory Manager, Knowledge Manager, Rule Manager,
Capability Registry, Agent Registry, Tool Registry, Evidence
Fusion Engine, Reasoning Engine, Recommendation Engine, Action
Engine) can attach callbacks at runtime without modifying the
Plugin Manager.

Only hook definitions — no business logic.
"""

from __future__ import annotations

from collections.abc import Callable

import structlog

from adip.plugins.contracts.models import Plugin, PluginDecision, PluginSandbox, PluginSession

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """Extension hooks for ADIP platform module integration.

    Each hook is a list of callables. Consumers register callbacks
    via the on_* methods. The PluginService invokes them at the
    appropriate points in the pipeline.
    """

    def __init__(self) -> None:
        self._pre_discover_hooks: list[Callable[[str], None]] = []
        self._post_discover_hooks: list[Callable[[Plugin], None]] = []
        self._pre_install_hooks: list[Callable[[Plugin], None]] = []
        self._post_install_hooks: list[Callable[[PluginDecision], None]] = []
        self._pre_load_hooks: list[Callable[[Plugin], None]] = []
        self._post_load_hooks: list[Callable[[Plugin], None]] = []
        self._pre_activate_hooks: list[Callable[[Plugin], None]] = []
        self._post_activate_hooks: list[Callable[[Plugin], None]] = []
        self._pre_suspend_hooks: list[Callable[[Plugin], None]] = []
        self._post_suspend_hooks: list[Callable[[Plugin], None]] = []
        self._pre_unload_hooks: list[Callable[[Plugin], None]] = []
        self._post_unload_hooks: list[Callable[[Plugin], None]] = []
        self._pre_delete_hooks: list[Callable[[str], None]] = []
        self._post_delete_hooks: list[Callable[[str, bool], None]] = []
        self._sandbox_created_hooks: list[Callable[[PluginSandbox], None]] = []
        self._sandbox_destroyed_hooks: list[Callable[[str], None]] = []
        self._session_started_hooks: list[Callable[[PluginSession], None]] = []
        self._session_completed_hooks: list[Callable[[PluginSession], None]] = []
        self._error_hooks: list[Callable[[str, Exception], None]] = []

    def on_pre_discover(self, callback: Callable[[str], None]) -> None:
        """Register a hook called before plugin discovery."""
        self._pre_discover_hooks.append(callback)

    def on_post_discover(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called after plugin discovery."""
        self._post_discover_hooks.append(callback)

    def on_pre_install(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called before plugin installation."""
        self._pre_install_hooks.append(callback)

    def on_post_install(self, callback: Callable[[PluginDecision], None]) -> None:
        """Register a hook called after plugin installation."""
        self._post_install_hooks.append(callback)

    def on_pre_load(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called before plugin loading."""
        self._pre_load_hooks.append(callback)

    def on_post_load(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called after plugin loading."""
        self._post_load_hooks.append(callback)

    def on_pre_activate(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called before plugin activation."""
        self._pre_activate_hooks.append(callback)

    def on_post_activate(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called after plugin activation."""
        self._post_activate_hooks.append(callback)

    def on_pre_suspend(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called before plugin suspension."""
        self._pre_suspend_hooks.append(callback)

    def on_post_suspend(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called after plugin suspension."""
        self._post_suspend_hooks.append(callback)

    def on_pre_unload(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called before plugin unloading."""
        self._pre_unload_hooks.append(callback)

    def on_post_unload(self, callback: Callable[[Plugin], None]) -> None:
        """Register a hook called after plugin unloading."""
        self._post_unload_hooks.append(callback)

    def on_pre_delete(self, callback: Callable[[str], None]) -> None:
        """Register a hook called before plugin deletion."""
        self._pre_delete_hooks.append(callback)

    def on_post_delete(self, callback: Callable[[str, bool], None]) -> None:
        """Register a hook called after plugin deletion."""
        self._post_delete_hooks.append(callback)

    def on_sandbox_created(self, callback: Callable[[PluginSandbox], None]) -> None:
        """Register a hook called when a sandbox is created."""
        self._sandbox_created_hooks.append(callback)

    def on_sandbox_destroyed(self, callback: Callable[[str], None]) -> None:
        """Register a hook called when a sandbox is destroyed."""
        self._sandbox_destroyed_hooks.append(callback)

    def on_session_started(self, callback: Callable[[PluginSession], None]) -> None:
        """Register a hook called when a plugin session starts."""
        self._session_started_hooks.append(callback)

    def on_session_completed(self, callback: Callable[[PluginSession], None]) -> None:
        """Register a hook called when a plugin session completes."""
        self._session_completed_hooks.append(callback)

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Register a hook called when an error occurs."""
        self._error_hooks.append(callback)

    def invoke_pre_discover(self, source: str) -> None:
        for hook in self._pre_discover_hooks:
            try:
                hook(source)
            except Exception:
                log.exception("hooks.pre_discover.error")

    def invoke_post_discover(self, plugin: Plugin) -> None:
        for hook in self._post_discover_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.post_discover.error")

    def invoke_pre_install(self, plugin: Plugin) -> None:
        for hook in self._pre_install_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.pre_install.error")

    def invoke_post_install(self, decision: PluginDecision) -> None:
        for hook in self._post_install_hooks:
            try:
                hook(decision)
            except Exception:
                log.exception("hooks.post_install.error")

    def invoke_pre_load(self, plugin: Plugin) -> None:
        for hook in self._pre_load_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.pre_load.error")

    def invoke_post_load(self, plugin: Plugin) -> None:
        for hook in self._post_load_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.post_load.error")

    def invoke_pre_activate(self, plugin: Plugin) -> None:
        for hook in self._pre_activate_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.pre_activate.error")

    def invoke_post_activate(self, plugin: Plugin) -> None:
        for hook in self._post_activate_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.post_activate.error")

    def invoke_pre_suspend(self, plugin: Plugin) -> None:
        for hook in self._pre_suspend_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.pre_suspend.error")

    def invoke_post_suspend(self, plugin: Plugin) -> None:
        for hook in self._post_suspend_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.post_suspend.error")

    def invoke_pre_unload(self, plugin: Plugin) -> None:
        for hook in self._pre_unload_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.pre_unload.error")

    def invoke_post_unload(self, plugin: Plugin) -> None:
        for hook in self._post_unload_hooks:
            try:
                hook(plugin)
            except Exception:
                log.exception("hooks.post_unload.error")

    def invoke_pre_delete(self, plugin_id: str) -> None:
        for hook in self._pre_delete_hooks:
            try:
                hook(plugin_id)
            except Exception:
                log.exception("hooks.pre_delete.error")

    def invoke_post_delete(self, plugin_id: str, success: bool) -> None:
        for hook in self._post_delete_hooks:
            try:
                hook(plugin_id, success)
            except Exception:
                log.exception("hooks.post_delete.error")

    def invoke_sandbox_created(self, sandbox: PluginSandbox) -> None:
        for hook in self._sandbox_created_hooks:
            try:
                hook(sandbox)
            except Exception:
                log.exception("hooks.sandbox_created.error")

    def invoke_sandbox_destroyed(self, sandbox_id: str) -> None:
        for hook in self._sandbox_destroyed_hooks:
            try:
                hook(sandbox_id)
            except Exception:
                log.exception("hooks.sandbox_destroyed.error")

    def invoke_session_started(self, session: PluginSession) -> None:
        for hook in self._session_started_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_started.error")

    def invoke_session_completed(self, session: PluginSession) -> None:
        for hook in self._session_completed_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_completed.error")

    def invoke_error(self, operation: str, error: Exception) -> None:
        for hook in self._error_hooks:
            try:
                hook(operation, error)
            except Exception:
                log.exception("hooks.error.error")


# Default global hooks instance
hooks: IntegrationHooks = IntegrationHooks()
