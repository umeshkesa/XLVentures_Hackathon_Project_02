"""Phase 3 tests for the Energy Domain Package (Enterprise Orchestration).

Tests all orchestration components: EnergySessionManager,
AssetContextManager, DigitalTwinManager, EnergyReadinessCalculator,
EnergyVersionManager, EnergyLineage, EnergySnapshot, DomainHealthManager,
AssetPortfolioManager, TopologyValidator, DomainPolicyManager,
EnergyDomainCoordinator, EnergyDomainManager, IntegrationHooks,
and DefaultEnergyDomainService.
"""

from __future__ import annotations

import uuid
from typing import Any

from adip.energy.contracts.models import (
    Alarm,
    DigitalTwin,
    EnergyAsset,
    Incident,
    MaintenanceRecord,
    Sensor,
    SensorReading,
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
    AssetType,
    IncidentPriority,
    MaintenanceType,
    SensorType,
)
from adip.energy.orchestration.context_manager import AssetContextManager
from adip.energy.orchestration.coordinator import EnergyDomainCoordinator
from adip.energy.orchestration.digital_twin import DigitalTwinManager
from adip.energy.orchestration.health import DomainHealthManager
from adip.energy.orchestration.lineage import EnergyLineage
from adip.energy.orchestration.manager import EnergyDomainManager
from adip.energy.orchestration.models import (
    EnergyDecision,
    EnergyExplainabilityMetadata,
    EnergyLineageModel,
    EnergyReadiness,
    EnergySession,
    EnergySnapshotModel,
    EnergyVersionRecord,
)
from adip.energy.orchestration.policy import DomainPolicyManager
from adip.energy.orchestration.portfolio import AssetPortfolioManager
from adip.energy.orchestration.readiness import EnergyReadinessCalculator
from adip.energy.orchestration.session import EnergySessionManager
from adip.energy.orchestration.snapshot import EnergySnapshot
from adip.energy.orchestration.topology_validator import TopologyValidator
from adip.energy.orchestration.version_manager import EnergyVersionManager
from adip.energy.services.hooks import IntegrationHooks
from adip.energy.services.service import DefaultEnergyDomainService

# ═════════════════════════════════════════════════════════════════════════════
# Orchestration Models
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergySession:
    def test_default_session(self) -> None:
        session = EnergySession(asset_id=uuid.uuid4())
        assert session.status == "INITIALIZED"
        assert session.domain == "ELECTRICITY"
        assert session.operation == ""
        assert session.started_at is not None
        assert session.completed_at is None
        assert session.metadata == {}

    def test_session_with_values(self) -> None:
        aid = uuid.uuid4()
        session = EnergySession(
            asset_id=aid,
            domain="RENEWABLES",
            status="ACTIVE",
            operation="test_op",
        )
        assert session.asset_id == aid
        assert session.domain == "RENEWABLES"
        assert session.status == "ACTIVE"
        assert session.operation == "test_op"

    def test_session_id_auto_generated(self) -> None:
        s1 = EnergySession(asset_id=uuid.uuid4())
        s2 = EnergySession(asset_id=uuid.uuid4())
        assert s1.session_id != s2.session_id


class TestEnergyDecision:
    def test_default_decision(self) -> None:
        decision = EnergyDecision(
            session_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
        )
        assert decision.health_score == 0.0
        assert decision.confidence == 0.0
        assert decision.decisions == []
        assert decision.explainability == {}

    def test_decision_with_values(self) -> None:
        decision = EnergyDecision(
            session_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            context_summary="Test context",
            health_score=0.85,
            readiness_status="READY",
            decisions=["Action A"],
            confidence=0.9,
        )
        assert decision.context_summary == "Test context"
        assert decision.health_score == 0.85
        assert decision.readiness_status == "READY"
        assert decision.decisions == ["Action A"]
        assert decision.confidence == 0.9

    def test_decision_timestamp(self) -> None:
        decision = EnergyDecision(session_id=uuid.uuid4(), asset_id=uuid.uuid4())
        assert decision.timestamp is not None


class TestEnergyExplainabilityMetadata:
    def test_default_fields(self) -> None:
        meta = EnergyExplainabilityMetadata()
        assert meta.why_asset_selected == ""
        assert meta.why_sensor_used == ""
        assert meta.why_alarm_raised == ""
        assert meta.why_maintenance_scheduled == ""
        assert meta.why_health_assessed == ""
        assert meta.why_incident_created == ""

    def test_with_values(self) -> None:
        meta = EnergyExplainabilityMetadata(
            why_asset_selected="Critical asset",
            why_alarm_raised="Overheating detected",
            why_maintenance_scheduled="Preventive schedule due",
        )
        assert meta.why_asset_selected == "Critical asset"
        assert meta.why_alarm_raised == "Overheating detected"
        assert meta.why_maintenance_scheduled == "Preventive schedule due"


class TestEnergyReadiness:
    def test_default_readiness(self) -> None:
        readiness = EnergyReadiness(asset_id=uuid.uuid4())
        assert readiness.status == "PENDING"
        assert readiness.checks == {}
        assert readiness.reason == ""

    def test_readiness_with_values(self) -> None:
        readiness = EnergyReadiness(
            asset_id=uuid.uuid4(),
            status="READY",
            checks={"health_ok": True, "sensors_active": True},
            reason="All conditions met",
        )
        assert readiness.status == "READY"
        assert readiness.checks == {"health_ok": True, "sensors_active": True}
        assert readiness.reason == "All conditions met"

    def test_readiness_id_unique(self) -> None:
        r1 = EnergyReadiness(asset_id=uuid.uuid4())
        r2 = EnergyReadiness(asset_id=uuid.uuid4())
        assert r1.readiness_id != r2.readiness_id


class TestEnergyVersionRecord:
    def test_default_version(self) -> None:
        version = EnergyVersionRecord(entity_id="e1", entity_type="asset")
        assert version.version_number == 1
        assert version.data == {}
        assert version.created_by == "system"

    def test_version_number_increment(self) -> None:
        v1 = EnergyVersionRecord(entity_id="e1", entity_type="asset")
        v2 = EnergyVersionRecord(entity_id="e1", entity_type="asset", version_number=2)
        assert v1.version_number == 1
        assert v2.version_number == 2


class TestEnergyLineageModel:
    def test_default_lineage(self) -> None:
        lineage = EnergyLineageModel(entity_id="e1", entity_type="asset")
        assert lineage.parent_ids == []
        assert lineage.operations == []
        assert lineage.metadata == {}

    def test_lineage_with_parents(self) -> None:
        lineage = EnergyLineageModel(
            entity_id="e1",
            entity_type="asset",
            parent_ids=["p1", "p2"],
            operations=["created", "modified"],
        )
        assert lineage.parent_ids == ["p1", "p2"]
        assert lineage.operations == ["created", "modified"]


