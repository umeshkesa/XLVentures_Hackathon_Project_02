"""Tests for Rule Manager DTOs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from adip.rules.dtos import RuleEvaluationDTO, RuleRequestDTO, RuleResponseDTO
from adip.rules.enums import RuleDomain, RuleType


class TestRuleRequestDTO:
    def test_defaults(self) -> None:
        dto = RuleRequestDTO()
        assert dto.name == ""
        assert dto.description == ""
        assert dto.domain == RuleDomain.SYSTEM
        assert dto.rule_type == RuleType.BUSINESS
        assert dto.priority == 0
        assert dto.namespace == "default"
        assert dto.tags == []
        assert dto.conditions == []
        assert dto.actions == []
        assert dto.metadata == {}

    def test_custom_values(self) -> None:
        dto = RuleRequestDTO(
            name="Test Rule",
            description="A test rule",
            domain=RuleDomain.ENERGY,
            rule_type=RuleType.SAFETY,
            priority=50,
            owner_id="user-1",
            tags=["safety", "energy"],
            conditions=[{"field": "temperature", "operator": "gt", "value": "100"}],
            actions=[{"action_type": "alert", "parameters": {"channel": "slack"}}],
        )
        assert dto.name == "Test Rule"
        assert dto.domain == RuleDomain.ENERGY
        assert dto.rule_type == RuleType.SAFETY
        assert dto.priority == 50
        assert len(dto.tags) == 2
        assert len(dto.conditions) == 1
        assert len(dto.actions) == 1


class TestRuleResponseDTO:
    def test_defaults(self) -> None:
        now = datetime.now(UTC)
        dto = RuleResponseDTO(
            rule_id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )
        assert dto.name == ""
        assert dto.domain == RuleDomain.SYSTEM
        assert dto.rule_type == RuleType.BUSINESS
        assert dto.status == "DRAFT"
        assert dto.version == 1
        assert dto.priority == 0
        assert dto.enabled is True

    def test_custom_values(self) -> None:
        now = datetime.now(UTC)
        dto = RuleResponseDTO(
            rule_id=uuid.uuid4(),
            name="Active Rule",
            description="An active safety rule",
            domain=RuleDomain.ENERGY,
            rule_type=RuleType.SAFETY,
            status="ACTIVE",
            version=3,
            priority=100,
            enabled=True,
            created_at=now,
            updated_at=now,
        )
        assert dto.name == "Active Rule"
        assert dto.status == "ACTIVE"
        assert dto.version == 3
        assert dto.priority == 100

    def test_version_constraint(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(Exception):
            RuleResponseDTO(rule_id=uuid.uuid4(), created_at=now, updated_at=now, version=0)


class TestRuleEvaluationDTO:
    def test_defaults(self) -> None:
        dto = RuleEvaluationDTO()
        assert dto.domain == RuleDomain.SYSTEM
        assert dto.inputs == {}
        assert dto.attributes == {}
        assert dto.user_id == ""
        assert dto.namespace == "default"
        assert dto.correlation_id == ""
        assert dto.evaluation_strategy == "SEQUENTIAL"
        assert dto.limit_rules == 0

    def test_custom_values(self) -> None:
        dto = RuleEvaluationDTO(
            domain=RuleDomain.ENERGY,
            inputs={"temperature": 95},
            attributes={"asset_type": "turbine"},
            user_id="operator-1",
            evaluation_strategy="PRIORITY",
            limit_rules=10,
        )
        assert dto.domain == RuleDomain.ENERGY
        assert dto.inputs["temperature"] == 95
        assert dto.evaluation_strategy == "PRIORITY"
        assert dto.limit_rules == 10

    def test_limit_validation(self) -> None:
        with pytest.raises(Exception):
            RuleEvaluationDTO(limit_rules=-1)
