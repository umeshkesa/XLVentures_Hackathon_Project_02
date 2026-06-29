"""Tests for Phase 3.1 — Intelligent Content Classification."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from adip.data_import.classifier import (
    ContentCategory,
    ContentClassifier,
    ContentClassResult,
    ClassificationRegistry,
    TargetModule,
)
from adip.data_import.coordinator import ImportCoordinator


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def classifier() -> ContentClassifier:
    return ContentClassifier()


@pytest.fixture
def mini_classification_dataset(tmp_path: Path) -> Path:
    """Create a minimal dataset with diverse file types for classification testing."""
    root = tmp_path / "classify_test"
    dirs = [
        "customer_profiles",
        "operations/equipment_registry",
        "operations/incidents",
        "operations/maintenance",
        "operations/scada_logs",
        "operations/work_orders",
        "operations/inventory",
        "operations/weather_data",
        "customer_interactions/complaints",
        "customer_interactions/feedback",
        "customer_interactions/crm_updates",
        "customer_interactions/service_requests",
        "business/sla",
        "business/compliance",
        "business/business_rules",
        "business/recommendation_history",
        "knowledge_base/knowledge_articles",
        "knowledge_base/equipment_manuals",
        "operations/sensor_data",
        "operations/energy_reports",
        "scenarios/SCN001_Transformer_Overheating",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    (root / "customer_profiles" / "customers.csv").write_text(
        "customer_id,company_name,industry,location,contact_person\nCUS001,Test Corp,Energy,Hyderabad,John\n"
    )
    (root / "operations" / "equipment_registry" / "equipment_registry.csv").write_text(
        "asset_id,asset_name,asset_type,customer_id,facility\nAST001,Transformer A,Transformer,CUS001,PlantA\n"
    )
    (root / "operations" / "incidents" / "incident_reports.csv").write_text(
        "incident_id,asset_id,severity,incident_date,root_cause\nINC001,AST001,High,2026-06-01,Cooling failure\n"
    )
    (root / "operations" / "maintenance" / "maintenance_history.csv").write_text(
        "maintenance_id,asset_id,maintenance_type,date\nMNT001,AST001,Corrective,2026-06-02\n"
    )
    (root / "operations" / "scada_logs" / "alarm_logs.csv").write_text(
        "timestamp,asset_id,alarm_code,severity,message\n2026-06-01,AST001,ALM001,Warning,Temp high\n"
    )
    (root / "operations" / "work_orders" / "work_orders.csv").write_text(
        "work_order_id,asset_id,priority,issue_description,status\nWO001,AST001,High,Overheating,Open\n"
    )
    (root / "operations" / "inventory" / "spare_parts_inventory.csv").write_text(
        "part_id,part_name,asset_type,quantity_in_stock,reorder_level\nPART001,Cooling Fan,Transformer,10,5\n"
    )
    (root / "operations" / "weather_data" / "weather_india.csv").write_text(
        "city,lat,lon,temperature,humidity\nHyderabad,17.375,78.474,26,32\n"
    )
    (root / "customer_interactions" / "complaints" / "complaints.csv").write_text(
        "complaint_id,customer_id,date,severity,issue\nCMP001,CUS001,2026-06-01,High,Overheating\n"
    )
    (root / "customer_interactions" / "feedback" / "feedback.csv").write_text(
        "feedback_id,customer_id,date,rating,comments\nFB001,CUS001,2026-06-03,4,Good\n"
    )
    (root / "customer_interactions" / "crm_updates" / "crm_updates.csv").write_text(
        "crm_id,customer_id,date,update_type,notes\nCRM001,CUS001,2026-06-01,Status Change,Resolved\n"
    )
    (root / "customer_interactions" / "service_requests" / "service_requests.csv").write_text(
        "request_id,customer_id,request_date,request_type,description\nSR001,CUS001,2026-06-01,Inspection,High temp\n"
    )
    (root / "business" / "sla" / "sla_definitions.csv").write_text(
        "sla_id,sla_type,response_time_hours,resolution_time_hours\nSLA001,Premium,1,4\n"
    )
    (root / "business" / "compliance" / "compliance_requirements.csv").write_text(
        "compliance_id,standard,requirement,severity\nCOMP001,ISO 55000,PM every 6 months,High\n"
    )
    (root / "business" / "business_rules" / "rules.json").write_text(
        json.dumps([{"rule_id": "R001", "category": "Safety", "condition": "temp > 90", "action": "Shutdown", "severity": "Critical"}])
    )
    (root / "business" / "recommendation_history" / "recommendations.csv").write_text(
        "recommendation_id,incident_id,asset_id,recommendation\nREC001,INC001,AST001,Replace fan\n"
    )
    (root / "knowledge_base" / "knowledge_articles" / "energy_tips.txt").write_text("Energy saving tips")
    (root / "knowledge_base" / "equipment_manuals" / "transformer_manual.pdf").write_bytes(b"PDF content")
    (root / "operations" / "sensor_data" / "ai4i2020.csv").write_text(
        "UDI,Product ID,Type,Air temperature [K],Process temperature [K]\n1,M14860,M,298.1,308.6\n"
    )
    (root / "operations" / "energy_reports" / "floor1.csv").write_text(
        "Date,z1_Light(kW),z1_Plug(kW),z2_AC1(kW)\n2018-07-01,12.94,18.56,45.24\n"
    )
    (root / "scenarios" / "SCN001_Transformer_Overheating" / "incident_report.txt").write_text("Transformer overheated")
    (root / "scenarios" / "SCN001_Transformer_Overheating" / "customer_email.txt").write_text("Please help")
    (root / "scenarios" / "SCN001_Transformer_Overheating" / "outcome.json").write_text(
        json.dumps({"status": "Resolved"})
    )

    return root


# ===========================================================================
# Tests: ContentCategory & TargetModule enums
# ===========================================================================


class TestEnums:
    def test_content_category_values(self) -> None:
        assert ContentCategory.CUSTOMER_PROFILE == "CUSTOMER_PROFILE"
        assert ContentCategory.EQUIPMENT == "EQUIPMENT"
        assert ContentCategory.INCIDENT == "INCIDENT"
        assert ContentCategory.UNKNOWN == "UNKNOWN"

    def test_content_category_comprehensive(self) -> None:
        values = [m.value for m in ContentCategory]
        assert len(values) >= 30
        assert "UNKNOWN" in values
        assert "SENSOR_AI4I" in values
        assert "ENERGY_REPORT" in values

    def test_target_module_values(self) -> None:
        assert TargetModule.EVIDENCE == "EVIDENCE"
        assert TargetModule.KNOWLEDGE == "KNOWLEDGE"
        assert TargetModule.RULES == "RULES"
        assert TargetModule.ENERGY == "ENERGY"


# ===========================================================================
# Tests: ContentClassResult model
# ===========================================================================


class TestContentClassResult:
    def test_default_construction(self) -> None:
        result = ContentClassResult(
            category=ContentCategory.INCIDENT,
            confidence=0.95,
            target_modules=[TargetModule.EVIDENCE],
            file_path="/data/incidents.csv",
            source_name="incidents.csv",
            detected_by="csv_headers",
        )
        assert result.category == ContentCategory.INCIDENT
        assert result.confidence == 0.95
        assert result.target_modules == [TargetModule.EVIDENCE]
        assert result.detected_by == "csv_headers"

    def test_source_name_from_path(self) -> None:
        result = ContentClassResult(
            category=ContentCategory.EQUIPMENT,
            confidence=0.9,
            target_modules=[TargetModule.ENERGY],
            file_path="/some/path/equipment.csv",
        )
        assert result.source_name == "equipment.csv"

    def test_to_dict(self) -> None:
        result = ContentClassResult(
            category=ContentCategory.ALARM,
            confidence=0.85,
            target_modules=[TargetModule.EVIDENCE, TargetModule.ENERGY],
            file_path="/data/alarms.csv",
            detected_by="path_pattern",
            details={"pattern": "scada_logs/"},
        )
        d = result.to_dict()
        assert d["category"] == "ALARM"
        assert d["confidence"] == 0.85
        assert d["target_modules"] == ["EVIDENCE", "ENERGY"]
        assert d["detected_by"] == "path_pattern"

    def test_repr(self) -> None:
        result = ContentClassResult(
            category=ContentCategory.CUSTOMER_PROFILE,
            confidence=0.95,
            target_modules=[TargetModule.REFERENCE],
        )
        r = repr(result)
        assert "CUSTOMER_PROFILE" in r
        assert "0.95" in r

    def test_unknown_result(self) -> None:
        result = ContentClassResult(
            category=ContentCategory.UNKNOWN,
            confidence=0.1,
            target_modules=[TargetModule.EVIDENCE],
            file_path="/data/unknown.xyz",
        )
        assert result.category == ContentCategory.UNKNOWN
        assert result.confidence < 0.5


# ===========================================================================
# Tests: CSV Header Classification
# ===========================================================================


class TestCsvHeaderClassification:
    def test_classify_customers(self, classifier: ContentClassifier) -> None:
        headers = ["customer_id", "company_name", "industry", "location"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.CUSTOMER_PROFILE
        assert result.confidence > 0.7
        assert TargetModule.REFERENCE in result.target_modules

    def test_classify_incidents(self, classifier: ContentClassifier) -> None:
        headers = ["incident_id", "asset_id", "severity", "incident_date", "root_cause"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.INCIDENT
        assert TargetModule.EVIDENCE in result.target_modules

    def test_classify_equipment(self, classifier: ContentClassifier) -> None:
        headers = ["asset_id", "asset_name", "asset_type", "customer_id"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.EQUIPMENT
        assert TargetModule.ENERGY in result.target_modules

    def test_classify_complaints(self, classifier: ContentClassifier) -> None:
        headers = ["complaint_id", "customer_id", "date", "severity", "issue"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.COMPLAINT

    def test_classify_feedback(self, classifier: ContentClassifier) -> None:
        headers = ["feedback_id", "customer_id", "date", "rating", "feedback_category"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.FEEDBACK

    def test_classify_alarms(self, classifier: ContentClassifier) -> None:
        headers = ["timestamp", "asset_id", "alarm_code", "severity", "message"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.ALARM

    def test_classify_sla(self, classifier: ContentClassifier) -> None:
        headers = ["sla_id", "sla_type", "response_time_hours", "resolution_time_hours"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.SLA
        assert TargetModule.RULES in result.target_modules

    def test_classify_compliance(self, classifier: ContentClassifier) -> None:
        headers = ["compliance_id", "standard", "requirement", "severity"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.COMPLIANCE

    def test_classify_sensor_ai4i(self, classifier: ContentClassifier) -> None:
        headers = ["UDI", "Product ID", "Type", "Air temperature [K]", "Process temperature [K]"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.SENSOR_AI4I

    def test_classify_energy_report(self, classifier: ContentClassifier) -> None:
        headers = ["Date", "z1_Light(kW)", "z1_Plug(kW)", "z2_AC1(kW)"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.ENERGY_REPORT

    def test_classify_weather(self, classifier: ContentClassifier) -> None:
        headers = ["city", "lat", "lon", "temperature", "humidity"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.WEATHER

    def test_classify_spare_parts(self, classifier: ContentClassifier) -> None:
        headers = ["part_id", "part_name", "asset_type", "quantity_in_stock", "reorder_level"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.SPARE_PART

    def test_classify_unknown_headers(self, classifier: ContentClassifier) -> None:
        headers = ["foo", "bar", "baz", "qux"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.UNKNOWN

    def test_classify_empty_headers(self, classifier: ContentClassifier) -> None:
        result = classifier.classify_csv_headers([])
        assert result.category == ContentCategory.UNKNOWN

    def test_classify_record(self, classifier: ContentClassifier) -> None:
        row = {"incident_id": "INC001", "asset_id": "AST001", "severity": "High"}
        result = classifier.classify_record(row)
        assert result.category == ContentCategory.INCIDENT


# ===========================================================================
# Tests: File Path Classification
# ===========================================================================


class TestFilePathClassification:
    def test_classify_by_path_equipment(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "operations" / "equipment_registry" / "data.csv"
        result = classifier._classify_by_path(fpath)
        assert result.category == ContentCategory.EQUIPMENT
        assert result.confidence > 0.7

    def test_classify_by_path_incidents(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "operations" / "incidents" / "report.csv"
        result = classifier._classify_by_path(fpath)
        assert result.category == ContentCategory.INCIDENT

    def test_classify_by_path_knowledge(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "knowledge_base" / "knowledge_articles" / "article.txt"
        result = classifier._classify_by_path(fpath)
        assert result.category == ContentCategory.KNOWLEDGE_ARTICLE
        assert TargetModule.KNOWLEDGE in result.target_modules

    def test_classify_by_path_scenario(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "scenarios" / "SCN001_Transformer_Overheating" / "incident.txt"
        result = classifier._classify_by_path(fpath)
        assert result.category == ContentCategory.SCENARIO

    def test_classify_by_path_unknown(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "some_unknown_dir" / "random.txt"
        result = classifier._classify_by_path(fpath)
        assert result.category == ContentCategory.UNKNOWN


# ===========================================================================
# Tests: Full File Classification
# ===========================================================================


class TestFullFileClassification:
    def test_classify_csv_file_by_path(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "customer_profiles" / "customers.csv"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.CUSTOMER_PROFILE

    def test_classify_csv_file_by_headers(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "unknown_location" / "data.csv"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text("incident_id,asset_id,severity,incident_date,root_cause\nINC001,AST001,High,2026-06-01,Test\n")
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.INCIDENT
        assert result.detected_by.startswith("csv_headers")

    def test_classify_json_rules(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "business" / "business_rules" / "rules.json"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.BUSINESS_RULE
        assert TargetModule.RULES in result.target_modules

    def test_classify_txt_knowledge_article(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "knowledge_base" / "knowledge_articles" / "energy_tips.txt"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.KNOWLEDGE_ARTICLE
        assert TargetModule.KNOWLEDGE in result.target_modules

    def test_classify_pdf_manual(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "knowledge_base" / "equipment_manuals" / "transformer_manual.pdf"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.PDF_MANUAL
        assert TargetModule.KNOWLEDGE in result.target_modules

    def test_classify_ai4i_sensor_csv(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "operations" / "sensor_data" / "ai4i2020.csv"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.SENSOR_AI4I

    def test_classify_incident_csv(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "operations" / "incidents" / "incident_reports.csv"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.INCIDENT

    def test_classify_complaint_csv(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "customer_interactions" / "complaints" / "complaints.csv"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.COMPLAINT

    def test_classify_scenario_text(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        fpath = mini_classification_dataset / "scenarios" / "SCN001_Transformer_Overheating" / "incident_report.txt"
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.SCENARIO_INCIDENT

    def test_classify_unknown_extension(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "test.xyz"
        fpath.write_text("some data")
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.UNKNOWN
        assert result.confidence <= 0.2


# ===========================================================================
# Tests: Batch Classification & Routing
# ===========================================================================


class TestBatchClassification:
    def test_classify_directory(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        results = classifier.classify_directory(mini_classification_dataset)
        assert len(results) >= 20

    def test_classify_file_batch(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        files = [
            mini_classification_dataset / "customer_profiles" / "customers.csv",
            mini_classification_dataset / "operations" / "incidents" / "incident_reports.csv",
            mini_classification_dataset / "business" / "sla" / "sla_definitions.csv",
        ]
        results = classifier.classify_file_batch(files)
        assert len(results) == 3
        categories = [r.category for r in results]
        assert ContentCategory.CUSTOMER_PROFILE in categories
        assert ContentCategory.INCIDENT in categories
        assert ContentCategory.SLA in categories

    def test_get_classification_summary(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        results = classifier.classify_directory(mini_classification_dataset)
        summary = classifier.get_classification_summary(results)
        assert summary["total"] >= 20
        assert summary["high_confidence"] > 0
        assert summary["unknown"] >= 0

    def test_route_to_module_primary(self, classifier: ContentClassifier) -> None:
        result = ContentClassResult(
            category=ContentCategory.EQUIPMENT,
            confidence=0.9,
            target_modules=[TargetModule.ENERGY, TargetModule.REFERENCE],
        )
        assert classifier.route_to_module(result) == TargetModule.ENERGY

    def test_route_to_module_empty(self, classifier: ContentClassifier) -> None:
        result = ContentClassResult(
            category=ContentCategory.UNKNOWN,
            confidence=0.1,
            target_modules=[],
        )
        assert classifier.route_to_module(result) == TargetModule.EVIDENCE

    def test_route_all(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        results = classifier.classify_directory(mini_classification_dataset)
        routing = classifier.route_all(results)
        assert len(routing) > 0
        all_keys = set(routing.keys())
        assert "EVIDENCE" in all_keys or "KNOWLEDGE" in all_keys or "RULES" in all_keys or "ENERGY" in all_keys

    def test_unknown_file_fallback(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "unknown" / "file.dat"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text("some binary data")
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.UNKNOWN
        assert result.confidence <= 0.2


# ===========================================================================
# Tests: Coordinator Integration
# ===========================================================================


class TestCoordinatorClassification:
    def test_coordinator_classify_datasets(self, mini_classification_dataset: Path) -> None:
        coordinator = ImportCoordinator(mini_classification_dataset)
        result = coordinator.classify_datasets()
        assert result["total_files"] >= 20
        assert "summary" in result
        assert "classifications" in result
        assert result["summary"]["total"] >= 20

    def test_coordinator_classify_summary_breakdown(self, mini_classification_dataset: Path) -> None:
        coordinator = ImportCoordinator(mini_classification_dataset)
        result = coordinator.classify_datasets()
        summary = result["summary"]
        assert summary["high_confidence"] > 0
        assert "by_category" in summary
        assert "by_module" in summary
        by_cat = summary["by_category"]
        assert ContentCategory.CUSTOMER_PROFILE.value in by_cat
        assert ContentCategory.INCIDENT.value in by_cat


# ===========================================================================
# Tests: Edge Cases
# ===========================================================================


class TestClassifierEdgeCases:
    def test_classify_empty_directory(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        results = classifier.classify_directory(empty_dir)
        assert results == []

    def test_classify_nonexistent_directory(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        results = classifier.classify_directory(tmp_path / "does_not_exist")
        assert results == []

    def test_classify_case_insensitive_headers(self, classifier: ContentClassifier) -> None:
        headers = ["CUSTOMER_ID", "COMPANY_NAME", "INDUSTRY", "LOCATION"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.CUSTOMER_PROFILE
        assert result.confidence > 0.7

    def test_classify_partial_header_match(self, classifier: ContentClassifier) -> None:
        headers = ["incident_id", "asset_id", "random_field"]
        result = classifier.classify_csv_headers(headers)
        assert result.category == ContentCategory.INCIDENT

    def test_classify_record_with_extra_fields(self, classifier: ContentClassifier) -> None:
        row = {
            "complaint_id": "CMP001",
            "customer_id": "CUS001",
            "date": "2026-01-01",
            "severity": "High",
            "issue": "Problem",
            "extra_field": "ignored",
        }
        result = classifier.classify_record(row)
        assert result.category == ContentCategory.COMPLAINT

    def test_classify_json_outcome(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "scenarios" / "SCN001" / "outcome.json"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(json.dumps({"status": "Done"}))
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.SCENARIO_OUTCOME

    def test_classify_by_filename_keyword(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "some_dir" / "incident_report.txt"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text("Incident report content")
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.SCENARIO_INCIDENT

    def test_classification_registry_defaults(self) -> None:
        registry = ClassificationRegistry()
        assert len(registry.HEADER_SIGNATURES) >= 20
        assert len(registry.PATH_SIGNATURES) >= 25
        assert len(registry.EXTENSION_SIGNATURES) >= 4

    def test_routing_no_duplicates(self, classifier: ContentClassifier, mini_classification_dataset: Path) -> None:
        results = classifier.classify_directory(mini_classification_dataset)
        all_paths = [r.file_path for r in results]
        assert len(all_paths) == len(set(all_paths))

    def test_classify_json_rules_by_filename(self, classifier: ContentClassifier, tmp_path: Path) -> None:
        fpath = tmp_path / "some_dir" / "rules_config.json"
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(json.dumps([{"rule": "test"}]))
        result = classifier.classify_file(fpath)
        assert result.category == ContentCategory.BUSINESS_RULE


# ===========================================================================
# Tests: PostImportPipeline classification integration
# ===========================================================================


class TestPipelineClassification:
    def test_classify_and_route_in_pipeline(self, mini_classification_dataset: Path) -> None:
        from adip.data_import.services.post_import import PostImportPipeline

        pipeline = PostImportPipeline()
        result = pipeline.classify_and_route(mini_classification_dataset)
        assert result["total"] >= 20
        assert "summary" in result
        assert "routing" in result
        assert "results" in result

    def test_classify_and_route_has_high_confidence(self, mini_classification_dataset: Path) -> None:
        from adip.data_import.services.post_import import PostImportPipeline

        pipeline = PostImportPipeline()
        result = pipeline.classify_and_route(mini_classification_dataset)
        summary = result["summary"]
        assert summary["high_confidence"] > 0

    def test_classify_and_route_routing_keys(self, mini_classification_dataset: Path) -> None:
        from adip.data_import.services.post_import import PostImportPipeline

        pipeline = PostImportPipeline()
        result = pipeline.classify_and_route(mini_classification_dataset)
        routing = result["routing"]
        assert "KNOWLEDGE" in routing or "RULES" in routing or "EVIDENCE" in routing or "ENERGY" in routing
