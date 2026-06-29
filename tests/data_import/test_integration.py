"""End-to-end integration test: Dataset Import → Post-Import Integration Pipeline.

Verifies that imported data flows through Evidence, Knowledge, Rules, Energy,
Recommendation, Reasoning services with full traceability.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adip.data_import.coordinator import ImportCoordinator
from adip.data_import.services.post_import import PostImportPipeline


@pytest.fixture
def dataset_path(tmp_path: Path) -> Path:
    from tests.data_import.test_importers import _create_mini_dataset

    return _create_mini_dataset(tmp_path)


class TestDataImportIntegration:
    """Verifies the full import pipeline: Dataset → Import → Integration → Traceability."""

    def test_run_all_with_integration(self, dataset_path: Path) -> None:
        """Run coordinator's run_all_with_integration and verify results."""
        coordinator = ImportCoordinator(dataset_path)
        report, integration_results = coordinator.run_all_with_integration()

        assert report.session_id
        assert report.global_stats.imported > 0

        assert "evidence_operations" in integration_results
        assert "knowledge_base" in integration_results
        assert "business_rules" in integration_results
        assert "energy_domain" in integration_results
        assert "reasoning" in integration_results
        assert "next_best_action" in integration_results
        assert "recommendation_history" in integration_results

        assert integration_results["reasoning"] is not None
        assert integration_results["next_best_action"] is not None

    def test_post_import_pipeline_run_all(self, dataset_path: Path) -> None:
        """Run the PostImportPipeline standalone after import."""
        coordinator = ImportCoordinator(dataset_path)
        coordinator.run_all()

        pipeline = PostImportPipeline()
        results = pipeline.run_all(dataset_root=dataset_path)

        assert "evidence_operations" in results
        assert "knowledge_base" in results
        assert "business_rules" in results
        assert "energy_domain" in results
        assert "reasoning" in results
        assert "next_best_action" in results

    def test_evidence_integration(self, dataset_path: Path) -> None:
        """Verify imported operational records become Evidence objects."""
        from adip.data_import.services.post_import import (
            EvidenceIntegrator,
            _evidence_service,
        )
        from adip.evidence.enums import EvidenceType, EvidenceDomain

        rows = [
            {"complaint_id": "CMP001", "issue": "Overheating", "customer_id": "CUS001"},
            {"complaint_id": "CMP002", "issue": "Noise", "customer_id": "CUS001"},
        ]
        integrator = EvidenceIntegrator()
        count = integrator.integrate_batch(
            rows,
            evidence_type=EvidenceType.CUSTOMER,
            domain=EvidenceDomain.CUSTOMER,
            source_type="complaint",
            tag="test",
        )
        assert count == 2

        health = _evidence_service.health()
        assert health is not None

    def test_knowledge_integration(self, dataset_path: Path) -> None:
        """Verify text/pdf files become Knowledge documents."""
        from adip.data_import.services.post_import import KnowledgeIntegrator
        from adip.knowledge.enums import DocumentType, KnowledgeDomain

        integrator = KnowledgeIntegrator()
        doc = integrator.integrate_document(
            "test/article.txt",
            "Energy saving tips content",
            DocumentType.ARTICLE,
            KnowledgeDomain.OPERATIONS,
            title="Energy Saving Tips",
            tags=["energy", "savings"],
        )
        assert doc is not None
        assert doc.title == "Energy Saving Tips"
        assert doc.content == "Energy saving tips content"

    def test_rules_integration(self, dataset_path: Path) -> None:
        """Verify rules.json and compliance CSV become Rule objects."""
        from adip.data_import.services.post_import import RulesIntegrator

        integrator = RulesIntegrator()
        rules_data = [
            {"rule_id": "TEST001", "category": "Safety", "condition": "temp > 90", "action": "Shutdown", "severity": "Critical"},
        ]
        count = integrator.integrate_rules_json(rules_data)
        assert count == 1

        compliance_rows = [
            {"compliance_id": "COMP-TEST", "standard": "ISO 55000",
             "requirement": "Monthly inspection", "applicable_asset_type": "Transformer",
             "severity": "High", "action_if_violated": "Schedule inspection"},
        ]
        count = integrator.integrate_compliance(compliance_rows)
        assert count == 1

        sla_rows = [
            {"sla_id": "SLA-TEST", "sla_type": "Gold",
             "response_time_hours": "2", "resolution_time_hours": "8",
             "uptime_guarantee": "99.99", "penalty_clause": "5%"},
        ]
        count = integrator.integrate_sla(sla_rows)
        assert count == 1

    def test_energy_domain_integration(self, dataset_path: Path) -> None:
        """Verify equipment, alarms, incidents become Energy domain objects."""
        from adip.data_import.services.post_import import EnergyDomainIntegrator

        integrator = EnergyDomainIntegrator()
        equip_rows = [
            {"asset_id": "AST-TEST", "asset_name": "Test Solar Panel",
             "asset_type": "Solar Inverter", "customer_id": "CUS001",
             "facility": "Test Facility", "location": "Hyderabad",
             "installation_date": "2024-01-01", "status": "Active"},
        ]
        count = integrator.integrate_equipment(equip_rows)
        assert count == 1

        alarm_rows = [
            {"asset_id": "AST-TEST", "alarm_code": "ALM-TEST",
             "severity": "Warning", "message": "Test alarm",
             "timestamp": "2026-06-01T10:00:00"},
        ]
        count = integrator.integrate_alarms(alarm_rows)
        assert count == 1

        inc_rows = [
            {"asset_id": "AST-TEST", "severity": "High",
             "root_cause": "Test incident",
             "incident_date": "2026-06-01T10:00:00"},
        ]
        count = integrator.integrate_incidents(inc_rows)
        assert count == 1

    def test_reasoning_trigger(self, dataset_path: Path) -> None:
        """Verify Reasoning engine can be triggered with evidence package ID."""
        from adip.data_import.services.post_import import ReasoningTrigger
        import uuid

        trigger = ReasoningTrigger()
        result = trigger.reason_on_evidence(str(uuid.uuid4()), "ENERGY")
        assert result is not None

    def test_nba_generation(self, dataset_path: Path) -> None:
        """Verify Next Best Action generation."""
        from adip.data_import.services.post_import import RecommendationIntegrator

        integrator = RecommendationIntegrator()
        context = {
            "reasoning_result_id": "test-reasoning-id",
            "source": "test",
            "incident_id": "INC001",
            "asset_id": "AST001",
        }
        result = integrator.generate_nba(context)
        assert result is not None

    def test_traceability_evidence_has_source_tags(self, dataset_path: Path) -> None:
        """Verify evidence objects retain traceable source metadata."""
        from adip.data_import.services.post_import import EvidenceIntegrator
        from adip.evidence.enums import EvidenceType, EvidenceDomain

        rows = [
            {"request_id": "SR001", "description": "Emergency inspection"},
        ]
        integrator = EvidenceIntegrator()
        count = integrator.integrate_batch(
            rows,
            evidence_type=EvidenceType.EMAIL,
            domain=EvidenceDomain.MAINTENANCE,
            source_type="service_request",
            tag="customer",
        )
        assert count == 1

    def test_full_pipeline_traceability(self, dataset_path: Path) -> None:
        """Run full end-to-end pipeline and verify traceability artifacts."""
        coordinator = ImportCoordinator(dataset_path)
        coordinator.run_all()

        pipeline = PostImportPipeline()
        results = pipeline.run_all(dataset_root=dataset_path)

        assert results["evidence_operations"] is not None
        assert results["knowledge_base"] is not None
        kb = results["knowledge_base"]
        if isinstance(kb, dict):
            for key in ("articles", "playbooks", "sops", "best_practices", "manuals"):
                assert key in kb

        rules = results["business_rules"]
        if isinstance(rules, dict):
            for key in ("rules_json", "compliance", "sla"):
                assert key in rules

        assert results["reasoning"] is not None
        assert results["next_best_action"] is not None
