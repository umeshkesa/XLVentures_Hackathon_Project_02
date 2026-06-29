from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum as _StrEnum
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adip.models.base import AuditMixin, Base


class ImportPhase(_StrEnum):
    REFERENCE = "REFERENCE"
    OPERATIONS = "OPERATIONS"
    BUSINESS_RULES = "BUSINESS_RULES"
    KNOWLEDGE = "KNOWLEDGE"
    TIME_SERIES = "TIME_SERIES"
    SCENARIOS = "SCENARIOS"


class ImportStatus(_StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ImportSession(Base, AuditMixin):
    __tablename__ = "data_import_sessions"

    phase: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default=ImportStatus.PENDING, nullable=False)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    processed_files: Mapped[int] = mapped_column(Integer, default=0)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    imported_records: Mapped[int] = mapped_column(Integer, default=0)
    skipped_records: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_records: Mapped[int] = mapped_column(Integer, default=0)
    validation_errors: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    source_path: Mapped[str] = mapped_column(String(512), default="")

    batches: Mapped[list[ImportBatch]] = relationship(
        "ImportBatch", back_populates="session", cascade="all, delete-orphan"
    )


class ImportBatch(Base, AuditMixin):
    __tablename__ = "data_import_batches"

    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default=ImportStatus.PENDING, nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    imported: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped[ImportSession] = relationship("ImportSession", back_populates="batches")


class Customer(Base, AuditMixin):
    __tablename__ = "import_customers"

    customer_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(256), nullable=False)
    industry: Mapped[str] = mapped_column(String(128), default="")
    location: Mapped[str] = mapped_column(String(256), default="")
    contact_person: Mapped[str] = mapped_column(String(256), default="")
    contact_email: Mapped[str] = mapped_column(String(256), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    contract_start: Mapped[str] = mapped_column(String(16), default="")
    contract_end: Mapped[str] = mapped_column(String(16), default="")
    sla_type: Mapped[str] = mapped_column(String(32), default="")
    status: Mapped[str] = mapped_column(String(32), default="Active")


class Facility(Base, AuditMixin):
    __tablename__ = "import_facilities"

    facility_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    facility_name: Mapped[str] = mapped_column(String(256), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    location: Mapped[str] = mapped_column(String(256), default="")
    facility_type: Mapped[str] = mapped_column(String(64), default="")
    total_area_sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    asset_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


class EquipmentAsset(Base, AuditMixin):
    __tablename__ = "import_equipment"

    asset_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    asset_name: Mapped[str] = mapped_column(String(256), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    facility: Mapped[str] = mapped_column(String(256), default="")
    location: Mapped[str] = mapped_column(String(256), default="")
    installation_date: Mapped[str] = mapped_column(String(16), default="")
    status: Mapped[str] = mapped_column(String(32), default="Active")
    last_maintenance_date: Mapped[str] = mapped_column(String(16), default="")


class Technician(Base, AuditMixin):
    __tablename__ = "import_technicians"

    technician_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    specialty: Mapped[str] = mapped_column(String(128), default="")
    certification_level: Mapped[str] = mapped_column(String(32), default="")
    availability_status: Mapped[str] = mapped_column(String(32), default="")
    assigned_region: Mapped[str] = mapped_column(String(128), default="")
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contact: Mapped[str] = mapped_column(String(128), default="")


class Incident(Base, AuditMixin):
    __tablename__ = "import_incidents"

    incident_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String(16), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    incident_date: Mapped[str] = mapped_column(String(16), default="")
    root_cause: Mapped[str] = mapped_column(Text, default="")
    downtime_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_loss_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolution: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="")


class WorkOrder(Base, AuditMixin):
    __tablename__ = "import_work_orders"

    work_order_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String(16), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    technician_id: Mapped[str] = mapped_column(String(16), default="")
    priority: Mapped[str] = mapped_column(String(16), default="")
    status: Mapped[str] = mapped_column(String(32), default="")
    issue_description: Mapped[str] = mapped_column(Text, default="")
    created_date: Mapped[str] = mapped_column(String(16), default="")
    scheduled_date: Mapped[str] = mapped_column(String(16), default="")
    completion_date: Mapped[str] = mapped_column(String(16), default="")
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)


class MaintenanceRecord(Base, AuditMixin):
    __tablename__ = "import_maintenance"

    maintenance_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String(16), nullable=False)
    work_order_id: Mapped[str] = mapped_column(String(16), default="")
    maintenance_type: Mapped[str] = mapped_column(String(32), default="")
    technician_id: Mapped[str] = mapped_column(String(16), default="")
    date: Mapped[str] = mapped_column(String(16), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    outcome: Mapped[str] = mapped_column(String(32), default="")
    next_due_date: Mapped[str] = mapped_column(String(16), default="")
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)


class AlarmLog(Base, AuditMixin):
    __tablename__ = "import_alarm_logs"

    timestamp: Mapped[str] = mapped_column(String(32), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(16), nullable=False)
    alarm_code: Mapped[str] = mapped_column(String(16), default="")
    severity: Mapped[str] = mapped_column(String(16), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    operator_action: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="")


class ServiceRequest(Base, AuditMixin):
    __tablename__ = "import_service_requests"

    request_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(16), nullable=False)
    request_date: Mapped[str] = mapped_column(String(16), default="")
    request_type: Mapped[str] = mapped_column(String(64), default="")
    priority: Mapped[str] = mapped_column(String(16), default="")
    status: Mapped[str] = mapped_column(String(32), default="")
    description: Mapped[str] = mapped_column(Text, default="")