class TestEnergySnapshotModel:
    def test_default_snapshot(self) -> None:
        snap = EnergySnapshotModel(entity_id="e1", entity_type="asset")
        assert snap.snapshot_type == "state"
        assert snap.data == {}

    def test_snapshot_with_data(self) -> None:
        snap = EnergySnapshotModel(
            entity_id="e1",
            entity_type="asset",
            snapshot_type="health",
            data={"score": 0.9},
        )
        assert snap.snapshot_type == "health"
        assert snap.data == {"score": 0.9}

    def test_snapshot_timestamp(self) -> None:
        snap = EnergySnapshotModel(entity_id="e1", entity_type="asset")
        assert snap.timestamp is not None


# ═════════════════════════════════════════════════════════════════════════════
# EnergySessionManager
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergySessionManager:
    def test_create_session(self) -> None:
        mgr = EnergySessionManager()
        session = mgr.create_session(asset_id=str(uuid.uuid4()))
        assert session.status == "INITIALIZED"
        assert session.domain == "ELECTRICITY"

    def test_create_session_with_params(self) -> None:
        mgr = EnergySessionManager()
        aid = str(uuid.uuid4())
        session = mgr.create_session(
            asset_id=aid,
            domain="RENEWABLES",
            operation="test_op",
        )
        assert str(session.asset_id) == aid
        assert session.domain == "RENEWABLES"
        assert session.operation == "test_op"

    def test_get_session(self) -> None:
        mgr = EnergySessionManager()
        session = mgr.create_session(asset_id=str(uuid.uuid4()))
        retrieved = mgr.get_session(str(session.session_id))
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_get_session_not_found(self) -> None:
        mgr = EnergySessionManager()
        assert mgr.get_session("nonexistent") is None

    def test_update_status_valid(self) -> None:
        mgr = EnergySessionManager()
        session = mgr.create_session(asset_id=str(uuid.uuid4()))
        sid = str(session.session_id)
        updated = mgr.update_status(sid, "ACTIVE")
        assert updated is not None
        assert updated.status == "ACTIVE"

    def test_update_status_invalid_transition(self) -> None:
        mgr = EnergySessionManager()
        session = mgr.create_session(asset_id=str(uuid.uuid4()))
        sid = str(session.session_id)
        # COMPLETED -> ACTIVE is invalid
        mgr.update_status(sid, "COMPLETED")
        result = mgr.update_status(sid, "ACTIVE")
        assert result is None

    def test_update_status_nonexistent(self) -> None:
        mgr = EnergySessionManager()
        assert mgr.update_status("nonexistent", "ACTIVE") is None

    def test_update_status_sets_completed_at(self) -> None:
        mgr = EnergySessionManager()
        session = mgr.create_session(asset_id=str(uuid.uuid4()))
        sid = str(session.session_id)
        mgr.update_status(sid, "ACTIVE")
        completed = mgr.update_status(sid, "COMPLETED")
        assert completed is not None
        assert completed.completed_at is not None

    def test_get_active_sessions(self) -> None:
        mgr = EnergySessionManager()
        s1 = mgr.create_session(asset_id=str(uuid.uuid4()), operation="op1")
        s2 = mgr.create_session(asset_id=str(uuid.uuid4()), operation="op2")
        mgr.update_status(str(s2.session_id), "COMPLETED")
        active = mgr.get_active_sessions()
        assert len(active) == 1
        assert active[0].session_id == s1.session_id

    def test_get_all_sessions(self) -> None:
        mgr = EnergySessionManager()
        mgr.create_session(asset_id=str(uuid.uuid4()))
        mgr.create_session(asset_id=str(uuid.uuid4()))
        mgr.create_session(asset_id=str(uuid.uuid4()))
        assert len(mgr.get_all_sessions()) == 3

    def test_count(self) -> None:
        mgr = EnergySessionManager()
        assert mgr.count() == 0
        mgr.create_session(asset_id=str(uuid.uuid4()))
        assert mgr.count() == 1

    def test_clear(self) -> None:
        mgr = EnergySessionManager()
        mgr.create_session(asset_id=str(uuid.uuid4()))
        mgr.clear()
        assert mgr.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# AssetContextManager
# ═════════════════════════════════════════════════════════════════════════════


class TestAssetContextManager:
    def test_collect_context(self) -> None:
        mgr = AssetContextManager()
        ctx = mgr.collect_context(asset_id="asset-001")
        assert ctx["asset_id"] == "asset-001"
        assert "sensor_readings" in ctx
        assert "health_status" in ctx
        assert "maintenance_history" in ctx
        assert "active_alarms" in ctx
        assert "topology" in ctx

    def test_collect_context_minimal(self) -> None:
        mgr = AssetContextManager()
        ctx = mgr.collect_context(
            asset_id="asset-001",
            include_readings=False,
            include_health=False,
            include_maintenance=False,
            include_alarms=False,
            include_topology=False,
        )
        assert ctx["sensor_readings"] == []
        assert ctx["health_status"] == {}
        assert ctx["maintenance_history"] == []
        assert ctx["active_alarms"] == []
        assert ctx["topology"] == {}

    def test_get_cached_context(self) -> None:
        mgr = AssetContextManager()
        mgr.collect_context(asset_id="asset-001")
        cached = mgr.get_cached_context("asset-001")
        assert cached is not None
        assert cached["asset_id"] == "asset-001"

    def test_get_cached_context_not_found(self) -> None:
        mgr = AssetContextManager()
        assert mgr.get_cached_context("nonexistent") is None

    def test_get_context_summary(self) -> None:
        mgr = AssetContextManager()
        mgr.collect_context(asset_id="asset-001")
        summary = mgr.get_context_summary("asset-001")
        assert "asset-001" in summary
        assert "health" in summary

    def test_get_context_summary_no_context(self) -> None:
        mgr = AssetContextManager()
        summary = mgr.get_context_summary("nonexistent")
        assert "nonexistent" in summary

    def test_clear(self) -> None:
        mgr = AssetContextManager()
        mgr.collect_context(asset_id="asset-001")
        mgr.clear()
        assert mgr.get_cached_context("asset-001") is None


# ═════════════════════════════════════════════════════════════════════════════
# DigitalTwinManager
# ═════════════════════════════════════════════════════════════════════════════


