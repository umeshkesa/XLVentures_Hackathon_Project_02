"""Tests for MemoryDomain enum."""

from __future__ import annotations

from adip.memory.enums import MemoryDomain


class TestMemoryDomain:
    def test_domain_values(self) -> None:
        assert MemoryDomain.SYSTEM.value == "SYSTEM"
        assert MemoryDomain.PLANNER.value == "PLANNER"
        assert MemoryDomain.WORKFLOW.value == "WORKFLOW"
        assert MemoryDomain.KNOWLEDGE.value == "KNOWLEDGE"
        assert MemoryDomain.RULES.value == "RULES"
        assert MemoryDomain.EVIDENCE.value == "EVIDENCE"
        assert MemoryDomain.REASONING.value == "REASONING"
        assert MemoryDomain.RECOMMENDATION.value == "RECOMMENDATION"
        assert MemoryDomain.EXPLAINABILITY.value == "EXPLAINABILITY"
        assert MemoryDomain.ACTION.value == "ACTION"
        assert MemoryDomain.ENERGY.value == "ENERGY"
        assert MemoryDomain.CUSTOMER.value == "CUSTOMER"
        assert MemoryDomain.PLUGIN.value == "PLUGIN"

    def test_future_ready_domains(self) -> None:
        assert MemoryDomain.HEALTHCARE.value == "HEALTHCARE"
        assert MemoryDomain.FINANCE.value == "FINANCE"
        assert MemoryDomain.MANUFACTURING.value == "MANUFACTURING"

    def test_domain_is_string_enum(self) -> None:
        assert issubclass(MemoryDomain, str)

    def test_domain_membership(self) -> None:
        domains = {d.value for d in MemoryDomain}
        assert "SYSTEM" in domains
        assert "HEALTHCARE" in domains
        assert len(domains) == 16

    def test_domain_from_string(self) -> None:
        assert MemoryDomain("SYSTEM") == MemoryDomain.SYSTEM
        assert MemoryDomain("WORKFLOW") == MemoryDomain.WORKFLOW
        assert MemoryDomain("HEALTHCARE") == MemoryDomain.HEALTHCARE