class Complaint(Base, AuditMixin):
    __tablename__ = "import_complaints"

    complaint_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    date: Mapped[str] = mapped_column(String(16), default="")
    severity: Mapped[str] = mapped_column(String(16), default="")
    issue: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="")
    resolution: Mapped[str] = mapped_column(Text, default="")


class Feedback(Base, AuditMixin):
    __tablename__ = "import_feedback"

    feedback_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    date: Mapped[str] = mapped_column(String(16), default="")
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback_category: Mapped[str] = mapped_column(String(64), default="")
    comments: Mapped[str] = mapped_column(Text, default="")
    action_taken: Mapped[str] = mapped_column(Text, default="")


class CrmUpdate(Base, AuditMixin):
    __tablename__ = "import_crm_updates"

    crm_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    date: Mapped[str] = mapped_column(String(16), default="")
    update_type: Mapped[str] = mapped_column(String(64), default="")
    priority: Mapped[str] = mapped_column(String(16), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    assigned_team: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="")


class SlaDefinition(Base, AuditMixin):
    __tablename__ = "import_sla_definitions"

    sla_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    sla_type: Mapped[str] = mapped_column(String(32), nullable=False)
    response_time_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolution_time_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uptime_guarantee: Mapped[str] = mapped_column(String(16), default="")
    penalty_clause: Mapped[str] = mapped_column(Text, default="")
    priority_support: Mapped[str] = mapped_column(String(8), default="No")


class Contract(Base, AuditMixin):
    __tablename__ = "import_contracts"

    contract_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(16), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(64), default="")
    start_date: Mapped[str] = mapped_column(String(16), default="")
    end_date: Mapped[str] = mapped_column(String(16), default="")
    contract_value_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    sla_type: Mapped[str] = mapped_column(String(32), default="")
    status: Mapped[str] = mapped_column(String(32), default="")
    renewal_option: Mapped[str] = mapped_column(String(16), default="")


class ComplianceRequirement(Base, AuditMixin):
    __tablename__ = "import_compliance"

    compliance_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    standard: Mapped[str] = mapped_column(String(64), nullable=False)
    requirement: Mapped[str] = mapped_column(Text, default="")
    applicable_asset_type: Mapped[str] = mapped_column(String(64), default="")
    severity: Mapped[str] = mapped_column(String(16), default="")
    action_if_violated: Mapped[str] = mapped_column(Text, default="")


class BusinessRule(Base, AuditMixin):
    __tablename__ = "import_business_rules"

    rule_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    condition: Mapped[str] = mapped_column(Text, default="")
    action: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(16), default="")
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class RecommendationHistory(Base, AuditMixin):
    __tablename__ = "import_recommendations"

    recommendation_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    incident_id: Mapped[str] = mapped_column(String(16), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(16), default="")
    recommendation: Mapped[str] = mapped_column(Text, default="")
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision: Mapped[str] = mapped_column(String(32), default="")
    outcome: Mapped[str] = mapped_column(String(32), default="")
    lessons_learned: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[str] = mapped_column(String(16), default="")


class SparePart(Base, AuditMixin):
    __tablename__ = "import_spare_parts"

    part_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    part_name: Mapped[str] = mapped_column(String(256), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), default="")
    quantity_in_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reorder_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vendor: Mapped[str] = mapped_column(String(128), default="")
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="")


class WeatherRecord(Base, AuditMixin):
    __tablename__ = "import_weather"

    city: Mapped[str] = mapped_column(String(128), nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_dir: Mapped[str] = mapped_column(String(8), default="")
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm2_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm10: Mapped[float | None] = mapped_column(Float, nullable=True)


class SensorReading(Base, AuditMixin):
    __tablename__ = "import_sensor_readings"

    udi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_id: Mapped[str] = mapped_column(String(32), default="")
    type_: Mapped[str] = mapped_column("type", String(8), default="")
    air_temperature_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    process_temperature_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    rotational_speed_rpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    torque_nm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tool_wear_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    machine_failure: Mapped[int | None] = mapped_column(Integer, nullable=True)
    twf: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hdf: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pwf: Mapped[int | None] = mapped_column(Integer, nullable=True)
    osf: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rnf: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ScenarioRecord(Base, AuditMixin):
    __tablename__ = "import_scenarios"

    scenario_id: Mapped[str] = mapped_column(String(16), nullable=False)
    incident_id: Mapped[str] = mapped_column(String(16), default="")
    asset_id: Mapped[str] = mapped_column(String(16), default="")
    customer_id: Mapped[str] = mapped_column(String(16), default="")
    title: Mapped[str] = mapped_column(String(256), default="")
    severity: Mapped[str] = mapped_column(String(16), default="")
    status: Mapped[str] = mapped_column(String(32), default="")
    outcome: Mapped[str] = mapped_column(Text, default="")
    recommendation: Mapped[str] = mapped_column(Text, default="")
    incident_report: Mapped[str] = mapped_column(Text, default="")
    customer_email: Mapped[str] = mapped_column(Text, default="")
    lessons_learned: Mapped[str] = mapped_column(Text, default="")
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    downtime_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_loss_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
