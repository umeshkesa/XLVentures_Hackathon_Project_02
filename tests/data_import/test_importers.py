from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from adip.data_import.importers.business_rules import BusinessRulesImporter
from adip.data_import.importers.knowledge import KnowledgeImporter
from adip.data_import.importers.operations import OperationsImporter
from adip.data_import.importers.reference import ReferenceImporter
from adip.data_import.importers.scenarios import ScenarioImporter
from adip.data_import.importers.timeseries import TimeSeriesImporter


def _create_mini_dataset(tmp_path: Path) -> Path:
    root = tmp_path / "adip_dataset"
    dirs = [
        "customer_profiles",
        "operations/facility_profiles",
        "operations/equipment_registry",
        "operations/technician_profiles",
        "operations/incidents",
        "operations/work_orders",
        "operations/maintenance",
        "operations/scada_logs",
        "operations/inventory",
        "operations/weather_data",
        "operations/sensor_data",
        "operations/energy_reports/CU-BEMS dataset files",
        "customer_interactions/service_requests",
        "customer_interactions/complaints",
        "customer_interactions/feedback",
        "customer_interactions/crm_updates",
        "business/sla",
        "business/compliance",
        "business/contracts",
        "business/business_rules",
        "business/recommendation_history",
        "knowledge_base/knowledge_articles",
        "knowledge_base/playbooks",
        "knowledge_base/sops",
        "knowledge_base/best_practices",
        "knowledge_base/equipment_manuals",
        "scenarios/SCN001_Transformer_Overheating",
        "scenarios/SCN002_Cooling_Failure",
        "scenarios/SCN003_Wind_Vibration",
        "scenarios/SCN004_Power_Spike",
        "scenarios/SCN005_SLA_Breach",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    (root / "customer_profiles/customers.csv").write_text(
        "customer_id,company_name,industry,location,contact_person,contact_email,phone,contract_start,contract_end,sla_type,status\n"
        "CUS001,Test Corp,Energy,Hyderabad,John,john@test.com,123,2025-01-01,2027-12-31,Premium,Active\n"
    )
    (root / "operations/facility_profiles/facilities.csv").write_text(
        "facility_id,facility_name,customer_id,location,facility_type,total_area_sqft,asset_count\n"
        "FAC001,Test Facility,CUS001,Hyderabad,Plant,50000,10\n"
    )
    (root / "operations/equipment_registry/equipment_registry.csv").write_text(
        "asset_id,asset_name,asset_type,customer_id,facility,location,installation_date,status,last_maintenance_date\n"
        "AST001,Test Transformer,Transformer,CUS001,Facility,Hyderabad,2020-01-01,Active,2026-01-01\n"
    )
    (root / "operations/technician_profiles/technicians.csv").write_text(
        "technician_id,name,specialty,certification_level,availability_status,assigned_region,experience_years,contact\n"
        "TECH001,John Doe,Transformer,Level 3,Available,North,10,john@tech.com\n"
    )
    (root / "operations/incidents/incident_reports.csv").write_text(
        "incident_id,asset_id,customer_id,severity,incident_date,root_cause,downtime_hours,energy_loss_kwh,resolution,status\n"
        "INC001,AST001,CUS001,High,2026-06-01,Cooling fan failure,6,1200,Replaced fan,Resolved\n"
    )
    (root / "operations/work_orders/work_orders.csv").write_text(
        "work_order_id,asset_id,customer_id,technician_id,priority,status,issue_description,created_date,scheduled_date,completion_date,cost\n"
        "WO001,AST001,CUS001,TECH001,High,Closed,Overheating,2026-06-01,2026-06-01,2026-06-02,25000\n"
    )
    (root / "operations/maintenance/maintenance_history.csv").write_text(
        "maintenance_id,asset_id,work_order_id,maintenance_type,technician_id,date,description,outcome,next_due_date,cost\n"
        "MNT001,AST001,WO001,Corrective,TECH001,2026-06-02,Replaced fan,Completed,2026-12-02,25000\n"
    )
    (root / "operations/scada_logs/alarm_logs.csv").write_text(
        "timestamp,asset_id,alarm_code,severity,message,operator_action,status\n"
        "2026-06-01 10:15:00,AST001,ALM001,Warning,Temp exceeded,Monitor,Closed\n"
    )
    (root / "operations/inventory/spare_parts_inventory.csv").write_text(
        "part_id,part_name,asset_type,quantity_in_stock,reorder_level,vendor,lead_time_days,unit_cost,status\n"
        "PART001,Cooling Fan,Transformer,12,5,ABB,7,15000,Available\n"
    )
    (root / "operations/weather_data/weather_india.csv").write_text(
        "city,lat,lon,temperature,weather_code,wind_speed,wind_dir,pressure,humidity,pm2_5,pm10\n"
        "Hyderabad,17.375,78.474,26,143,10,81,1015,32,28.85,31.45\n"
    )
    (root / "customer_interactions/service_requests/service_requests.csv").write_text(
        "request_id,customer_id,asset_id,request_date,request_type,priority,status,description\n"
        "SR001,CUS001,AST001,2026-06-01,Emergency Inspection,Critical,Open,High temperature\n"
    )
    (root / "customer_interactions/complaints/complaints.csv").write_text(
        "complaint_id,customer_id,date,severity,issue,status,resolution\n"
        "CMP001,CUS001,2026-06-01,High,Overheating,Open,Pending\n"
    )
    (root / "customer_interactions/feedback/feedback.csv").write_text(
        "feedback_id,customer_id,date,rating,feedback_category,comments,action_taken\n"
        "FB001,CUS001,2026-06-03,4,Service Quality,Good,Recorded\n"
    )
    (root / "customer_interactions/crm_updates/crm_updates.csv").write_text(
        "crm_id,customer_id,date,update_type,priority,notes,assigned_team,status\n"
        "CRM001,CUS001,2026-06-01,Incident Escalation,High,Issue escalated,Engineering,Open\n"
    )
    (root / "business/sla/sla_definitions.csv").write_text(
        "sla_id,sla_type,response_time_hours,resolution_time_hours,uptime_guarantee,penalty_clause,priority_support\n"
        "SLA001,Premium,1,4,99.99,10% credit,Yes\n"
    )
    (root / "business/compliance/compliance_requirements.csv").write_text(
        "compliance_id,standard,requirement,applicable_asset_type,severity,action_if_violated\n"
        "COMP001,ISO 55000,Preventive maintenance every 6 months,Transformer,High,Schedule maintenance\n"
    )
    (root / "business/contracts/contracts.csv").write_text(
        "contract_id,customer_id,contract_type,start_date,end_date,contract_value_usd,sla_type,status,renewal_option\n"
        "CON001,CUS001,Enterprise,2025-01-01,2027-12-31,500000,Premium,Active,Automatic\n"
    )
    (root / "business/business_rules/rules.json").write_text(
        json.dumps([{"rule_id": "RULE001", "category": "Safety", "condition": "temp > 90", "action": "Shutdown", "severity": "Critical"}])
    )
    (root / "business/recommendation_history/recommendations.csv").write_text(
        "recommendation_id,incident_id,asset_id,recommendation,confidence_score,decision,outcome,lessons_learned,date\n"
        "REC001,INC001,AST001,Replace fan,0.92,Approved,Successful,Root cause found,2026-06-02\n"
    )
    (root / "knowledge_base/knowledge_articles/test_article.txt").write_text("Test knowledge article content")
    (root / "knowledge_base/playbooks/test_playbook.txt").write_text("Test playbook content")
    (root / "knowledge_base/sops/test_sop.txt.txt").write_text("Test SOP content")
    (root / "knowledge_base/equipment_manuals/test_manual.pdf").write_bytes(b"PDF content")
    (root / "scenarios/SCN001_Transformer_Overheating/incident_report.txt").write_text("Incident report content")
    (root / "scenarios/SCN001_Transformer_Overheating/customer_email.txt").write_text("Email content")
    (root / "scenarios/SCN001_Transformer_Overheating/outcome.json").write_text(
        json.dumps({"status": "Successful", "action_taken": "Replaced fan", "downtime_hours": 6})
    )
    (root / "scenarios/SCN001_Transformer_Overheating/recommendation.json").write_text(
        json.dumps({"incident_id": "INC001", "asset_id": "AST001", "recommendation": "Replace fan", "confidence_score": 0.92})
    )

    for scn_num in ["SCN002_Cooling_Failure", "SCN003_Wind_Vibration", "SCN004_Power_Spike", "SCN005_SLA_Breach"]:
        (root / f"scenarios/{scn_num}/incident_report.txt").write_text("Incident report")
        (root / f"scenarios/{scn_num}/customer_email.txt").write_text("Email")
        (root / f"scenarios/{scn_num}/outcome.json").write_text(json.dumps({"status": "Done"}))
        (root / f"scenarios/{scn_num}/recommendation.json").write_text(json.dumps({"recommendation": "Fix"}))

    (root / "operations/sensor_data/ai4i2020.csv").write_text(
        "UDI,Product ID,Type,Air temperature [K],Process temperature [K],Rotational speed [rpm],Torque [Nm],Tool wear [min],Machine failure,TWF,HDF,PWF,OSF,RNF\n"
        "1,M14860,M,298.1,308.6,1551,42.8,0,0,0,0,0,0,0\n"
        "2,L47181,L,298.2,308.7,1408,46.3,3,0,0,0,0,0,0\n"
    )

    (root / "operations/energy_reports/CU-BEMS dataset files/2018Floor1.csv").write_text(
        "Date,z1_Light(kW),z1_Plug(kW),z2_AC1(kW)\n2018-07-01 00:00:00,12.94,18.56,45.24\n"
    )

    return root


class TestImporters:
    @pytest.fixture
    def dataset_path(self, tmp_path: Path) -> Path:
        return _create_mini_dataset(tmp_path)

    def test_reference_importer(self, dataset_path: Path) -> None:
        importer = ReferenceImporter(dataset_path)
        stats = importer.run()
        assert stats.phase == "REFERENCE"
        assert stats.total_records >= 4
        assert stats.imported >= 4

    def test_operations_importer(self, dataset_path: Path) -> None:
        importer = OperationsImporter(dataset_path)
        stats = importer.run()
        assert stats.phase == "OPERATIONS"
        assert stats.total_records >= 10
        assert stats.imported >= 10

    def test_business_rules_importer(self, dataset_path: Path) -> None:
        importer = BusinessRulesImporter(dataset_path)
        stats = importer.run()
        assert stats.phase == "BUSINESS_RULES"
        assert stats.imported >= 5
        assert "rules.json" in stats.file_breakdown

    def test_knowledge_importer(self, dataset_path: Path) -> None:
        importer = KnowledgeImporter(dataset_path)
        stats = importer.run()
        assert stats.phase == "KNOWLEDGE"
        assert stats.imported >= 4

    def test_timeseries_importer(self, dataset_path: Path) -> None:
        importer = TimeSeriesImporter(dataset_path)
        stats = importer.run()
        assert stats.phase == "TIME_SERIES"
        assert stats.total_records >= 3
        assert "ai4i2020.csv" in stats.file_breakdown

    def test_scenario_importer(self, dataset_path: Path) -> None:
        importer = ScenarioImporter(dataset_path)
        stats = importer.run()
        assert stats.phase == "SCENARIOS"
        assert stats.imported >= 1

    def test_importer_deduplication(self, dataset_path: Path) -> None:
        importer = ReferenceImporter(dataset_path)
        stats1 = importer.run()
        stats2 = importer.run()
        assert stats1.imported >= 4
        assert stats2.duplicates > 0
