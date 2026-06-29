"""Registry domain service adapter."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter


class RegistryAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "registry"

    def register(self, component: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"registry_id": "reg-001", "status": "registered", "component": component or {}})

    def unregister(self, registry_id: str) -> Any:
        return self._success_response(data={"registry_id": registry_id, "status": "unregistered"})

    def get_entry(self, registry_id: str) -> Any:
        return self._success_response(data={"registry_id": registry_id, "status": "active"})

    def search(self, query: str) -> Any:
        return self._success_response(data={"query": query, "results": [], "total": 0})
