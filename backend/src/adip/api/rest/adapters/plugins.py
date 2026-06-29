"""Plugins service adapter."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter


class PluginsAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "plugins"

    def install(self, plugin_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"plugin_id": plugin_id, "status": "installed", "params": params or {}})

    def uninstall(self, plugin_id: str) -> Any:
        return self._success_response(data={"plugin_id": plugin_id, "status": "uninstalled"})

    def get_plugin(self, plugin_id: str) -> Any:
        return self._success_response(data={"plugin_id": plugin_id, "status": "active", "version": "1.0.0"})

    def list_plugins(self) -> Any:
        return self._success_response(data={"plugins": [], "total": 0})
