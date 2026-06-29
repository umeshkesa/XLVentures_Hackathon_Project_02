from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import structlog

from adip.data_import.classifier import ContentCategory, ContentClassifier, ContentClassResult, TargetModule
from adip.data_import.deduplicators import InMemoryDeduplicator
from adip.data_import.importers import (
    BusinessRulesImporter,
    KnowledgeImporter,
    OperationsImporter,
    ReferenceImporter,
    ScenarioImporter,
    TimeSeriesImporter,
)
from adip.data_import.statistics import ImportReport, ImportStats

log = structlog.get_logger(__name__)


class ImportCoordinator:
    """Orchestrates the full dataset import across all phases in dependency order."""

    def __init__(self, dataset_root: str | Path) -> None:
        self.dataset_root = Path(dataset_root).resolve()
        self.dedup = InMemoryDeduplicator()
        self.report = ImportReport()
        self._phases: list[tuple[str, Any]] = []

    def run_all(self) -> ImportReport:
        """Run all import phases in dependency order."""
        self.report.session_id = str(uuid.uuid4())
        self.report.timer.start()

        log.info("import.coordinator.start", dataset_root=str(self.dataset_root))

        phase_order = [
            ("REFERENCE", ReferenceImporter),
            ("OPERATIONS", OperationsImporter),
            ("BUSINESS_RULES", BusinessRulesImporter),
            ("KNOWLEDGE", KnowledgeImporter),
            ("TIME_SERIES", TimeSeriesImporter),
            ("SCENARIOS", ScenarioImporter),
        ]

        for phase_name, importer_cls in phase_order:
            importer = importer_cls(self.dataset_root, deduplicator=self.dedup)
            try:
                stats = importer.run()
            except Exception as exc:
                log.exception("import.phase.failed", phase=phase_name)
                stats = ImportStats(phase=phase_name)
                stats.validation_errors = -1
                log.error("import.phase.error", phase=phase_name, error=str(exc))
            self.report.add_phase_stats(stats)

        self.report.timer.stop()
        log.info("import.coordinator.complete", report=self.report.global_stats.to_dict())
        return self.report

    def run_all_with_integration(self) -> tuple[ImportReport, dict[str, Any]]:
        """Run all import phases and then trigger the post-import integration pipeline."""
        report = self.run_all()
        try:
            from adip.data_import.services.post_import import PostImportPipeline
            pipeline = PostImportPipeline()
            integration_results = pipeline.run_all(
                dataset_root=self.dataset_root,
                imported_summary=report.phase_stats,
            )
        except Exception as exc:
            log.exception("integration.pipeline.failed")
            integration_results = {"error": str(exc)}
        return report, integration_results

    def classify_datasets(self) -> dict[str, Any]:
        """Classify all discoverable dataset files and return the classification summary."""
        classifier = ContentClassifier()

        all_files: list[Path] = []
        checks = {
            "REFERENCE": [
                "customer_profiles/customers.csv",
                "operations/facility_profiles/facilities.csv",
                "operations/equipment_registry/equipment_registry.csv",
                "operations/technician_profiles/technicians.csv",
            ],
            "OPERATIONS": [
                "operations/incidents/incident_reports.csv",
                "operations/work_orders/work_orders.csv",
                "operations/maintenance/maintenance_history.csv",
                "operations/scada_logs/alarm_logs.csv",
                "operations/inventory/spare_parts_inventory.csv",
                "operations/weather_data/weather_india.csv",
                "customer_interactions/service_requests/service_requests.csv",
                "customer_interactions/complaints/complaints.csv",
                "customer_interactions/feedback/feedback.csv",
                "customer_interactions/crm_updates/crm_updates.csv",
            ],
            "BUSINESS_RULES": [
                "business/sla/sla_definitions.csv",
                "business/compliance/compliance_requirements.csv",
                "business/contracts/contracts.csv",
                "business/business_rules/rules.json",
                "business/recommendation_history/recommendations.csv",
            ],
            "TIME_SERIES": [
                "operations/sensor_data/ai4i2020.csv",
                "operations/sensor_data/ai4i2020_sample.csv",
            ],
        }
        for paths in checks.values():
            for p in paths:
                full = self.dataset_root / p
                if full.is_file():
                    all_files.append(full)

        knowledge_dirs = [
            "knowledge_base/knowledge_articles",
            "knowledge_base/playbooks",
            "knowledge_base/sops",
            "knowledge_base/best_practices",
            "knowledge_base/equipment_manuals",
        ]
        for d in knowledge_dirs:
            full_dir = self.dataset_root / d
            if full_dir.is_dir():
                for f in sorted(full_dir.iterdir()):
                    if f.is_file():
                        all_files.append(f)

        scenario_dirs = [
            "scenarios/SCN001_Transformer_Overheating",
            "scenarios/SCN002_Cooling_Failure",
            "scenarios/SCN003_Wind_Vibration",
            "scenarios/SCN004_Power_Spike",
            "scenarios/SCN005_SLA_Breach",
        ]
        for d in scenario_dirs:
            full_dir = self.dataset_root / d
            if full_dir.is_dir():
                for f in sorted(full_dir.iterdir()):
                    if f.is_file():
                        all_files.append(f)

        energy_dirs = [
            "operations/energy_reports",
        ]
        for d in energy_dirs:
            full_dir = self.dataset_root / d
            if full_dir.is_dir():
                for f in sorted(full_dir.iterdir()):
                    if f.is_file():
                        all_files.append(f)

        results = [classifier.classify_file(f) for f in all_files]
        summary = classifier.get_classification_summary(results)

        return {
            "total_files": len(results),
            "summary": summary,
            "classifications": [r.to_dict() for r in results],
        }

    def run_phase(self, phase_name: str) -> ImportReport:
        """Run a single import phase."""
        self.report.session_id = str(uuid.uuid4())
        self.report.timer.start()

        phase_map = {
            "REFERENCE": ReferenceImporter,
            "OPERATIONS": OperationsImporter,
            "BUSINESS_RULES": BusinessRulesImporter,
            "KNOWLEDGE": KnowledgeImporter,
            "TIME_SERIES": TimeSeriesImporter,
            "SCENARIOS": ScenarioImporter,
        }

        importer_cls = phase_map.get(phase_name.upper())
        if importer_cls is None:
            raise ValueError(
                f"Unknown phase: {phase_name}. "
                f"Available: {list(phase_map.keys())}"
            )

        importer = importer_cls(self.dataset_root, deduplicator=self.dedup)
        try:
            stats = importer.run()
        except Exception as exc:
            log.exception("import.phase.failed", phase=phase_name)
            stats = ImportStats(phase=phase_name)
            stats.validation_errors = -1

        self.report.add_phase_stats(stats)
        self.report.timer.stop()
        return self.report

    def list_datasets(self) -> dict[str, Any]:
        """List all discoverable dataset files under the root."""
        result: dict[str, Any] = {
            "dataset_root": str(self.dataset_root),
            "phases": {},
        }
        checks = {
            "REFERENCE": [
                "customer_profiles/customers.csv",
                "operations/facility_profiles/facilities.csv",
                "operations/equipment_registry/equipment_registry.csv",
                "operations/technician_profiles/technicians.csv",
            ],
            "OPERATIONS": [
                "operations/incidents/incident_reports.csv",
                "operations/work_orders/work_orders.csv",
                "operations/maintenance/maintenance_history.csv",
                "operations/scada_logs/alarm_logs.csv",
                "operations/inventory/spare_parts_inventory.csv",
                "operations/weather_data/weather_india.csv",
                "customer_interactions/service_requests/service_requests.csv",
                "customer_interactions/complaints/complaints.csv",
                "customer_interactions/feedback/feedback.csv",
                "customer_interactions/crm_updates/crm_updates.csv",
            ],
            "BUSINESS_RULES": [
                "business/sla/sla_definitions.csv",
                "business/compliance/compliance_requirements.csv",
                "business/contracts/contracts.csv",
                "business/business_rules/rules.json",
                "business/recommendation_history/recommendations.csv",
            ],
            "KNOWLEDGE": [
                "knowledge_base/knowledge_articles/",
                "knowledge_base/playbooks/",
                "knowledge_base/sops/",
                "knowledge_base/best_practices/",
                "knowledge_base/equipment_manuals/",
            ],
            "TIME_SERIES": [
                "operations/sensor_data/ai4i2020.csv",
                "operations/energy_reports/CU-BEMS dataset files/",
            ],
            "SCENARIOS": [
                "scenarios/SCN001_Transformer_Overheating/",
                "scenarios/SCN002_Cooling_Failure/",
                "scenarios/SCN003_Wind_Vibration/",
                "scenarios/SCN004_Power_Spike/",
                "scenarios/SCN005_SLA_Breach/",
            ],
        }
        for phase, paths in checks.items():
            found = []
            missing = []
            for p in paths:
                full = self.dataset_root / p
                if full.exists():
                    found.append(p)
                else:
                    missing.append(p)
            result["phases"][phase] = {
                "found": found,
                "missing": missing,
            }
        result["all_found"] = all(
            len(v["missing"]) == 0 for v in result["phases"].values()
        )
        return result