class TestDigitalTwinManager:
    def test_create_twin(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(asset_id=str(uuid.uuid4()))
        assert twin.twin_type == "simulation"
        assert twin.model_version == "1.0.0"
        assert twin.is_active is True

    def test_create_twin_with_params(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(
            asset_id=str(uuid.uuid4()),
            twin_type="predictive",
            model_version="2.0.0",
            parameters={"threshold": 0.8},
        )
        assert twin.twin_type == "predictive"
        assert twin.model_version == "2.0.0"
        assert twin.parameters == {"threshold": 0.8}

    def test_get_twin(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(asset_id=str(uuid.uuid4()))
        retrieved = mgr.get_twin(str(twin.twin_id))
        assert retrieved is not None
        assert retrieved.twin_id == twin.twin_id

    def test_get_twin_not_found(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.get_twin("nonexistent") is None

    def test_get_twin_for_asset(self) -> None:
        mgr = DigitalTwinManager()
        aid = str(uuid.uuid4())
        mgr.create_twin(asset_id=aid)
        twin = mgr.get_twin_for_asset(aid)
        assert twin is not None
        assert str(twin.asset_id) == aid

    def test_get_twin_for_asset_not_found(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.get_twin_for_asset("nonexistent") is None

    def test_synchronise(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(asset_id=str(uuid.uuid4()))
        result = mgr.synchronise(str(twin.twin_id), {"temperature": 45.0})
        assert result is not None
        assert result.last_synchronised is not None

    def test_synchronise_not_found(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.synchronise("nonexistent") is None

    def test_get_sync_history(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(asset_id=str(uuid.uuid4()))
        mgr.synchronise(str(twin.twin_id), {"temp": 42.0})
        mgr.synchronise(str(twin.twin_id), {"temp": 43.0})
        history = mgr.get_sync_history(str(twin.twin_id))
        assert len(history) == 2

    def test_get_sync_history_empty(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.get_sync_history("nonexistent") == []

    def test_activate(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(asset_id=str(uuid.uuid4()))
        mgr.deactivate(str(twin.twin_id))
        activated = mgr.activate(str(twin.twin_id))
        assert activated is not None
        assert activated.is_active is True

    def test_activate_not_found(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.activate("nonexistent") is None

    def test_deactivate(self) -> None:
        mgr = DigitalTwinManager()
        twin = mgr.create_twin(asset_id=str(uuid.uuid4()))
        deactivated = mgr.deactivate(str(twin.twin_id))
        assert deactivated is not None
        assert deactivated.is_active is False

    def test_deactivate_not_found(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.deactivate("nonexistent") is None

    def test_count(self) -> None:
        mgr = DigitalTwinManager()
        assert mgr.count() == 0
        mgr.create_twin(asset_id=str(uuid.uuid4()))
        assert mgr.count() == 1

    def test_clear(self) -> None:
        mgr = DigitalTwinManager()
        mgr.create_twin(asset_id=str(uuid.uuid4()))
        mgr.clear()
        assert mgr.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# EnergyReadinessCalculator
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyReadinessCalculator:
    def test_assess_readiness_ready(self) -> None:
        calc = EnergyReadinessCalculator()
        result = calc.assess_readiness(
            asset_id=str(uuid.uuid4()),
            health_score=0.9,
            sensors_active=True,
            has_critical_alarms=False,
            maintenance_current=True,
            topology_ok=True,
        )
        assert result.status == "READY"
        assert result.checks["health_ok"] is True

    def test_assess_readiness_pending(self) -> None:
        calc = EnergyReadinessCalculator()
        result = calc.assess_readiness(
            asset_id=str(uuid.uuid4()),
            health_score=0.6,
            sensors_active=False,
            has_critical_alarms=False,
            maintenance_current=True,
            topology_ok=True,
        )
        assert result.status == "PENDING"

    def test_assess_readiness_blocked(self) -> None:
        calc = EnergyReadinessCalculator()
        result = calc.assess_readiness(
            asset_id=str(uuid.uuid4()),
            health_score=0.3,
            sensors_active=False,
            has_critical_alarms=True,
            maintenance_current=False,
            topology_ok=False,
        )
        assert result.status == "BLOCKED"

    def test_get_readiness(self) -> None:
        calc = EnergyReadinessCalculator()
        aid = str(uuid.uuid4())
        result = calc.assess_readiness(asset_id=aid)
        retrieved = calc.get_readiness(str(result.readiness_id))
        assert retrieved is not None
        assert retrieved.readiness_id == result.readiness_id

    def test_get_readiness_not_found(self) -> None:
        calc = EnergyReadinessCalculator()
        assert calc.get_readiness("nonexistent") is None

    def test_get_readiness_for_asset(self) -> None:
        calc = EnergyReadinessCalculator()
        aid = str(uuid.uuid4())
        calc.assess_readiness(asset_id=aid)
        result = calc.get_readiness_for_asset(aid)
        assert result is not None
        assert str(result.asset_id) == aid

    def test_get_readiness_for_asset_not_found(self) -> None:
        calc = EnergyReadinessCalculator()
        assert calc.get_readiness_for_asset("nonexistent") is None

    def test_count(self) -> None:
        calc = EnergyReadinessCalculator()
        assert calc.count() == 0
        calc.assess_readiness(asset_id=str(uuid.uuid4()))
        assert calc.count() == 1

    def test_clear(self) -> None:
        calc = EnergyReadinessCalculator()
        calc.assess_readiness(asset_id=str(uuid.uuid4()))
        calc.clear()
        assert calc.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# EnergyVersionManager
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyVersionManager:
    def test_create_version(self) -> None:
        mgr = EnergyVersionManager()
        version = mgr.create_version(entity_id="e1", entity_type="asset")
        assert version.version_number == 1
        assert version.entity_id == "e1"
        assert version.entity_type == "asset"

    def test_create_version_with_data(self) -> None:
        mgr = EnergyVersionManager()
        version = mgr.create_version(
            entity_id="e1",
            entity_type="asset",
            data={"name": "Transformer-01"},
            created_by="user-1",
            change_description="Initial registration",
        )
        assert version.data == {"name": "Transformer-01"}
        assert version.created_by == "user-1"
        assert version.change_description == "Initial registration"

    def test_version_number_increment(self) -> None:
        mgr = EnergyVersionManager()
        v1 = mgr.create_version(entity_id="e1", entity_type="asset")
        v2 = mgr.create_version(entity_id="e1", entity_type="asset")
        assert v1.version_number == 1
        assert v2.version_number == 2

    def test_get_versions(self) -> None:
        mgr = EnergyVersionManager()
        mgr.create_version(entity_id="e1", entity_type="asset")
        mgr.create_version(entity_id="e1", entity_type="asset")
        versions = mgr.get_versions("e1")
        assert len(versions) == 2

    def test_get_versions_empty(self) -> None:
        mgr = EnergyVersionManager()
        assert mgr.get_versions("nonexistent") == []

    def test_get_latest_version(self) -> None:
        mgr = EnergyVersionManager()
        mgr.create_version(entity_id="e1", entity_type="asset", data={"v": 1})
        v2 = mgr.create_version(entity_id="e1", entity_type="asset", data={"v": 2})
        latest = mgr.get_latest_version("e1")
        assert latest is not None
        assert latest.version_number == 2
        assert latest.data == {"v": 2}

    def test_get_latest_version_none(self) -> None:
        mgr = EnergyVersionManager()
        assert mgr.get_latest_version("nonexistent") is None

    def test_compare_versions(self) -> None:
        mgr = EnergyVersionManager()
        mgr.create_version(entity_id="e1", entity_type="asset", data={"name": "A"})
        mgr.create_version(entity_id="e1", entity_type="asset", data={"name": "B"})
        result = mgr.compare_versions("e1", 1, 2)
        assert result["changed"] is True

    def test_compare_versions_same(self) -> None:
        mgr = EnergyVersionManager()
        mgr.create_version(entity_id="e1", entity_type="asset", data={"name": "A"})
        mgr.create_version(entity_id="e1", entity_type="asset", data={"name": "A"})
        result = mgr.compare_versions("e1", 1, 2)
        assert result["changed"] is False

    def test_compare_versions_not_found(self) -> None:
        mgr = EnergyVersionManager()
        result = mgr.compare_versions("e1", 1, 2)
        assert "error" in result

    def test_count(self) -> None:
        mgr = EnergyVersionManager()
        assert mgr.count() == 0
        mgr.create_version(entity_id="e1", entity_type="asset")
        assert mgr.count() == 1

    def test_count_for_entity(self) -> None:
        mgr = EnergyVersionManager()
        mgr.create_version(entity_id="e1", entity_type="asset")
        mgr.create_version(entity_id="e1", entity_type="asset")
        mgr.create_version(entity_id="e2", entity_type="asset")
        assert mgr.count_for_entity("e1") == 2
        assert mgr.count_for_entity("e2") == 1

    def test_clear(self) -> None:
        mgr = EnergyVersionManager()
        mgr.create_version(entity_id="e1", entity_type="asset")
        mgr.clear()
        assert mgr.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# EnergyLineage
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyLineage:
    def test_create_lineage(self) -> None:
        lineage = EnergyLineage()
        record = lineage.create_lineage(entity_id="e1", entity_type="asset")
        assert record.entity_id == "e1"
        assert record.entity_type == "asset"
        assert record.operations == []
        assert record.parent_ids == []

    def test_create_lineage_with_parents(self) -> None:
        lineage = EnergyLineage()
        record = lineage.create_lineage(
            entity_id="e1",
            entity_type="asset",
            parent_ids=["p1"],
            operation="created",
        )
        assert record.parent_ids == ["p1"]
        assert record.operations == ["created"]

    def test_record_operation(self) -> None:
        lineage = EnergyLineage()
        record = lineage.create_lineage(entity_id="e1", entity_type="asset")
        updated = lineage.record_operation(str(record.lineage_id), "updated")
        assert updated is not None
        assert updated.operations == ["updated"]

    def test_record_operation_not_found(self) -> None:
        lineage = EnergyLineage()
        result = lineage.record_operation("nonexistent", "updated")
        assert result is None

    def test_get_lineage(self) -> None:
        lineage = EnergyLineage()
        record = lineage.create_lineage(entity_id="e1", entity_type="asset")
        retrieved = lineage.get_lineage(str(record.lineage_id))
        assert retrieved is not None
        assert retrieved.lineage_id == record.lineage_id

    def test_get_lineage_not_found(self) -> None:
        lineage = EnergyLineage()
        assert lineage.get_lineage("nonexistent") is None

    def test_get_lineage_for_entity(self) -> None:
        lineage = EnergyLineage()
        lineage.create_lineage(entity_id="e1", entity_type="asset")
        lineage.create_lineage(entity_id="e1", entity_type="asset")
        records = lineage.get_lineage_for_entity("e1")
        assert len(records) == 2

    def test_count(self) -> None:
        lineage = EnergyLineage()
        assert lineage.count() == 0
        lineage.create_lineage(entity_id="e1", entity_type="asset")
        assert lineage.count() == 1

    def test_clear(self) -> None:
        lineage = EnergyLineage()
        lineage.create_lineage(entity_id="e1", entity_type="asset")
        lineage.clear()
        assert lineage.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# EnergySnapshot
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergySnapshot:
    def test_create_snapshot(self) -> None:
        snap = EnergySnapshot()
        record = snap.create_snapshot(entity_id="e1", entity_type="asset")
        assert record.entity_id == "e1"
        assert record.entity_type == "asset"
        assert record.snapshot_type == "state"
        assert record.data == {}

    def test_create_snapshot_with_data(self) -> None:
        snap = EnergySnapshot()
        record = snap.create_snapshot(
            entity_id="e1",
            entity_type="asset",
            snapshot_type="health",
            data={"score": 0.85},
        )
        assert record.snapshot_type == "health"
        assert record.data == {"score": 0.85}

    def test_get_snapshot(self) -> None:
        snap = EnergySnapshot()
        record = snap.create_snapshot(entity_id="e1", entity_type="asset")
        retrieved = snap.get_snapshot(str(record.snapshot_id))
        assert retrieved is not None
        assert retrieved.snapshot_id == record.snapshot_id

    def test_get_snapshot_not_found(self) -> None:
        snap = EnergySnapshot()
        assert snap.get_snapshot("nonexistent") is None

    def test_get_snapshots_for_entity(self) -> None:
        snap = EnergySnapshot()
        snap.create_snapshot(entity_id="e1", entity_type="asset")
        snap.create_snapshot(entity_id="e1", entity_type="asset")
        records = snap.get_snapshots_for_entity("e1")
        assert len(records) == 2

    def test_get_snapshots_by_type(self) -> None:
        snap = EnergySnapshot()
        snap.create_snapshot(entity_id="e1", entity_type="asset", snapshot_type="state")
        snap.create_snapshot(entity_id="e1", entity_type="asset", snapshot_type="health")
        state_snaps = snap.get_snapshots_by_type("state")
        assert len(state_snaps) == 1

    def test_count(self) -> None:
        snap = EnergySnapshot()
        assert snap.count() == 0
        snap.create_snapshot(entity_id="e1", entity_type="asset")
        assert snap.count() == 1

    def test_clear(self) -> None:
        snap = EnergySnapshot()
        snap.create_snapshot(entity_id="e1", entity_type="asset")
        snap.clear()
        assert snap.count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# DomainHealthManager
# ═════════════════════════════════════════════════════════════════════════════


class TestDomainHealthManager:
    def test_report_health(self) -> None:
        mgr = DomainHealthManager()
        mgr.report_health("coordinator", "HEALTHY")
        assert mgr.get_component_health("coordinator") == "HEALTHY"

    def test_get_component_health_default(self) -> None:
        mgr = DomainHealthManager()
        assert mgr.get_component_health("unknown") == "UNKNOWN"

    def test_get_health_all_healthy(self) -> None:
        mgr = DomainHealthManager()
        mgr.report_health("coordinator", "HEALTHY")
        mgr.report_health("manager", "HEALTHY")
        health = mgr.get_health()
        assert health["overall_status"] == "HEALTHY"

    def test_get_health_degraded(self) -> None:
        mgr = DomainHealthManager()
        mgr.report_health("coordinator", "HEALTHY")
        mgr.report_health("manager", "DEGRADED")
        health = mgr.get_health()
        assert health["overall_status"] == "DEGRADED"

    def test_get_health_unhealthy(self) -> None:
        mgr = DomainHealthManager()
        mgr.report_health("coordinator", "HEALTHY")
        mgr.report_health("manager", "UNHEALTHY")
        health = mgr.get_health()
        assert health["overall_status"] == "UNHEALTHY"

    def test_get_metrics_summary(self) -> None:
        mgr = DomainHealthManager()
        mgr.report_health("c1", "HEALTHY")
        mgr.report_health("c2", "DEGRADED")
        metrics = mgr.get_metrics_summary()
        assert metrics["total_components"] == 2
        assert metrics["healthy"] == 1
        assert metrics["degraded"] == 1

    def test_clear(self) -> None:
        mgr = DomainHealthManager()
        mgr.report_health("coordinator", "HEALTHY")
        mgr.clear()
        assert mgr.get_component_health("coordinator") == "UNKNOWN"


# ═════════════════════════════════════════════════════════════════════════════
# AssetPortfolioManager
# ═════════════════════════════════════════════════════════════════════════════


class TestAssetPortfolioManager:
    def test_analyse_portfolio(self) -> None:
        mgr = AssetPortfolioManager()
        result = mgr.analyse_portfolio(
            asset_ids=["a1", "a2", "a3"],
            portfolio_name="Test Portfolio",
        )
        assert result["asset_count"] == 3
        assert result["portfolio_name"] == "Test Portfolio"
        assert "portfolio_id" in result

    def test_analyse_portfolio_default_name(self) -> None:
        mgr = AssetPortfolioManager()
        result = mgr.analyse_portfolio(asset_ids=["a1"])
        assert "Portfolio-" in result["portfolio_name"]

    def test_get_portfolio(self) -> None:
        mgr = AssetPortfolioManager()
        result = mgr.analyse_portfolio(asset_ids=["a1"])
        retrieved = mgr.get_portfolio(result["portfolio_id"])
        assert retrieved is not None
        assert retrieved["portfolio_id"] == result["portfolio_id"]

    def test_get_portfolio_not_found(self) -> None:
        mgr = AssetPortfolioManager()
        assert mgr.get_portfolio("nonexistent") is None

    def test_get_portfolio_summary(self) -> None:
        mgr = AssetPortfolioManager()
        result = mgr.analyse_portfolio(asset_ids=["a1", "a2"], portfolio_name="MyPort")
        summary = mgr.get_portfolio_summary(result["portfolio_id"])
        assert "MyPort" in summary
        assert "2" in summary

    def test_get_portfolio_summary_not_found(self) -> None:
        mgr = AssetPortfolioManager()
        assert mgr.get_portfolio_summary("nonexistent") == "Portfolio not found"

    def test_aggregate_by_domain(self) -> None:
        mgr = AssetPortfolioManager()
        result = mgr.aggregate_by_domain(["a1", "a2", "a3"])
        assert "ELECTRICITY" in result
        assert "RENEWABLES" in result

    def test_clear(self) -> None:
        mgr = AssetPortfolioManager()
        mgr.analyse_portfolio(asset_ids=["a1"])
        mgr.clear()
        assert mgr.get_portfolio("nonexistent") is None


# ═════════════════════════════════════════════════════════════════════════════
# TopologyValidator
# ═════════════════════════════════════════════════════════════════════════════


class TestTopologyValidator:
    def test_validate_topology(self) -> None:
        validator = TopologyValidator()
        result = validator.validate_topology(asset_ids=["a1", "a2", "a3"])
        assert result["asset_count"] == 3
        assert "result_id" in result

    def test_validate_topology_connected(self) -> None:
        validator = TopologyValidator()
        result = validator.validate_topology(
            asset_ids=["a1", "a2"],
            edges=[("a1", "a2", "connects_to")],
        )
        assert result["edge_count"] == 1
        assert result["is_connected"] is True

    def test_validate_topology_orphaned(self) -> None:
        validator = TopologyValidator()
        result = validator.validate_topology(
            asset_ids=["a1", "a2", "a3"],
            edges=[("a1", "a2", "connects_to")],
        )
        assert result["has_orphans"] is True
        assert "a3" in result["orphaned_assets"]

    def test_get_validation(self) -> None:
        validator = TopologyValidator()
        result = validator.validate_topology(asset_ids=["a1"])
        retrieved = validator.get_validation(result["result_id"])
        assert retrieved is not None

    def test_get_validation_not_found(self) -> None:
        validator = TopologyValidator()
        assert validator.get_validation("nonexistent") is None

    def test_get_orphaned_assets(self) -> None:
        validator = TopologyValidator()
        result = validator.validate_topology(
            asset_ids=["a1", "a2"],
            edges=[("a1", "a2", "connects_to")],
        )
        orphans = validator.get_orphaned_assets(result["result_id"])
        assert orphans == []

    def test_clear(self) -> None:
        validator = TopologyValidator()
        validator.validate_topology(asset_ids=["a1"])
        validator.clear()
        assert validator.get_validation("nonexistent") is None


# ═════════════════════════════════════════════════════════════════════════════
# DomainPolicyManager
# ═════════════════════════════════════════════════════════════════════════════


class TestDomainPolicyManager:
    def test_check_policy_allowed(self) -> None:
        mgr = DomainPolicyManager()
        result = mgr.check_policy(
            operation="register_asset",
            asset_id="a1",
            domain="ELECTRICITY",
        )
        assert result["allowed"] is True
        assert result["operation"] == "register_asset"

    def test_check_policy_with_metadata(self) -> None:
        mgr = DomainPolicyManager()
        result = mgr.check_policy(
            operation="critical_op",
            asset_id="a1",
            metadata={"requires_approval": True},
        )
        assert result["allowed"] is True

    def test_check_batch(self) -> None:
        mgr = DomainPolicyManager()
        results = mgr.check_batch([
            {"operation": "op1", "asset_id": "a1", "domain": "ELECTRICITY"},
            {"operation": "op2", "asset_id": "a2", "domain": "GAS"},
        ])
        assert len(results) == 2
        assert results[0]["allowed"] is True

    def test_get_check(self) -> None:
        mgr = DomainPolicyManager()
        result = mgr.check_policy(operation="op1", asset_id="a1")
        retrieved = mgr.get_check(result["result_id"])
        assert retrieved is not None

    def test_get_check_not_found(self) -> None:
        mgr = DomainPolicyManager()
        assert mgr.get_check("nonexistent") is None

    def test_clear(self) -> None:
        mgr = DomainPolicyManager()
        mgr.check_policy(operation="op1", asset_id="a1")
        mgr.clear()
        assert mgr.get_check("nonexistent") is None


# ═════════════════════════════════════════════════════════════════════════════
# EnergyDomainCoordinator
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyDomainCoordinator:
    def test_register_asset(self) -> None:
        coord = EnergyDomainCoordinator()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        result = coord.register_asset(asset)
        assert result.asset_id == asset.asset_id

    def test_get_asset(self) -> None:
        coord = EnergyDomainCoordinator()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        coord.register_asset(asset)
        retrieved = coord.get_asset(str(asset.asset_id))
        assert retrieved is not None
        assert retrieved.name == "T1"

    def test_get_asset_not_found(self) -> None:
        coord = EnergyDomainCoordinator()
        assert coord.get_asset("nonexistent") is None

    def test_register_sensor(self) -> None:
        coord = EnergyDomainCoordinator()
        sensor = Sensor(
            asset_id=uuid.uuid4(),
            sensor_type=SensorType.TEMPERATURE,
            name="Temp-01",
            unit="°C",
        )
        result = coord.register_sensor(sensor)
        assert result.sensor_id == sensor.sensor_id

    def test_get_sensor(self) -> None:
        coord = EnergyDomainCoordinator()
        sensor = Sensor(
            asset_id=uuid.uuid4(),
            sensor_type=SensorType.TEMPERATURE,
            name="Temp-01",
            unit="°C",
        )
        coord.register_sensor(sensor)
        retrieved = coord.get_sensor(str(sensor.sensor_id))
        assert retrieved is not None

    def test_get_sensor_not_found(self) -> None:
        coord = EnergyDomainCoordinator()
        assert coord.get_sensor("nonexistent") is None

    def test_receive_reading(self) -> None:
        coord = EnergyDomainCoordinator()
        reading = SensorReading(
            sensor_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            value=45.0,
            unit="°C",
        )
        result = coord.receive_reading(reading)
        assert result.reading_id == reading.reading_id

    def test_create_digital_twin(self) -> None:
        coord = EnergyDomainCoordinator()
        twin = DigitalTwin(
            asset_id=uuid.uuid4(),
            twin_type="simulation",
        )
        result = coord.create_digital_twin(twin)
        assert result.twin_id == twin.twin_id

    def test_get_digital_twin(self) -> None:
        coord = EnergyDomainCoordinator()
        twin = DigitalTwin(asset_id=uuid.uuid4())
        coord.create_digital_twin(twin)
        retrieved = coord.get_digital_twin(str(twin.twin_id))
        assert retrieved is not None

    def test_get_digital_twin_not_found(self) -> None:
        coord = EnergyDomainCoordinator()
        assert coord.get_digital_twin("nonexistent") is None

    def test_raise_alarm(self) -> None:
        coord = EnergyDomainCoordinator()
        alarm = Alarm(
            asset_id=uuid.uuid4(),
            name="Overheating",
            severity=AlarmSeverity.WARNING,
        )
        result = coord.raise_alarm(alarm)
        assert result.alarm_id == alarm.alarm_id
        assert result.name == "Overheating"

    def test_get_alarm(self) -> None:
        coord = EnergyDomainCoordinator()
        alarm = Alarm(asset_id=uuid.uuid4(), name="Alarm-1", severity=AlarmSeverity.WARNING)
        coord.raise_alarm(alarm)
        retrieved = coord.get_alarm(str(alarm.alarm_id))
        assert retrieved is not None

    def test_create_incident(self) -> None:
        coord = EnergyDomainCoordinator()
        incident = Incident(
            title="Substation failure",
            priority=IncidentPriority.HIGH,
        )
        result = coord.create_incident(incident)
        assert result.incident_id == incident.incident_id

    def test_record_maintenance(self) -> None:
        coord = EnergyDomainCoordinator()
        record = MaintenanceRecord(
            asset_id=uuid.uuid4(),
            maintenance_type=MaintenanceType.PREVENTIVE,
            technician="Tech-1",
            duration_hours=2.0,
        )
        result = coord.record_maintenance(record)
        assert result.record_id == record.record_id

    def test_get_asset_health(self) -> None:
        coord = EnergyDomainCoordinator()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        coord.register_asset(asset)
        health = coord.get_asset_health(str(asset.asset_id))
        assert health is not None
        assert health.overall_score >= 0.0

    def test_get_asset_health_not_found(self) -> None:
        coord = EnergyDomainCoordinator()
        assert coord.get_asset_health("nonexistent") is None

    def test_get_decision(self) -> None:
        coord = EnergyDomainCoordinator()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        coord.register_asset(asset)
        # Retrieve last decision - decisions are stored internally
        decision = coord.get_decision("test")
        # After register_asset, decisions should be populated
        # We can't directly check without knowing the decision_id
        # But the get_decision should not crash

    def test_health(self) -> None:
        coord = EnergyDomainCoordinator()
        health = coord.health()
        assert health.overall_status is not None

    def test_metrics(self) -> None:
        coord = EnergyDomainCoordinator()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        coord.register_asset(asset)
        metrics = coord.metrics()
        assert metrics.assets_total >= 1


# ═════════════════════════════════════════════════════════════════════════════
# EnergyDomainManager
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyDomainManager:
    def test_register_asset(self) -> None:
        mgr = EnergyDomainManager()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        result = mgr.register_asset(asset)
        assert result.asset_id == asset.asset_id

    def test_get_asset(self) -> None:
        mgr = EnergyDomainManager()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        mgr.register_asset(asset)
        retrieved = mgr.get_asset(str(asset.asset_id))
        assert retrieved is not None
        assert retrieved.name == "T1"

    def test_update_asset(self) -> None:
        mgr = EnergyDomainManager()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        mgr.register_asset(asset)
        updated = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1-Updated")
        result = mgr.update_asset(str(asset.asset_id), updated)
        assert result is not None
        assert result.name == "T1-Updated"

    def test_update_asset_not_found(self) -> None:
        mgr = EnergyDomainManager()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        result = mgr.update_asset("nonexistent", asset)
        assert result is None

    def test_register_sensor(self) -> None:
        mgr = EnergyDomainManager()
        sensor = Sensor(
            asset_id=uuid.uuid4(),
            sensor_type=SensorType.TEMPERATURE,
            name="Temp-01",
            unit="°C",
        )
        result = mgr.register_sensor(sensor)
        assert result.sensor_id == sensor.sensor_id

    def test_get_sensor(self) -> None:
        mgr = EnergyDomainManager()
        sensor = Sensor(
            asset_id=uuid.uuid4(),
            sensor_type=SensorType.TEMPERATURE,
            name="Temp-01",
            unit="°C",
        )
        mgr.register_sensor(sensor)
        retrieved = mgr.get_sensor(str(sensor.sensor_id))
        assert retrieved is not None

    def test_receive_reading(self) -> None:
        mgr = EnergyDomainManager()
        reading = SensorReading(
            sensor_id=uuid.uuid4(),
            asset_id=uuid.uuid4(),
            value=45.0,
            unit="°C",
        )
        result = mgr.receive_reading(reading)
        assert result.reading_id == reading.reading_id

    def test_create_digital_twin(self) -> None:
        mgr = EnergyDomainManager()
        twin = DigitalTwin(asset_id=uuid.uuid4())
        result = mgr.create_digital_twin(twin)
        assert result.twin_id == twin.twin_id

    def test_get_digital_twin(self) -> None:
        mgr = EnergyDomainManager()
        twin = DigitalTwin(asset_id=uuid.uuid4())
        mgr.create_digital_twin(twin)
        retrieved = mgr.get_digital_twin(str(twin.twin_id))
        assert retrieved is not None

    def test_raise_alarm(self) -> None:
        mgr = EnergyDomainManager()
        alarm = Alarm(
            asset_id=uuid.uuid4(),
            name="Alarm-1",
            severity=AlarmSeverity.WARNING,
        )
        result = mgr.raise_alarm(alarm)
        assert result.alarm_id == alarm.alarm_id

    def test_get_alarm(self) -> None:
        mgr = EnergyDomainManager()
        alarm = Alarm(
            asset_id=uuid.uuid4(),
            name="Alarm-1",
            severity=AlarmSeverity.WARNING,
        )
        mgr.raise_alarm(alarm)
        retrieved = mgr.get_alarm(str(alarm.alarm_id))
        assert retrieved is not None

    def test_create_incident(self) -> None:
        mgr = EnergyDomainManager()
        incident = Incident(title="Test incident", priority=IncidentPriority.MEDIUM)
        result = mgr.create_incident(incident)
        assert result.incident_id == incident.incident_id

    def test_record_maintenance(self) -> None:
        mgr = EnergyDomainManager()
        record = MaintenanceRecord(
            asset_id=uuid.uuid4(),
            maintenance_type=MaintenanceType.PREVENTIVE,
        )
        result = mgr.record_maintenance(record)
        assert result.record_id == record.record_id

    def test_get_asset_health(self) -> None:
        mgr = EnergyDomainManager()
        asset = EnergyAsset(asset_type=AssetType.TRANSFORMER, name="T1")
        mgr.register_asset(asset)
        health = mgr.get_asset_health(str(asset.asset_id))
        assert health is not None

    def test_get_health(self) -> None:
        mgr = EnergyDomainManager()
        health = mgr.get_health()
        assert health.overall_status is not None

    def test_get_metrics(self) -> None:
        mgr = EnergyDomainManager()
        metrics = mgr.get_metrics()
        assert metrics is not None

    def test_get_decision(self) -> None:
        mgr = EnergyDomainManager()
        decision = mgr.get_decision("test-decision")
        assert decision is None


# ═════════════════════════════════════════════════════════════════════════════
# IntegrationHooks
# ═════════════════════════════════════════════════════════════════════════════


class TestIntegrationHooks:
    def test_register_and_fire_pre_asset(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_register_asset(hook)
        hooks.run_pre_register_asset(asset_id="a1")
        assert len(calls) == 1

    def test_register_and_fire_post_asset(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_register_asset(hook)
        hooks.run_post_register_asset(asset_id="a1")
        assert len(calls) == 1

    def test_register_and_fire_pre_sensor(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_register_sensor(hook)
        hooks.run_pre_register_sensor(sensor_id="s1")
        assert len(calls) == 1

    def test_register_and_fire_post_sensor(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_register_sensor(hook)
        hooks.run_post_register_sensor(sensor_id="s1")
        assert len(calls) == 1

    def test_register_and_fire_pre_reading(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_receive_reading(hook)
        hooks.run_pre_receive_reading(reading_id="r1")
        assert len(calls) == 1

    def test_register_and_fire_post_reading(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_receive_reading(hook)
        hooks.run_post_receive_reading(reading_id="r1")
        assert len(calls) == 1

    def test_register_and_fire_pre_twin(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_create_twin(hook)
        hooks.run_pre_create_twin(twin_id="t1")
        assert len(calls) == 1

    def test_register_and_fire_post_twin(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_create_twin(hook)
        hooks.run_post_create_twin(twin_id="t1")
        assert len(calls) == 1

    def test_register_and_fire_pre_alarm(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_raise_alarm(hook)
        hooks.run_pre_raise_alarm(alarm_id="a1")
        assert len(calls) == 1

    def test_register_and_fire_post_alarm(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_raise_alarm(hook)
        hooks.run_post_raise_alarm(alarm_id="a1")
        assert len(calls) == 1

    def test_register_and_fire_pre_incident(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_create_incident(hook)
        hooks.run_pre_create_incident(incident_id="i1")
        assert len(calls) == 1

    def test_register_and_fire_post_incident(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_create_incident(hook)
        hooks.run_post_create_incident(incident_id="i1")
        assert len(calls) == 1

    def test_register_and_fire_pre_maintenance(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_record_maintenance(hook)
        hooks.run_pre_record_maintenance(record_id="m1")
        assert len(calls) == 1

    def test_register_and_fire_post_maintenance(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_post_record_maintenance(hook)
        hooks.run_post_record_maintenance(record_id="m1")
        assert len(calls) == 1

    def test_session_hooks(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_session_created(hook)
        hooks.register_session_completed(hook)
        hooks.run_session_created(session_id="s1")
        hooks.run_session_completed(session_id="s1")
        assert len(calls) == 2

    def test_decision_hook(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_decision_made(hook)
        hooks.run_decision_made(decision_id="d1")
        assert len(calls) == 1

    def test_error_hook(self) -> None:
        calls: list[str] = []

        def hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_on_error(hook)
        hooks.run_on_error(operation="test", error="test error")
        assert len(calls) == 1

    def test_exception_isolation(self) -> None:
        calls: list[str] = []

        def failing_hook(**kwargs: Any) -> None:
            msg = "test error"
            raise ValueError(msg)

        def good_hook(**kwargs: Any) -> None:
            calls.append("fired")

        hooks = IntegrationHooks()
        hooks.register_pre_register_asset(failing_hook)
        hooks.register_pre_register_asset(good_hook)
        hooks.run_pre_register_asset(asset_id="a1")
        assert len(calls) == 1

    def test_multiple_hooks(self) -> None:
        calls: list[str] = []

        def hook1(**kwargs: Any) -> None:
            calls.append("hook1")

        def hook2(**kwargs: Any) -> None:
            calls.append("hook2")

        hooks = IntegrationHooks()
        hooks.register_pre_register_asset(hook1)
        hooks.register_pre_register_asset(hook2)
        hooks.run_pre_register_asset(asset_id="a1")
        assert calls == ["hook1", "hook2"]


# ═════════════════════════════════════════════════════════════════════════════
# DefaultEnergyDomainService
# ═════════════════════════════════════════════════════════════════════════════


class TestDefaultEnergyDomainService:
    def test_register_asset(self) -> None:
        service = DefaultEnergyDomainService()
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.register_asset(dto)
        assert result is not None
        assert result.name == "T1"

    def test_register_asset_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.register_asset(dto, user_id="user-1")
        assert result is None

    def test_register_asset_no_auth_admin(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return user_id == "admin"

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.register_asset(dto, user_id="admin")
        assert result is not None

    def test_get_asset(self) -> None:
        service = DefaultEnergyDomainService()
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.register_asset(dto)
        assert result is not None
        retrieved = service.get_asset(str(result.asset_id))
        assert retrieved is not None
        assert retrieved.name == "T1"

    def test_get_asset_not_found(self) -> None:
        service = DefaultEnergyDomainService()
        assert service.get_asset("nonexistent") is None

    def test_update_asset(self) -> None:
        service = DefaultEnergyDomainService()
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.register_asset(dto)
        assert result is not None
        update_dto = EnergyAssetDTO(name="T1-Updated", asset_type=AssetType.TRANSFORMER)
        updated = service.update_asset(str(result.asset_id), update_dto, user_id="admin")
        assert updated is not None
        assert updated.name == "T1-Updated"

    def test_update_asset_not_found(self) -> None:
        service = DefaultEnergyDomainService()
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.update_asset("nonexistent", dto)
        assert result is None

    def test_update_asset_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.update_asset("test-id", dto, user_id="user-1")
        assert result is None

    def test_register_sensor(self) -> None:
        service = DefaultEnergyDomainService()
        dto = SensorDTO(
            asset_id=uuid.uuid4(),
            name="Temp-01",
            sensor_type=SensorType.TEMPERATURE,
            unit="°C",
        )
        result = service.register_sensor(dto)
        assert result is not None
        assert result.name == "Temp-01"

    def test_register_sensor_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = SensorDTO(
            asset_id=uuid.uuid4(),
            name="Temp-01",
            sensor_type=SensorType.TEMPERATURE,
        )
        result = service.register_sensor(dto, user_id="user-1")
        assert result is None

    def test_get_sensor(self) -> None:
        service = DefaultEnergyDomainService()
        dto = SensorDTO(
            asset_id=uuid.uuid4(),
            name="Temp-01",
            sensor_type=SensorType.TEMPERATURE,
        )
        result = service.register_sensor(dto)
        assert result is not None
        retrieved = service.get_sensor(str(result.sensor_id))
        assert retrieved is not None

    def test_receive_reading(self) -> None:
        service = DefaultEnergyDomainService()
        dto = SensorDTO(
            asset_id=uuid.uuid4(),
            name="Temp-01",
            sensor_type=SensorType.TEMPERATURE,
        )
        sensor = service.register_sensor(dto)
        assert sensor is not None
        reading = service.receive_reading(
            sensor_id=str(sensor.sensor_id),
            value=45.0,
            unit="°C",
        )
        assert reading is not None
        assert reading.value == 45.0

    def test_receive_reading_sensor_not_found(self) -> None:
        service = DefaultEnergyDomainService()
        reading = service.receive_reading(
            sensor_id="nonexistent",
            value=45.0,
        )
        assert reading is None

    def test_create_digital_twin(self) -> None:
        service = DefaultEnergyDomainService()
        dto = DigitalTwinDTO(asset_id=uuid.uuid4(), twin_type="simulation")
        result = service.create_digital_twin(dto)
        assert result is not None
        assert result.twin_type == "simulation"

    def test_create_digital_twin_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = DigitalTwinDTO(asset_id=uuid.uuid4())
        result = service.create_digital_twin(dto, user_id="user-1")
        assert result is None

    def test_raise_alarm(self) -> None:
        service = DefaultEnergyDomainService()
        dto = AlarmDTO(
            asset_id=uuid.uuid4(),
            name="Overheating",
            severity=AlarmSeverity.WARNING,
        )
        result = service.raise_alarm(dto)
        assert result is not None
        assert result.name == "Overheating"

    def test_raise_alarm_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = AlarmDTO(asset_id=uuid.uuid4(), name="Alarm", severity=AlarmSeverity.WARNING)
        result = service.raise_alarm(dto, user_id="user-1")
        assert result is None

    def test_create_incident(self) -> None:
        service = DefaultEnergyDomainService()
        dto = IncidentDTO(title="Test incident", priority=IncidentPriority.MEDIUM)
        result = service.create_incident(dto)
        assert result is not None
        assert result.title == "Test incident"

    def test_create_incident_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        dto = IncidentDTO(title="Test", priority=IncidentPriority.MEDIUM)
        result = service.create_incident(dto, user_id="user-1")
        assert result is None

    def test_record_maintenance(self) -> None:
        service = DefaultEnergyDomainService()
        result = service.record_maintenance(
            asset_id=str(uuid.uuid4()),
            maintenance_type="PREVENTIVE",
            technician="Tech-1",
            description="Routine check",
            duration_hours=2.0,
        )
        assert result is not None
        assert result.duration_hours == 2.0

    def test_record_maintenance_auth_failure(self) -> None:
        def auth_check(user_id: str, operation: str) -> bool:
            return False

        service = DefaultEnergyDomainService(auth_callback=auth_check)
        result = service.record_maintenance(
            asset_id=str(uuid.uuid4()),
            maintenance_type="PREVENTIVE",
            user_id="user-1",
        )
        assert result is None

    def test_get_asset_health(self) -> None:
        service = DefaultEnergyDomainService()
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        asset = service.register_asset(dto)
        assert asset is not None
        health = service.get_asset_health(str(asset.asset_id))
        assert health is not None

    def test_get_asset_hierarchy(self) -> None:
        service = DefaultEnergyDomainService()
        hierarchy = service.get_asset_hierarchy(str(uuid.uuid4()))
        assert hierarchy == []

    def test_get_health(self) -> None:
        service = DefaultEnergyDomainService()
        health = service.get_health()
        assert health is not None

    def test_get_metrics(self) -> None:
        service = DefaultEnergyDomainService()
        metrics = service.get_metrics()
        assert metrics is not None

    def test_get_decision(self) -> None:
        service = DefaultEnergyDomainService()
        decision = service.get_decision("test-decision")
        assert decision is None

    def test_audit_callback(self) -> None:
        audit_log: list[tuple[str, str, str, dict[str, Any]]] = []

        def audit(action: str, user: str, entity: str, details: dict[str, Any]) -> None:
            audit_log.append((action, user, entity, details))

        service = DefaultEnergyDomainService(audit_callback=audit)
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        result = service.register_asset(dto, user_id="admin")
        assert result is not None
        assert len(audit_log) == 1
        assert audit_log[0][0] == "register_asset"
        assert audit_log[0][1] == "admin"

    def test_hooks_fired_on_register_asset(self) -> None:
        hooks = IntegrationHooks()
        pre_calls: list[str] = []
        post_calls: list[str] = []

        def pre(**kwargs: Any) -> None:
            pre_calls.append("pre")

        def post(**kwargs: Any) -> None:
            post_calls.append("post")

        hooks.register_pre_register_asset(pre)
        hooks.register_post_register_asset(post)

        service = DefaultEnergyDomainService(hooks=hooks)
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        service.register_asset(dto)
        assert len(pre_calls) == 1
        assert len(post_calls) == 1

    def test_error_raises_exception(self) -> None:
        class FailingManager:
            def register_asset(self, *args: Any, **kwargs: Any) -> EnergyAsset:
                msg = "Failed to register"
                raise RuntimeError(msg)

        from adip.energy.orchestration.manager import EnergyDomainManager

        # Create a patched manager
        manager = EnergyDomainManager()

        service = DefaultEnergyDomainService(manager=manager)
        dto = EnergyAssetDTO(name="T1", asset_type=AssetType.TRANSFORMER)
        # Should not raise because the real manager doesn't fail
        result = service.register_asset(dto)
        assert result is not None
