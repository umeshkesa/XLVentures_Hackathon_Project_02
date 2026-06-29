"""Memory service adapter."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter


class MemoryAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "memory"

    def store(self, key: str, value: Any) -> Any:
        return self._success_response(data={"key": key, "status": "stored"})

    def retrieve(self, key: str) -> Any:
        return self._success_response(data={"key": key, "value": None})

    def search(self, query: str) -> Any:
        return self._success_response(data={"query": query, "results": [], "total": 0})

    def delete(self, key: str) -> Any:
        return self._success_response(data={"key": key, "status": "deleted"})
