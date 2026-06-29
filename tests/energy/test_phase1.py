"""Phase 1 tests for the Energy Domain Package (Architecture, Contracts & Models).

Tests all enums, domain models, events, exceptions, DTOs, interfaces,
asset hierarchy, sensor models, digital twins, alarms, and incidents.
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.energy.contracts.events import (
    AlarmRaised,
    AssetRegistered,
    AssetUpdated,
    EnergyEvent,
    IncidentCreated,
    MaintenanceCompleted,
    MaintenanceStarted,
    SensorReadingReceived,
)
from adip.energy.contracts.exceptions import (
    AlarmException,
    AssetException,
    EnergyDomainException,
    MaintenanceException,
    SensorException,
)
from adip.energy.contracts.models import (
    Alarm,
    AssetHealth,
    AssetHierarchy,
    AssetRelationship,
    DigitalTwin,
    EnergyAsset,
    EnergyContext,
    EnergyHealth,
    EnergyMetadata,
    EnergyMetrics,
    Incident,
    MaintenancePlan,
    MaintenanceRecord,
    Sensor,
    SensorReading,
    WorkOrder,
)
from adip.energy.dtos import (
    AlarmDTO,
    DigitalTwinDTO,
    EnergyAssetDTO,
    IncidentDTO,
    SensorDTO,
)
from adip.energy.enums import (
    AlarmSeverity,
    AlarmStatus,
    AssetStatus,
    AssetType,
    EnergyDomain,
    HealthState,
    IncidentPriority,
    MaintenanceType,
    SensorType,
    WorkOrderStatus,
)
from adip.energy.interfaces import (
    AlarmRepository,
    AssetRepository,
    DigitalTwinRepository,
    EnergyDomainCoordinator,
    EnergyDomainManager,
    EnergyDomainService,
    MaintenanceRepository,
    SensorRepository,
)

# ═════════════════════════════════════════════════════════════════════════════
# Enums
# ═════════════════════════════════════════════════════════════════════════════


class TestAssetType:
    def test_values(self) -> None:
        assert AssetType.TRANSFORMER.value == "TRANSFORMER"
        assert AssetType.SUBSTATION.value == "SUBSTATION"
        assert AssetType.BREAKER.value == "BREAKER"
        assert AssetType.FEEDER.value == "FEEDER"
        assert AssetType.GENERATOR.value == "GENERATOR"
        assert AssetType.BATTERY.value == "BATTERY"
        assert AssetType.SOLAR_PANEL.value == "SOLAR_PANEL"
        assert AssetType.WIND_TURBINE.value == "WIND_TURBINE"
        assert AssetType.METER.value == "METER"
        assert AssetType.SENSOR.value == "SENSOR"

    def test_unique_values(self) -> None:
        values = [e.value for e in AssetType]
        assert len(values) == len(set(values))

    def test_ten_asset_types(self) -> None:
        assert len(AssetType) == 10


class TestSensorType:
    def test_values(self) -> None:
        assert SensorType.TEMPERATURE.value == "TEMPERATURE"
        assert SensorType.VOLTAGE.value == "VOLTAGE"
        assert SensorType.CURRENT.value == "CURRENT"
        assert SensorType.POWER.value == "POWER"
        assert SensorType.FREQUENCY.value == "FREQUENCY"
        assert SensorType.HUMIDITY.value == "HUMIDITY"
        assert SensorType.PRESSURE.value == "PRESSURE"
        assert SensorType.OIL_LEVEL.value == "OIL_LEVEL"
        assert SensorType.VIBRATION.value == "VIBRATION"

    def test_unique_values(self) -> None:
        values = [e.value for e in SensorType]
        assert len(values) == len(set(values))

    def test_nine_sensor_types(self) -> None:
        assert len(SensorType) == 9


class TestHealthState:
    def test_values(self) -> None:
        assert HealthState.NORMAL.value == "NORMAL"
        assert HealthState.WARNING.value == "WARNING"
        assert HealthState.CRITICAL.value == "CRITICAL"
        assert HealthState.OFFLINE.value == "OFFLINE"
        assert HealthState.MAINTENANCE.value == "MAINTENANCE"

    def test_unique_values(self) -> None:
        values = [e.value for e in HealthState]
        assert len(values) == len(set(values))

    def test_five_health_states(self) -> None:
        assert len(HealthState) == 5


class TestMaintenanceType:
    def test_values(self) -> None:
        assert MaintenanceType.PREVENTIVE.value == "PREVENTIVE"
        assert MaintenanceType.PREDICTIVE.value == "PREDICTIVE"
        assert MaintenanceType.CORRECTIVE.value == "CORRECTIVE"
        assert MaintenanceType.EMERGENCY.value == "EMERGENCY"

    def test_unique_values(self) -> None:
        values = [e.value for e in MaintenanceType]
        assert len(values) == len(set(values))

    def test_four_maintenance_types(self) -> None:
        assert len(MaintenanceType) == 4


class TestAlarmSeverity:
    def test_values(self) -> None:
        assert AlarmSeverity.CRITICAL.value == "CRITICAL"
        assert AlarmSeverity.MAJOR.value == "MAJOR"
        assert AlarmSeverity.MINOR.value == "MINOR"
        assert AlarmSeverity.WARNING.value == "WARNING"
        assert AlarmSeverity.INFO.value == "INFO"

    def test_unique_values(self) -> None:
        values = [e.value for e in AlarmSeverity]
        assert len(values) == len(set(values))

    def test_five_severities(self) -> None:
        assert len(AlarmSeverity) == 5


class TestEnergyDomain:
    def test_values(self) -> None:
        assert EnergyDomain.ELECTRICITY.value == "ELECTRICITY"
        assert EnergyDomain.GAS.value == "GAS"
        assert EnergyDomain.WATER.value == "WATER"
        assert EnergyDomain.STEAM.value == "STEAM"
        assert EnergyDomain.RENEWABLES.value == "RENEWABLES"

    def test_unique_values(self) -> None:
        values = [e.value for e in EnergyDomain]
        assert len(values) == len(set(values))

    def test_five_domains(self) -> None:
        assert len(EnergyDomain) == 5


class TestAssetStatus:
    def test_values(self) -> None:
        assert AssetStatus.ACTIVE.value == "ACTIVE"
        assert AssetStatus.INACTIVE.value == "INACTIVE"
        assert AssetStatus.DECOMMISSIONED.value == "DECOMMISSIONED"
        assert AssetStatus.PLANNED.value == "PLANNED"
        assert AssetStatus.CONSTRUCTION.value == "CONSTRUCTION"

    def test_unique_values(self) -> None:
        values = [e.value for e in AssetStatus]
        assert len(values) == len(set(values))

    def test_five_statuses(self) -> None:
        assert len(AssetStatus) == 5


class TestAlarmStatus:
    def test_values(self) -> None:
        assert AlarmStatus.ACTIVE.value == "ACTIVE"
        assert AlarmStatus.ACKNOWLEDGED.value == "ACKNOWLEDGED"
        assert AlarmStatus.RESOLVED.value == "RESOLVED"
        assert AlarmStatus.CLEARED.value == "CLEARED"
        assert AlarmStatus.ESCALATED.value == "ESCALATED"

    def test_unique_values(self) -> None:
        values = [e.value for e in AlarmStatus]
        assert len(values) == len(set(values))

    def test_five_alarm_statuses(self) -> None:
        assert len(AlarmStatus) == 5


class TestIncidentPriority:
    def test_values(self) -> None:
        assert IncidentPriority.CRITICAL.value == "CRITICAL"
        assert IncidentPriority.HIGH.value == "HIGH"
        assert IncidentPriority.MEDIUM.value == "MEDIUM"
        assert IncidentPriority.LOW.value == "LOW"

    def test_unique_values(self) -> None:
        values = [e.value for e in IncidentPriority]
        assert len(values) == len(set(values))

    def test_four_priorities(self) -> None:
        assert len(IncidentPriority) == 4


class TestWorkOrderStatus:
    def test_values(self) -> None:
        assert WorkOrderStatus.OPEN.value == "OPEN"
        assert WorkOrderStatus.ASSIGNED.value == "ASSIGNED"
        assert WorkOrderStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert WorkOrderStatus.COMPLETED.value == "COMPLETED"
        assert WorkOrderStatus.CANCELLED.value == "CANCELLED"

    def test_unique_values(self) -> None:
        values = [e.value for e in WorkOrderStatus]
        assert len(values) == len(set(values))

    def test_five_work_order_statuses(self) -> None:
        assert len(WorkOrderStatus) == 5


# ═════════════════════════════════════════════════════════════════════════════
# Domain Models
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyAsset:
    def test_default_asset(self) -> None:
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER)
        assert asset.asset_type == AssetType.TRANSFORMER
        assert asset.domain == EnergyDomain.ELECTRICITY
        assert asset.status == AssetStatus.ACTIVE
        assert asset.name == ""

    def test_requires_asset_type(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAsset()

    def test_asset_type_invalid(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAsset(asset_type="INVALID")

    def test_with_full_data(self) -> None:
        asset = EnergyAsset(
            asset_type=AssetType.GENERATOR,
            name="Main Generator 1",
            domain=EnergyDomain.ELECTRICITY,
            status=AssetStatus.ACTIVE,
            location="Building A, Room 101",
            latitude=40.7128,
            longitude=-74.0060,
            manufacturer="Siemens",
            model="G-1000",
            serial_number="SN-12345",
            rated_capacity=1000.0,
            rated_voltage=11.0,
            tags=["primary", "backup"],
        )
        assert asset.name == "Main Generator 1"
        assert asset.manufacturer == "Siemens"
        assert asset.rated_capacity == 1000.0
        assert asset.tags == ["primary", "backup"]
        assert asset.latitude == 40.7128
        assert asset.longitude == -74.0060

    def test_asset_has_uuid(self) -> None:
        asset = EnergyAsset(asset_type=AssetType.METER)
        assert isinstance(asset.asset_id, uuid.UUID)

    def test_rated_capacity_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAsset(asset_type=AssetType.BATTERY, rated_capacity=-1.0)

    def test_latitude_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAsset(asset_type=AssetType.SENSOR, latitude=100.0)

    def test_longitude_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAsset(asset_type=AssetType.SENSOR, longitude=200.0)

    def test_rated_voltage_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAsset(asset_type=AssetType.TRANSFORMER, rated_voltage=-1.0)


class TestAssetHierarchy:
    def test_default_hierarchy(self) -> None:
        parent_id = uuid.uuid4()
        child_id = uuid.uuid4()
        hier = AssetHierarchy(
            parent_asset_id=parent_id,
            child_asset_id=child_id,
        )
        assert hier.parent_asset_id == parent_id
        assert hier.child_asset_id == child_id
        assert hier.relationship_type == "contains"
        assert hier.level == 0

    def test_requires_parent_and_child(self) -> None:
        with pytest.raises(ValidationError):
            AssetHierarchy()

    def test_with_path(self) -> None:
        root_id = uuid.uuid4()
        parent_id = uuid.uuid4()
        child_id = uuid.uuid4()
        hier = AssetHierarchy(
            parent_asset_id=parent_id,
            child_asset_id=child_id,
            relationship_type="feeds",
            level=2,
            path=[root_id, parent_id, child_id],
        )
        assert hier.relationship_type == "feeds"
        assert hier.level == 2
        assert len(hier.path) == 3


class TestAssetRelationship:
    def test_default_relationship(self) -> None:
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        rel = AssetRelationship(
            source_asset_id=source_id,
            target_asset_id=target_id,
            relationship_type="feeds",
        )
        assert rel.source_asset_id == source_id
        assert rel.target_asset_id == target_id
        assert rel.direction == "directed"

    def test_requires_source_target_type(self) -> None:
        with pytest.raises(ValidationError):
            AssetRelationship()

    def test_with_weight(self) -> None:
        rel = AssetRelationship(
            source_asset_id=uuid.uuid4(),
            target_asset_id=uuid.uuid4(),
            relationship_type="backs_up",
            direction="bidirectional",
            weight=0.85,
        )
        assert rel.weight == 0.85
        assert rel.direction == "bidirectional"

    def test_weight_range(self) -> None:
        with pytest.raises(ValidationError):
            AssetRelationship(
                source_asset_id=uuid.uuid4(),
                target_asset_id=uuid.uuid4(),
                relationship_type="test",
                weight=1.5,
            )


class TestDigitalTwin:
    def test_default_twin(self) -> None:
        asset_id = uuid.uuid4()
        twin = DigitalTwin(asset_id=asset_id)
        assert twin.asset_id == asset_id
        assert twin.twin_type == "simulation"
        assert twin.model_version == "1.0.0"
        assert twin.is_active is True

    def test_requires_asset_id(self) -> None:
        with pytest.raises(ValidationError):
            DigitalTwin()

    def test_with_full_data(self) -> None:
        twin = DigitalTwin(
            asset_id=uuid.uuid4(),
            twin_type="predictive",
            model_version="2.0.0",
            parameters={"efficiency": 0.95, "temperature": 75.0},
            state={"running": True, "load": 0.8},
            is_active=True,
        )
        assert twin.twin_type == "predictive"
        assert twin.parameters["efficiency"] == 0.95
        assert twin.state["load"] == 0.8


class TestSensor:
    def test_default_sensor(self) -> None:
        asset_id = uuid.uuid4()
        sensor = Sensor(
            asset_id=asset_id,
            sensor_type=SensorType.TEMPERATURE,
            unit="°C",
        )
        assert sensor.asset_id == asset_id
        assert sensor.sensor_type == SensorType.TEMPERATURE
        assert sensor.unit == "°C"
        assert sensor.is_active is True
        assert sensor.sampling_interval_seconds == 60

    def test_requires_asset_id_and_type(self) -> None:
        with pytest.raises(ValidationError):
            Sensor()

    def test_invalid_sensor_type(self) -> None:
        with pytest.raises(ValidationError):
            Sensor(
                asset_id=uuid.uuid4(),
                sensor_type="INVALID",
                unit="°C",
            )

    def test_sampling_interval_ge_one(self) -> None:
        with pytest.raises(ValidationError):
            Sensor(
                asset_id=uuid.uuid4(),
                sensor_type=SensorType.VOLTAGE,
                unit="kV",
                sampling_interval_seconds=0,
            )

    def test_accuracy_range(self) -> None:
        with pytest.raises(ValidationError):
            Sensor(
                asset_id=uuid.uuid4(),
                sensor_type=SensorType.CURRENT,
                unit="A",
                accuracy=150.0,
            )


class TestSensorReading:
    def test_default_reading(self) -> None:
        sensor_id = uuid.uuid4()
        asset_id = uuid.uuid4()
        reading = SensorReading(
            sensor_id=sensor_id,
            asset_id=asset_id,
            value=25.5,
            unit="°C",
        )
        assert reading.sensor_id == sensor_id
        assert reading.asset_id == asset_id
        assert reading.value == 25.5
        assert reading.quality == "good"

    def test_requires_sensor_asset_and_value(self) -> None:
        with pytest.raises(ValidationError):
            SensorReading()

    def test_with_quality(self) -> None:
        reading = SensorReading(
            sensor_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            value=100.0,
            quality="substituted",
        )
        assert reading.quality == "substituted"


class TestAssetHealth:
    def test_default_health(self) -> None:
        asset_id = uuid.uuid4()
        health = AssetHealth(asset_id=asset_id)
        assert health.asset_id == asset_id
        assert health.health_state == HealthState.NORMAL
        assert health.overall_score == 1.0
        assert health.temperature_score == 1.0

    def test_requires_asset_id(self) -> None:
        with pytest.raises(ValidationError):
            AssetHealth()

    def test_scores_bounds(self) -> None:
        with pytest.raises(ValidationError):
            AssetHealth(asset_id=uuid.uuid4(), overall_score=1.5)
        with pytest.raises(ValidationError):
            AssetHealth(asset_id=uuid.uuid4(), overall_score=-0.1)

    def test_with_alerts(self) -> None:
        health = AssetHealth(
            asset_id=uuid.uuid4(),
            health_state=HealthState.WARNING,
            overall_score=0.65,
            alerts=["High temperature", "Vibration anomaly"],
        )
        assert health.health_state == HealthState.WARNING
        assert len(health.alerts) == 2


class TestMaintenanceRecord:
    def test_default_record(self) -> None:
        asset_id = uuid.uuid4()
        record = MaintenanceRecord(
            asset_id=asset_id,
            maintenance_type=MaintenanceType.PREVENTIVE,
        )
        assert record.asset_id == asset_id
        assert record.maintenance_type == MaintenanceType.PREVENTIVE
        assert record.duration_hours == 0.0

    def test_requires_asset_id_and_type(self) -> None:
        with pytest.raises(ValidationError):
            MaintenanceRecord()

    def test_with_full_data(self) -> None:
        record = MaintenanceRecord(
            asset_id=uuid.uuid4(),
            maintenance_type=MaintenanceType.CORRECTIVE,
            description="Replaced faulty breaker",
            technician="John Doe",
            parts_used=["Breaker XYZ-200", "Cable 4mm"],
            duration_hours=3.5,
            cost=1500.00,
            downtime_hours=2.0,
            findings="Corrosion detected on contacts",
            recommendations="Schedule annual inspection",
        )
        assert record.technician == "John Doe"
        assert len(record.parts_used) == 2
        assert record.cost == 1500.00
        assert record.downtime_hours == 2.0


class TestMaintenancePlan:
    def test_default_plan(self) -> None:
        asset_id = uuid.uuid4()
        plan = MaintenancePlan(
            asset_id=asset_id,
            maintenance_type=MaintenanceType.PREVENTIVE,
        )
        assert plan.asset_id == asset_id
        assert plan.is_active is True
        assert plan.estimated_duration_hours == 0.0

    def test_requires_asset_id_and_type(self) -> None:
        with pytest.raises(ValidationError):
            MaintenancePlan()

    def test_with_recurrence(self) -> None:
        plan = MaintenancePlan(
            asset_id=uuid.uuid4(),
            maintenance_type=MaintenanceType.PREDICTIVE,
            name="Quarterly Oil Analysis",
            interval_days=90,
            estimated_duration_hours=2.0,
            required_parts=["Oil sample kit"],
            required_skills=["Oil analysis certification"],
        )
        assert plan.interval_days == 90
        assert len(plan.required_parts) == 1
        assert len(plan.required_skills) == 1


class TestAlarm:
    def test_default_alarm(self) -> None:
        asset_id = uuid.uuid4()
        alarm = Alarm(asset_id=asset_id)
        assert alarm.asset_id == asset_id
        assert alarm.severity == AlarmSeverity.WARNING
        assert alarm.status == AlarmStatus.ACTIVE
        assert alarm.name == ""

    def test_requires_asset_id(self) -> None:
        with pytest.raises(ValidationError):
            Alarm()

    def test_with_full_data(self) -> None:
        alarm = Alarm(
            asset_id=uuid.uuid4(),
            name="Transformer Overheating",
            description="Temperature exceeds 85°C threshold",
            severity=AlarmSeverity.CRITICAL,
            status=AlarmStatus.ACTIVE,
            source="sensor-001",
        )
        assert alarm.name == "Transformer Overheating"
        assert alarm.severity == AlarmSeverity.CRITICAL
        assert alarm.source == "sensor-001"

    def test_with_acknowledgement(self) -> None:
        alarm = Alarm(
            asset_id=uuid.uuid4(),
            severity=AlarmSeverity.MAJOR,
            status=AlarmStatus.ACKNOWLEDGED,
            acknowledged_by="operator-01",
        )
        assert alarm.status == AlarmStatus.ACKNOWLEDGED
        assert alarm.acknowledged_by == "operator-01"

    def test_invalid_severity(self) -> None:
        with pytest.raises(ValidationError):
            Alarm(asset_id=uuid.uuid4(), severity="INVALID")


class TestIncident:
    def test_default_incident(self) -> None:
        incident = Incident()
        assert incident.priority == IncidentPriority.MEDIUM
        assert incident.is_resolved is False
        assert incident.customers_affected == 0
        assert incident.title == ""

    def test_with_full_data(self) -> None:
        asset_ids = [uuid.uuid4(), uuid.uuid4()]
        alarm_ids = [uuid.uuid4()]
        incident = Incident(
            title="Substation Fire",
            description="Fire detected at Main Substation",
            asset_ids=asset_ids,
            alarm_ids=alarm_ids,
            priority=IncidentPriority.CRITICAL,
            impact_area="Downtown District",
            customers_affected=5000,
            outage_duration_minutes=120,
            reported_by="SCADA",
        )
        assert incident.title == "Substation Fire"
        assert len(incident.asset_ids) == 2
        assert incident.customers_affected == 5000
        assert incident.outage_duration_minutes == 120

    def test_resolved_incident(self) -> None:
        incident = Incident(
            title="Line Fault",
            is_resolved=True,
            root_cause="Tree contact",
            resolution="Tree trimmed, line restored",
        )
        assert incident.is_resolved is True
        assert incident.root_cause == "Tree contact"

    def test_customers_affected_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            Incident(customers_affected=-1)

    def test_outage_duration_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            Incident(outage_duration_minutes=-1)


class TestWorkOrder:
    def test_default_work_order(self) -> None:
        asset_id = uuid.uuid4()
        wo = WorkOrder(asset_id=asset_id)
        assert wo.asset_id == asset_id
        assert wo.status == WorkOrderStatus.OPEN
        assert wo.priority == IncidentPriority.MEDIUM
        assert wo.title == ""

    def test_requires_asset_id(self) -> None:
        with pytest.raises(ValidationError):
            WorkOrder()

    def test_with_full_data(self) -> None:
        wo = WorkOrder(
            asset_id=uuid.uuid4(),
            title="Replace Transformer Bushing",
            description="Replace damaged bushing on TX-001",
            status=WorkOrderStatus.ASSIGNED,
            priority=IncidentPriority.HIGH,
            assigned_to="Line Crew Alpha",
            estimated_hours=8.0,
        )
        assert wo.title == "Replace Transformer Bushing"
        assert wo.status == WorkOrderStatus.ASSIGNED
        assert wo.assigned_to == "Line Crew Alpha"
        assert wo.estimated_hours == 8.0

    def test_with_actuals(self) -> None:
        wo = WorkOrder(
            asset_id=uuid.uuid4(),
            title="Routine Inspection",
            status=WorkOrderStatus.COMPLETED,
            actual_hours=6.5,
            notes="All clear, no issues found",
        )
        assert wo.status == WorkOrderStatus.COMPLETED
        assert wo.actual_hours == 6.5


class TestEnergyContext:
    def test_default_context(self) -> None:
        context = EnergyContext()
        assert context.domain == EnergyDomain.ELECTRICITY
        assert context.load_condition == "normal"
        assert context.metadata == {}

    def test_with_full_data(self) -> None:
        context = EnergyContext(
            asset_id=uuid.uuid4(),
            domain=EnergyDomain.GAS,
            facility_id="PLANT-01",
            region="Northeast",
            weather_conditions="Storm warning",
            load_condition="peak",
            season="winter",
        )
        assert context.domain == EnergyDomain.GAS
        assert context.facility_id == "PLANT-01"
        assert context.weather_conditions == "Storm warning"


class TestEnergyMetadata:
    def test_default_metadata(self) -> None:
        meta = EnergyMetadata()
        assert meta.version == "1.0.0"
        assert meta.title == ""
        assert meta.tags == []

    def test_with_values(self) -> None:
        meta = EnergyMetadata(
            title="Generator TX-001",
            description="Main step-up transformer",
            tags=["primary", "high-voltage"],
            category="transformer",
            source="SCADA",
            version="2.0.0",
        )
        assert meta.title == "Generator TX-001"
        assert meta.source == "SCADA"
        assert meta.version == "2.0.0"


class TestEnergyMetrics:
    def test_default_metrics(self) -> None:
        metrics = EnergyMetrics()
        assert metrics.assets_total == 0
        assert metrics.sensors_total == 0
        assert metrics.alarms_active == 0
        assert metrics.average_health_score == 0.0

    def test_with_values(self) -> None:
        metrics = EnergyMetrics(
            assets_total=100,
            assets_active=85,
            assets_in_maintenance=10,
            assets_offline=5,
            sensors_total=500,
            sensors_active=480,
            readings_total=100000,
            alarms_active=12,
            alarms_critical=3,
            incidents_open=2,
            work_orders_open=15,
            work_orders_completed=200,
            maintenance_scheduled=25,
            maintenance_completed=150,
            average_health_score=0.87,
        )
        assert metrics.assets_total == 100
        assert metrics.sensors_total == 500
        assert metrics.alarms_critical == 3
        assert metrics.average_health_score == 0.87

    def test_non_negative_counts(self) -> None:
        with pytest.raises(ValidationError):
            EnergyMetrics(assets_total=-1)

    def test_health_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EnergyMetrics(average_health_score=1.5)
        with pytest.raises(ValidationError):
            EnergyMetrics(average_health_score=-0.1)


class TestEnergyHealth:
    def test_default_health(self) -> None:
        health = EnergyHealth()
        assert health.overall_status == ""
        assert health.total_assets == 0
        assert health.active_alarms == 0

    def test_with_values(self) -> None:
        health = EnergyHealth(
            overall_status="HEALTHY",
            asset_service_status="HEALTHY",
            sensor_service_status="HEALTHY",
            digital_twin_status="HEALTHY",
            maintenance_service_status="DEGRADED",
            alarm_service_status="HEALTHY",
            incident_service_status="HEALTHY",
            total_assets=1000,
            active_alarms=5,
            open_incidents=1,
        )
        assert health.overall_status == "HEALTHY"
        assert health.maintenance_service_status == "DEGRADED"
        assert health.total_assets == 1000
        assert health.active_alarms == 5

    def test_non_negative_counts(self) -> None:
        with pytest.raises(ValidationError):
            EnergyHealth(total_assets=-1)


# ═════════════════════════════════════════════════════════════════════════════
# Events
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyEvents:
    def test_energy_event_base(self) -> None:
        event = EnergyEvent()
        assert isinstance(event.event_id, uuid.UUID)
        assert event.correlation_id == ""

    def test_asset_registered(self) -> None:
        asset_id = uuid.uuid4()
        event = AssetRegistered(
            asset_id=asset_id,
            asset_type=AssetType.TRANSFORMER,
            domain=EnergyDomain.ELECTRICITY,
            name="TX-001",
        )
        assert event.asset_id == asset_id
        assert event.asset_type == AssetType.TRANSFORMER
        assert event.name == "TX-001"

    def test_asset_updated(self) -> None:
        event = AssetUpdated(
            asset_id=uuid.uuid4(),
            asset_type=AssetType.GENERATOR,
            previous_status="ACTIVE",
            new_status="MAINTENANCE",
            changed_fields=["status"],
        )
        assert event.previous_status == "ACTIVE"
        assert event.new_status == "MAINTENANCE"
        assert event.changed_fields == ["status"]

    def test_sensor_reading_received(self) -> None:
        event = SensorReadingReceived(
            reading_id=uuid.uuid4(),
            sensor_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            sensor_type=SensorType.TEMPERATURE,
            value=75.5,
            unit="°C",
        )
        assert event.sensor_type == SensorType.TEMPERATURE
        assert event.value == 75.5
        assert event.quality == "good"

    def test_alarm_raised(self) -> None:
        event = AlarmRaised(
            alarm_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            name="Overvoltage",
            severity=AlarmSeverity.CRITICAL,
            description="Voltage exceeds limit",
        )
        assert event.name == "Overvoltage"
        assert event.severity == AlarmSeverity.CRITICAL

    def test_incident_created(self) -> None:
        asset_ids = [uuid.uuid4(), uuid.uuid4()]
        event = IncidentCreated(
            incident_id=uuid.uuid4(),
            title="Power Outage",
            asset_ids=asset_ids,
            priority="CRITICAL",
            impact_area="Zone 3",
        )
        assert event.title == "Power Outage"
        assert len(event.asset_ids) == 2
        assert event.impact_area == "Zone 3"

    def test_maintenance_started(self) -> None:
        event = MaintenanceStarted(
            record_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            maintenance_type="PREVENTIVE",
            technician="Jane Smith",
        )
        assert event.maintenance_type == "PREVENTIVE"
        assert event.technician == "Jane Smith"

    def test_maintenance_completed(self) -> None:
        event = MaintenanceCompleted(
            record_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            maintenance_type="CORRECTIVE",
            duration_hours=4.5,
            findings="Replaced faulty component",
        )
        assert event.maintenance_type == "CORRECTIVE"
        assert event.duration_hours == 4.5
        assert event.findings == "Replaced faulty component"

    def test_event_inheritance(self) -> None:
        event = AssetRegistered(
            asset_id=uuid.uuid4(),
            asset_type=AssetType.METER,
        )
        assert isinstance(event, EnergyEvent)
        assert hasattr(event, "event_id")
        assert hasattr(event, "timestamp")
        assert hasattr(event, "correlation_id")

    def test_event_with_correlation(self) -> None:
        event = AlarmRaised(
            alarm_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            name="Test",
            severity=AlarmSeverity.MAJOR,
            correlation_id="corr-001",
        )
        assert event.correlation_id == "corr-001"


# ═════════════════════════════════════════════════════════════════════════════
# Exceptions
# ═════════════════════════════════════════════════════════════════════════════


class TestExceptions:
    def test_base_exception(self) -> None:
        exc = EnergyDomainException()
        assert exc.message == "Energy domain error occurred"
        assert exc.code == "ENERGY_DOMAIN_ERROR"
        assert exc.details == {}

    def test_base_with_custom_message(self) -> None:
        exc = EnergyDomainException(
            message="Custom error",
            code="CUSTOM_CODE",
            details={"key": "value"},
        )
        assert exc.message == "Custom error"
        assert exc.details["key"] == "value"

    def test_asset_exception(self) -> None:
        exc = AssetException()
        assert isinstance(exc, EnergyDomainException)
        assert exc.code == "ASSET_ERROR"

    def test_sensor_exception(self) -> None:
        exc = SensorException()
        assert isinstance(exc, EnergyDomainException)
        assert exc.code == "SENSOR_ERROR"

    def test_maintenance_exception(self) -> None:
        exc = MaintenanceException()
        assert isinstance(exc, EnergyDomainException)
        assert exc.code == "MAINTENANCE_ERROR"

    def test_alarm_exception(self) -> None:
        exc = AlarmException()
        assert isinstance(exc, EnergyDomainException)
        assert exc.code == "ALARM_ERROR"

    def test_exception_hierarchy(self) -> None:
        assert issubclass(AssetException, EnergyDomainException)
        assert issubclass(SensorException, EnergyDomainException)
        assert issubclass(MaintenanceException, EnergyDomainException)
        assert issubclass(AlarmException, EnergyDomainException)

    def test_all_exceptions_raise(self) -> None:
        with pytest.raises(EnergyDomainException):
            raise AssetException("Asset not found")
        with pytest.raises(EnergyDomainException):
            raise SensorException("Sensor read failure")
        with pytest.raises(EnergyDomainException):
            raise AlarmException("Alarm escalation failed")


# ═════════════════════════════════════════════════════════════════════════════
# DTOs
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyAssetDTO:
    def test_default_dto(self) -> None:
        dto = EnergyAssetDTO(asset_type=AssetType.TRANSFORMER)
        assert dto.asset_type == AssetType.TRANSFORMER
        assert dto.domain == EnergyDomain.ELECTRICITY
        assert dto.status == AssetStatus.ACTIVE

    def test_requires_asset_type(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAssetDTO()

    def test_with_values(self) -> None:
        dto = EnergyAssetDTO(
            name="TX-001",
            asset_type=AssetType.TRANSFORMER,
            domain=EnergyDomain.ELECTRICITY,
            location="Substation A",
            rated_capacity=50.0,
            tags=["primary"],
        )
        assert dto.name == "TX-001"
        assert dto.rated_capacity == 50.0

    def test_latitude_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EnergyAssetDTO(asset_type=AssetType.SENSOR, latitude=100.0)


class TestSensorDTO:
    def test_default_dto(self) -> None:
        dto = SensorDTO(
            asset_id=uuid.uuid4(),
            sensor_type=SensorType.VOLTAGE,
            unit="kV",
        )
        assert dto.sensor_type == SensorType.VOLTAGE
        assert dto.is_active is True
        assert dto.sampling_interval_seconds == 60

    def test_requires_asset_id_and_type(self) -> None:
        with pytest.raises(ValidationError):
            SensorDTO()

    def test_with_values(self) -> None:
        dto = SensorDTO(
            asset_id=uuid.uuid4(),
            name="Temp Sensor 01",
            sensor_type=SensorType.TEMPERATURE,
            unit="°C",
            sampling_interval_seconds=30,
            location="Top of transformer",
        )
        assert dto.name == "Temp Sensor 01"
        assert dto.sampling_interval_seconds == 30
        assert dto.location == "Top of transformer"


class TestDigitalTwinDTO:
    def test_default_dto(self) -> None:
        dto = DigitalTwinDTO(asset_id=uuid.uuid4())
        assert dto.twin_type == "simulation"
        assert dto.model_version == "1.0.0"
        assert dto.is_active is True

    def test_requires_asset_id(self) -> None:
        with pytest.raises(ValidationError):
            DigitalTwinDTO()

    def test_with_values(self) -> None:
        dto = DigitalTwinDTO(
            asset_id=uuid.uuid4(),
            twin_type="predictive",
            model_version="2.1.0",
            parameters={"threshold": 0.9},
        )
        assert dto.twin_type == "predictive"
        assert dto.parameters["threshold"] == 0.9


class TestAlarmDTO:
    def test_default_dto(self) -> None:
        dto = AlarmDTO(asset_id=uuid.uuid4())
        assert dto.severity == AlarmSeverity.WARNING
        assert dto.status == AlarmStatus.ACTIVE
        assert dto.name == ""

    def test_requires_asset_id(self) -> None:
        with pytest.raises(ValidationError):
            AlarmDTO()

    def test_with_values(self) -> None:
        dto = AlarmDTO(
            asset_id=uuid.uuid4(),
            name="Overcurrent",
            severity=AlarmSeverity.CRITICAL,
            source="relay-01",
        )
        assert dto.name == "Overcurrent"
        assert dto.severity == AlarmSeverity.CRITICAL


class TestIncidentDTO:
    def test_default_dto(self) -> None:
        dto = IncidentDTO()
        assert dto.priority == IncidentPriority.MEDIUM
        assert dto.customers_affected == 0
        assert dto.title == ""

    def test_with_values(self) -> None:
        dto = IncidentDTO(
            title="Line Down",
            description="Primary feeder line down",
            asset_ids=[uuid.uuid4()],
            priority=IncidentPriority.HIGH,
            customers_affected=1000,
            reported_by="Operator",
        )
        assert dto.title == "Line Down"
        assert dto.priority == IncidentPriority.HIGH
        assert dto.customers_affected == 1000


# ═════════════════════════════════════════════════════════════════════════════
# Interfaces
# ═════════════════════════════════════════════════════════════════════════════


class TestInterfacesAreAbstract:
    def test_energy_domain_service_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            EnergyDomainService()

    def test_energy_domain_manager_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            EnergyDomainManager()

    def test_energy_domain_coordinator_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            EnergyDomainCoordinator()

    def test_asset_repository_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            AssetRepository()

    def test_sensor_repository_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            SensorRepository()

    def test_digital_twin_repository_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            DigitalTwinRepository()

    def test_maintenance_repository_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            MaintenanceRepository()

    def test_alarm_repository_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            AlarmRepository()


class TestEnergyDomainServiceInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "register_asset",
            "get_asset",
            "update_asset",
            "register_sensor",
            "get_sensor",
            "receive_reading",
            "create_digital_twin",
            "raise_alarm",
            "create_incident",
            "record_maintenance",
            "get_asset_health",
            "get_asset_hierarchy",
            "get_health",
            "get_metrics",
        ]
        for method in methods:
            assert hasattr(EnergyDomainService, method)


class TestEnergyDomainManagerInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "register_asset",
            "get_asset",
            "update_asset",
            "register_sensor",
            "get_sensor",
            "receive_reading",
            "create_digital_twin",
            "get_digital_twin",
            "raise_alarm",
            "get_alarm",
            "create_incident",
            "record_maintenance",
            "get_asset_health",
            "get_health",
            "get_metrics",
        ]
        for method in methods:
            assert hasattr(EnergyDomainManager, method)


class TestEnergyDomainCoordinatorInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "register_asset",
            "get_asset",
            "register_sensor",
            "get_sensor",
            "receive_reading",
            "create_digital_twin",
            "raise_alarm",
            "create_incident",
            "health",
            "metrics",
        ]
        for method in methods:
            assert hasattr(EnergyDomainCoordinator, method)


class TestAssetRepositoryInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "save",
            "find_by_id",
            "find_by_type",
            "find_by_domain",
            "find_all",
            "delete",
            "count",
        ]
        for method in methods:
            assert hasattr(AssetRepository, method)


class TestSensorRepositoryInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "save",
            "find_by_id",
            "find_by_asset",
            "save_reading",
            "find_readings",
            "delete",
            "count",
        ]
        for method in methods:
            assert hasattr(SensorRepository, method)


class TestDigitalTwinRepositoryInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "save",
            "find_by_id",
            "find_by_asset",
            "delete",
        ]
        for method in methods:
            assert hasattr(DigitalTwinRepository, method)


class TestMaintenanceRepositoryInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "save_record",
            "find_record_by_id",
            "find_records_by_asset",
            "save_plan",
            "find_plan_by_id",
            "find_plans_by_asset",
        ]
        for method in methods:
            assert hasattr(MaintenanceRepository, method)


class TestAlarmRepositoryInterface:
    def test_has_all_required_methods(self) -> None:
        methods = [
            "save",
            "find_by_id",
            "find_by_asset",
            "find_active",
            "find_by_severity",
            "delete",
            "count",
        ]
        for method in methods:
            assert hasattr(AlarmRepository, method)


# ═════════════════════════════════════════════════════════════════════════════
# Module Imports
# ═════════════════════════════════════════════════════════════════════════════


class TestModuleImport:
    def test_import_enums(self) -> None:
        from adip.energy.enums import (
            AssetType,
        )
        assert AssetType is not None

    def test_import_models(self) -> None:
        from adip.energy.contracts.models import (
            EnergyAsset,
        )
        assert EnergyAsset is not None

    def test_import_events(self) -> None:
        from adip.energy.contracts.events import (
            AssetRegistered,
        )
        assert AssetRegistered is not None

    def test_import_exceptions(self) -> None:
        from adip.energy.contracts.exceptions import (
            EnergyDomainException,
        )
        assert EnergyDomainException is not None

    def test_import_dtos(self) -> None:
        from adip.energy.dtos import (
            EnergyAssetDTO,
        )
        assert EnergyAssetDTO is not None

    def test_import_interfaces(self) -> None:
        from adip.energy.interfaces import (
            EnergyDomainService,
        )
        assert EnergyDomainService is not None

    def test_package_import(self) -> None:
        import adip.energy as energy
        assert energy.AssetType is not None
        assert energy.EnergyDomainService is not None
        assert energy.EnergyAssetDTO is not None
        assert energy.energy_models is not None

    def test_package_all(self) -> None:
        import adip.energy as energy
        assert hasattr(energy, "__all__")
        assert "EnergyAssetDTO" in energy.__all__
        assert "EnergyDomainService" in energy.__all__
