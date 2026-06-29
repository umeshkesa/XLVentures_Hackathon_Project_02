"""Rules service adapter."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter


class RulesAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "rules"

    def evaluate(self, rule_id: str, context: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"rule_id": rule_id, "result": "allowed", "context": context or {}})

    def create_rule(self, rule: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"rule_id": "rule-001", "status": "created", "rule": rule or {}})

    def get_rule(self, rule_id: str) -> Any:
        return self._success_response(data={"rule_id": rule_id, "status": "active", "conditions": [], "actions": []})

    def list_rules(self) -> Any:
        return self._success_response(data={"rules": [], "total": 0})

    def delete_rule(self, rule_id: str) -> Any:
        return self._success_response(data={"rule_id": rule_id, "status": "deleted"})
