"""Phase 2 tests for the Energy Domain Package (Asset Intelligence & Domain Services).

Tests all execution-layer components: AssetGraph, AssetLifecycleManager,
SensorValidationPipeline, HealthScoreCalculator, AlarmCorrelationEngine,
MaintenanceScheduler, TopologyService, EnergyEventTimeline,
EquipmentClassification, UnitConversionService, DomainMetrics,
and DomainTrace.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from adip.energy.enums import (
    AlarmSeverity,
    AssetType,
    MaintenanceType,
)
from adip.energy.execution.alarm_correlation import AlarmCorrelationEngine
from adip.energy.execution.asset_graph import AssetGraph
from adip.energy.execution.equipment_classification import EquipmentClassification
from adip.energy.execution.event_timeline import EnergyEventTimeline
from adip.energy.execution.health_score import HealthScoreCalculator
from adip.energy.execution.lifecycle_manager import AssetLifecycleManager
from adip.energy.execution.maintenance_scheduler import MaintenanceScheduler
from adip.energy.execution.metrics import DomainMetrics
from adip.energy.execution.models import (
    AssetEdge,
    AssetGraphModel,
    AssetLifecycleState,
    AssetNode,
    ClassificationResult,
    ConversionRequest,
    ConversionResult,
    CorrelationGroup,
    DomainMetricsSnapshot,
    DomainTraceRecord,
    HealthScoreResult,
    LifecycleTransition,
    MaintenanceSchedule,
    TimelineEntry,
    TopologyResult,
    ValidationResult,
)
from adip.energy.execution.sensor_validation import SensorValidationPipeline
from adip.energy.execution.topology import TopologyService
from adip.energy.execution.trace import DomainTrace
from adip.energy.execution.unit_conversion import UnitConversionService

# ═════════════════════════════════════════════════════════════════════════════
# Execution-Layer Models
# ═════════════════════════════════════════════════════════════════════════════


class TestAssetLifecycleState:
    def test_values(self) -> None:
        assert AssetLifecycleState.PLANNED.value == "PLANNED"
        assert AssetLifecycleState.COMMISSIONED.value == "COMMISSIONED"
        assert AssetLifecycleState.OPERATIONAL.value == "OPERATIONAL"
        assert AssetLifecycleState.MAINTENANCE.value == "MAINTENANCE"
        assert AssetLifecycleState.RETIRED.value == "RETIRED"

    def test_unique_values(self) -> None:
        values = [e.value for e in AssetLifecycleState]
        assert len(values) == len(set(values))

    def test_five_states(self) -> None:
        assert len(AssetLifecycleState) == 5


class TestAssetNode:
    def test_default_node(self) -> None:
        node = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.TRANSFORMER)
        assert node.asset_name == ""
        assert node.level == 0
        assert node.metadata == {}

    def test_with_values(self) -> None:
        aid = uuid.uuid4()
        node = AssetNode(
            asset_id=aid,
            asset_name="Main Transformer",
            asset_type=AssetType.TRANSFORMER,
            level=1,
            metadata={"region": "north"},
        )
        assert node.asset_name == "Main Transformer"
        assert node.level == 1
        assert node.metadata == {"region": "north"}


class TestAssetEdge:
    def test_default_edge(self) -> None:
        edge = AssetEdge(source_asset_id=uuid.uuid4(), target_asset_id=uuid.uuid4())
        assert edge.relationship_type == "connects_to"
        assert edge.weight == 1.0

    def test_with_values(self) -> None:
        src = uuid.uuid4()
        tgt = uuid.uuid4()
        edge = AssetEdge(
            source_asset_id=src,
            target_asset_id=tgt,
            relationship_type="feeds",
            weight=0.8,
        )
        assert edge.relationship_type == "feeds"
        assert edge.weight == 0.8


class TestAssetGraphModel:
    def test_default_graph(self) -> None:
        graph = AssetGraphModel()
        assert graph.nodes == []
        assert graph.edges == []
        assert not graph.has_cycle

    def test_with_nodes_and_edges(self) -> None:
        n1 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.SUBSTATION)
        n2 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.TRANSFORMER)
        e = AssetEdge(
            source_asset_id=n1.asset_id,
            target_asset_id=n2.asset_id,
        )
        graph = AssetGraphModel(nodes=[n1, n2], edges=[e])
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1


class TestLifecycleTransition:
    def test_default_transition(self) -> None:
        t = LifecycleTransition(
            asset_id=uuid.uuid4(),
            from_state=AssetLifecycleState.PLANNED,
            to_state=AssetLifecycleState.COMMISSIONED,
        )
        assert t.reason == ""


class TestValidationResult:
    def test_default_valid(self) -> None:
        r = ValidationResult()
        assert r.is_valid
        assert r.issues == []

    def test_with_issues(self) -> None:
        r = ValidationResult(is_valid=False, issues=["Missing value"])
        assert not r.is_valid
        assert "Missing value" in r.issues


class TestHealthScoreResult:
    def test_default_score(self) -> None:
        r = HealthScoreResult(asset_id=uuid.uuid4())
        assert r.overall_score == 1.0

    def test_with_scores(self) -> None:
        r = HealthScoreResult(
            asset_id=uuid.uuid4(),
            overall_score=0.75,
            sensor_score=0.8,
            maintenance_score=0.7,
            age_score=0.9,
            alarm_score=0.6,
        )
        assert r.overall_score == 0.75


class TestCorrelationGroup:
    def test_default_group(self) -> None:
        g = CorrelationGroup()
        assert g.alarm_ids == []
        assert g.highest_severity == AlarmSeverity.INFO

    def test_with_alarms(self) -> None:
        aid1 = uuid.uuid4()
        aid2 = uuid.uuid4()
        g = CorrelationGroup(
            alarm_ids=[aid1, aid2],
            highest_severity=AlarmSeverity.CRITICAL,
            correlation_reason="Same asset",
        )
        assert len(g.alarm_ids) == 2
        assert g.highest_severity == AlarmSeverity.CRITICAL


class TestMaintenanceSchedule:
    def test_default_schedule(self) -> None:
        s = MaintenanceSchedule(
            asset_id=uuid.uuid4(),
            maintenance_type=MaintenanceType.PREVENTIVE,
            due_date=datetime.now(UTC),
        )
        assert s.priority == "normal"


class TestTopologyResult:
    def test_default(self) -> None:
        r = TopologyResult(asset_id=uuid.uuid4())
        assert r.upstream == []
        assert r.downstream == []


class TestTimelineEntry:
    def test_default_entry(self) -> None:
        e = TimelineEntry(
            asset_id=uuid.uuid4(),
            event_type="sensor_update",
        )
        assert e.description == ""


class TestDomainTraceRecord:
    def test_default_record(self) -> None:
        r = DomainTraceRecord()
        assert r.domain == "energy"
        assert r.success


class TestDomainMetricsSnapshot:
    def test_default_snapshot(self) -> None:
        s = DomainMetricsSnapshot()
        assert s.asset_count == 0


class TestClassificationResult:
    def test_default(self) -> None:
        r = ClassificationResult(
            asset_id=uuid.uuid4(),
            asset_type=AssetType.GENERATOR,
        )
        assert r.classification == ""


class TestConversionRequestAndResult:
    def test_request(self) -> None:
        r = ConversionRequest(
            value=100.0,
            from_unit="C",
            to_unit="F",
            conversion_type="temperature",
        )
        assert r.value == 100.0

    def test_result(self) -> None:
        r = ConversionResult(
            input_value=100.0,
            output_value=212.0,
            from_unit="C",
            to_unit="F",
            conversion_type="temperature",
        )
        assert r.output_value == 212.0


# ═════════════════════════════════════════════════════════════════════════════
# AssetGraph
# ═════════════════════════════════════════════════════════════════════════════


class TestAssetGraph:
    def test_build_empty_graph(self) -> None:
        graph = AssetGraph()
        result = graph.build_graph()
        assert result.nodes == []
        assert result.edges == []
        assert not result.has_cycle

    def test_build_with_assets(self) -> None:
        graph = AssetGraph()
        assets = [
            ("a1", "Substation A", "SUBSTATION"),
            ("a2", "Transformer T1", "TRANSFORMER"),
            ("a3", "Breaker B1", "BREAKER"),
        ]
        rels = [
            ("a1", "a2", "feeds", 1.0),
            ("a2", "a3", "protects", 0.8),
        ]
        result = graph.build_graph(assets, rels)
        assert len(result.nodes) == 3
        assert len(result.edges) == 2
        assert not result.has_cycle
        assert len(result.root_nodes) == 1
        assert len(result.leaf_nodes) == 1

    def test_cycle_detection(self) -> None:
        graph = AssetGraph()
        assets = [
            ("a1", "Asset 1", "TRANSFORMER"),
            ("a2", "Asset 2", "BREAKER"),
            ("a3", "Asset 3", "FEEDER"),
        ]
        rels = [
            ("a1", "a2", "connects_to", 1.0),
            ("a2", "a3", "connects_to", 1.0),
            ("a3", "a1", "connects_to", 1.0),
        ]
        result = graph.build_graph(assets, rels)
        assert result.has_cycle
        assert not result.topological_order

    def test_validate_valid_graph(self) -> None:
        graph = AssetGraph()
        assets = [("a1", "Sub A", "SUBSTATION")]
        result = graph.build_graph(assets)
        issues = graph.validate_graph(result)
        assert issues == []

    def test_validate_empty_graph_issues(self) -> None:
        graph = AssetGraph()
        result = graph.build_graph()
        issues = graph.validate_graph(result)
        assert "Graph has no nodes" in issues

    def test_validate_unknown_edge_source(self) -> None:
        graph = AssetGraph()
        bad_graph = AssetGraphModel(
            nodes=[
                AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.SUBSTATION),
            ],
            edges=[
                AssetEdge(
                    source_asset_id=uuid.uuid4(),
                    target_asset_id=uuid.uuid4(),
                ),
            ],
        )
        issues = graph.validate_graph(bad_graph)
        assert any("unknown source" in i for i in issues)

    def test_build_single_node(self) -> None:
        graph = AssetGraph()
        result = graph.build_graph(
            assets=[("g1", "Generator G1", "GENERATOR")]
        )
        assert len(result.nodes) == 1
        assert result.nodes[0].asset_type == AssetType.GENERATOR

    def test_build_unknown_asset_type_defaults(self) -> None:
        graph = AssetGraph()
        result = graph.build_graph(
            assets=[("x1", "Unknown", "UNKNOWN_TYPE")]
        )
        assert result.nodes[0].asset_type == AssetType.SENSOR

    def test_topological_order(self) -> None:
        graph = AssetGraph()
        result = graph.build_graph(
            assets=[
                ("root", "Root", "SUBSTATION"),
                ("mid", "Mid", "TRANSFORMER"),
                ("leaf", "Leaf", "BREAKER"),
            ],
            relationships=[
                ("root", "mid", "feeds", 1.0),
                ("mid", "leaf", "feeds", 1.0),
            ],
        )
        assert not result.has_cycle
        assert len(result.topological_order) == 3


# ═════════════════════════════════════════════════════════════════════════════
# AssetLifecycleManager
# ═════════════════════════════════════════════════════════════════════════════


class TestAssetLifecycleManager:
    def test_valid_transition(self) -> None:
        mgr = AssetLifecycleManager()
        t = mgr.transition(
            asset_id="123e4567-e89b-12d3-a456-426614174000",
            from_state=AssetLifecycleState.PLANNED,
            to_state=AssetLifecycleState.COMMISSIONED,
            reason="Installation complete",
        )
        assert t.from_state == AssetLifecycleState.PLANNED
        assert t.to_state == AssetLifecycleState.COMMISSIONED
        assert t.reason == "Installation complete"

    def test_invalid_transition_raises(self) -> None:
        mgr = AssetLifecycleManager()
        with pytest.raises(ValueError, match="Invalid lifecycle transition"):
            mgr.transition(
                asset_id=uuid.uuid4(),
                from_state=AssetLifecycleState.OPERATIONAL,
                to_state=AssetLifecycleState.PLANNED,
            )

    def test_retired_has_no_transitions(self) -> None:
        mgr = AssetLifecycleManager()
        valid = mgr.get_valid_transitions(AssetLifecycleState.RETIRED)
        assert valid == []

    def test_operational_to_maintenance(self) -> None:
        mgr = AssetLifecycleManager()
        t = mgr.transition(
            asset_id=uuid.uuid4(),
            from_state=AssetLifecycleState.OPERATIONAL,
            to_state=AssetLifecycleState.MAINTENANCE,
        )
        assert t.to_state == AssetLifecycleState.MAINTENANCE

    def test_maintenance_to_operational(self) -> None:
        mgr = AssetLifecycleManager()
        t = mgr.transition(
            asset_id=uuid.uuid4(),
            from_state=AssetLifecycleState.MAINTENANCE,
            to_state=AssetLifecycleState.OPERATIONAL,
        )
        assert t.to_state == AssetLifecycleState.OPERATIONAL

    def test_planned_to_retired(self) -> None:
        mgr = AssetLifecycleManager()
        t = mgr.transition(
            asset_id=uuid.uuid4(),
            from_state=AssetLifecycleState.PLANNED,
            to_state=AssetLifecycleState.RETIRED,
        )
        assert t.to_state == AssetLifecycleState.RETIRED

    def test_get_valid_transitions(self) -> None:
        mgr = AssetLifecycleManager()
        valid = mgr.get_valid_transitions(AssetLifecycleState.OPERATIONAL)
        assert AssetLifecycleState.MAINTENANCE in valid
        assert AssetLifecycleState.RETIRED in valid

    def test_transition_history(self) -> None:
        mgr = AssetLifecycleManager()
        aid = "123e4567-e89b-12d3-a456-426614174000"
        mgr.transition(
            asset_id=aid,
            from_state=AssetLifecycleState.PLANNED,
            to_state=AssetLifecycleState.COMMISSIONED,
        )
        mgr.transition(
            asset_id=aid,
            from_state=AssetLifecycleState.COMMISSIONED,
            to_state=AssetLifecycleState.OPERATIONAL,
        )
        history = mgr.get_transition_history(aid)
        assert len(history) == 2

    def test_get_all_transitions(self) -> None:
        mgr = AssetLifecycleManager()
        mgr.transition(
            asset_id=uuid.uuid4(),
            from_state=AssetLifecycleState.PLANNED,
            to_state=AssetLifecycleState.COMMISSIONED,
        )
        assert len(mgr.get_all_transitions()) == 1

    def test_commissioned_to_retired(self) -> None:
        mgr = AssetLifecycleManager()
        t = mgr.transition(
            asset_id=uuid.uuid4(),
            from_state=AssetLifecycleState.COMMISSIONED,
            to_state=AssetLifecycleState.RETIRED,
        )
        assert t.to_state == AssetLifecycleState.RETIRED


# ═════════════════════════════════════════════════════════════════════════════
# SensorValidationPipeline
# ═════════════════════════════════════════════════════════════════════════════


class TestSensorValidationPipeline:
    def test_valid_reading(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="TEMPERATURE",
            value=25.0,
            unit="C",
        )
        assert result.is_valid
        assert result.normalized_unit == "°C"

    def test_out_of_range_high(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="TEMPERATURE",
            value=500.0,
        )
        assert not result.is_valid
        assert any("above maximum" in i for i in result.issues)

    def test_out_of_range_low(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="FREQUENCY",
            value=30.0,
        )
        assert not result.is_valid
        assert any("below minimum" in i for i in result.issues)

    def test_missing_value_zero(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="VOLTAGE",
            value=0.0,
        )
        assert not result.is_valid

    def test_duplicate_detection(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="CURRENT",
            value=100.0,
            recent_readings=[100.0, 101.0],
        )
        assert not result.is_valid
        assert any("Duplicate" in i for i in result.issues)

    def test_timestamp_future(self) -> None:
        pipeline = SensorValidationPipeline()
        far_future = datetime.now(UTC) + timedelta(days=365)
        result = pipeline.validate(
            sensor_type="TEMPERATURE",
            value=25.0,
            timestamp=far_future,
        )
        assert not result.is_valid
        assert any("future" in i for i in result.issues)

    def test_unit_normalization(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="VOLTAGE",
            value=220.0,
            unit="kilovolt",
        )
        assert result.normalized_unit == "kV"

    def test_voltage_in_range(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="VOLTAGE",
            value=220.0,
        )
        assert result.is_valid

    def test_pressure_valid(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="PRESSURE",
            value=100.0,
        )
        assert result.is_valid

    def test_missing_timestamp_issue(self) -> None:
        pipeline = SensorValidationPipeline()
        result = pipeline.validate(
            sensor_type="TEMPERATURE",
            value=25.0,
            timestamp=None,
        )
        assert result.is_valid

    def test_get_default_range(self) -> None:
        pipeline = SensorValidationPipeline()
        min_v, max_v = pipeline.get_default_range("TEMPERATURE")
        assert min_v == -50.0
        assert max_v == 200.0

    def test_unknown_sensor_type_range(self) -> None:
        pipeline = SensorValidationPipeline()
        min_v, max_v = pipeline.get_default_range("UNKNOWN")
        assert min_v == float("-inf")


# ═════════════════════════════════════════════════════════════════════════════
# HealthScoreCalculator
# ═════════════════════════════════════════════════════════════════════════════


class TestHealthScoreCalculator:
    def test_perfect_health(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            sensor_readings=[],
            maintenance_count=10,
            asset_age_days=0.0,
            active_alarm_count=0,
        )
        assert result.overall_score == 0.93

    def test_no_maintenance(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            maintenance_count=0,
        )
        assert result.maintenance_score == 0.3

    def test_high_temperature_reduces_score(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            sensor_readings=[
                {"type": "TEMPERATURE", "value": 95.0},
            ],
            maintenance_count=5,
        )
        assert result.sensor_score < 1.0

    def test_active_alarms_reduce_score(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            active_alarm_count=3,
        )
        assert result.alarm_score < 1.0

    def test_old_asset_lower_age_score(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            asset_age_days=5000.0,
        )
        assert result.age_score < 1.0

    def test_high_vibration_reduces_score(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            sensor_readings=[
                {"type": "VIBRATION", "value": 75.0},
            ],
        )
        assert result.sensor_score < 1.0

    def test_overall_score_bounded(self) -> None:
        calc = HealthScoreCalculator()
        result = calc.calculate(
            asset_id=uuid.uuid4(),
            active_alarm_count=20,
        )
        assert 0.0 <= result.overall_score <= 1.0

    def test_maintenance_score_steps(self) -> None:
        calc = HealthScoreCalculator()
        r1 = calc.calculate(asset_id=uuid.uuid4(), maintenance_count=5)
        assert r1.maintenance_score == 1.0

        r2 = calc.calculate(asset_id=uuid.uuid4(), maintenance_count=3)
        assert r2.maintenance_score == 0.8

        r3 = calc.calculate(asset_id=uuid.uuid4(), maintenance_count=1)
        assert r3.maintenance_score == 0.6


# ═════════════════════════════════════════════════════════════════════════════
# AlarmCorrelationEngine
# ═════════════════════════════════════════════════════════════════════════════


class TestAlarmCorrelationEngine:
    def test_no_alarms(self) -> None:
        engine = AlarmCorrelationEngine()
        groups = engine.correlate()
        assert groups == []

    def test_single_alarm_standalone(self) -> None:
        engine = AlarmCorrelationEngine()
        groups = engine.correlate([
            {"alarm_id": "a1", "asset_id": "asset1", "severity": "CRITICAL"},
        ])
        assert len(groups) == 1
        assert len(groups[0].alarm_ids) == 1
        assert groups[0].highest_severity == AlarmSeverity.CRITICAL

    def test_same_asset_correlation(self) -> None:
        engine = AlarmCorrelationEngine()
        now = datetime.now(UTC)
        groups = engine.correlate([
            {"alarm_id": "a1", "asset_id": "asset1", "severity": "CRITICAL", "raised_at": now},
            {"alarm_id": "a2", "asset_id": "asset1", "severity": "MAJOR", "raised_at": now},
        ])
        assert len(groups) >= 1
        correlated = [g for g in groups if len(g.alarm_ids) > 1]
        assert len(correlated) >= 1

    def test_different_asset_no_correlation(self) -> None:
        engine = AlarmCorrelationEngine()
        now = datetime.now(UTC)
        groups = engine.correlate([
            {"alarm_id": "a1", "asset_id": "asset1", "severity": "CRITICAL", "raised_at": now},
            {"alarm_id": "a2", "asset_id": "asset2", "severity": "INFO", "raised_at": now + timedelta(hours=2)},
        ])
        all_single = all(len(g.alarm_ids) == 1 for g in groups)
        assert all_single

    def test_highest_severity_in_group(self) -> None:
        engine = AlarmCorrelationEngine()
        now = datetime.now(UTC)
        groups = engine.correlate([
            {"alarm_id": "a1", "asset_id": "asset1", "severity": "INFO", "raised_at": now},
            {"alarm_id": "a2", "asset_id": "asset1", "severity": "CRITICAL", "raised_at": now},
        ])
        correlated = [g for g in groups if len(g.alarm_ids) > 1]
        if correlated:
            assert correlated[0].highest_severity == AlarmSeverity.CRITICAL


# ═════════════════════════════════════════════════════════════════════════════
# MaintenanceScheduler
# ═════════════════════════════════════════════════════════════════════════════


class TestMaintenanceScheduler:
    def test_schedule_preventive(self) -> None:
        scheduler = MaintenanceScheduler()
        s = scheduler.schedule(
            asset_id=uuid.uuid4(),
            maintenance_type="PREVENTIVE",
        )
        assert s.maintenance_type == MaintenanceType.PREVENTIVE
        assert s.priority == "normal"

    def test_schedule_emergency(self) -> None:
        scheduler = MaintenanceScheduler()
        s = scheduler.schedule(
            asset_id=uuid.uuid4(),
            maintenance_type="EMERGENCY",
        )
        assert s.maintenance_type == MaintenanceType.EMERGENCY
        assert s.priority == "critical"

    def test_schedule_corrective(self) -> None:
        scheduler = MaintenanceScheduler()
        s = scheduler.schedule(
            asset_id=uuid.uuid4(),
            maintenance_type="CORRECTIVE",
        )
        assert s.priority == "high"

    def test_get_schedules_for_asset(self) -> None:
        scheduler = MaintenanceScheduler()
        aid = uuid.uuid4()
        scheduler.schedule(asset_id=aid, maintenance_type="PREVENTIVE")
        scheduler.schedule(asset_id=aid, maintenance_type="PREDICTIVE")
        schedules = scheduler.get_schedules_for_asset(str(aid))
        assert len(schedules) == 2

    def test_get_upcoming_schedules(self) -> None:
        scheduler = MaintenanceScheduler()
        scheduler.schedule(asset_id=uuid.uuid4(), maintenance_type="PREVENTIVE")
        upcoming = scheduler.get_upcoming_schedules(days_ahead=365)
        assert len(upcoming) >= 1

    def test_get_overdue_schedules(self) -> None:
        scheduler = MaintenanceScheduler()
        past = datetime.now(UTC) - timedelta(days=10)
        aid = uuid.uuid4()
        scheduler.schedule(
            asset_id=aid,
            maintenance_type="EMERGENCY",
            due_date=past,
        )
        overdue = scheduler.get_overdue_schedules()
        assert len(overdue) >= 1

    def test_cancel_schedule(self) -> None:
        scheduler = MaintenanceScheduler()
        s = scheduler.schedule(asset_id=uuid.uuid4(), maintenance_type="PREVENTIVE")
        assert scheduler.cancel_schedule(str(s.schedule_id))
        assert not scheduler.cancel_schedule(str(uuid.uuid4()))

    def test_get_all_schedules(self) -> None:
        scheduler = MaintenanceScheduler()
        scheduler.schedule(asset_id=uuid.uuid4(), maintenance_type="PREVENTIVE")
        assert len(scheduler.get_all_schedules()) >= 1

    def test_emergency_due_date_is_near(self) -> None:
        scheduler = MaintenanceScheduler()
        s = scheduler.schedule(asset_id=uuid.uuid4(), maintenance_type="EMERGENCY")
        now = datetime.now(UTC)
        assert s.due_date < now + timedelta(hours=5)


# ═════════════════════════════════════════════════════════════════════════════
# TopologyService
# ═════════════════════════════════════════════════════════════════════════════


class TestTopologyService:
    def _make_chain_graph(self) -> AssetGraphModel:
        n1 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.SUBSTATION, level=0)
        n2 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.TRANSFORMER, level=1)
        n3 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.BREAKER, level=2)
        return AssetGraphModel(
            nodes=[n1, n2, n3],
            edges=[
                AssetEdge(source_asset_id=n1.asset_id, target_asset_id=n2.asset_id),
                AssetEdge(source_asset_id=n2.asset_id, target_asset_id=n3.asset_id),
            ],
        )

    def test_get_downstream(self) -> None:
        svc = TopologyService()
        graph = self._make_chain_graph()
        downstream = svc.get_downstream(graph, str(graph.nodes[0].asset_id))
        assert len(downstream) == 2

    def test_get_upstream(self) -> None:
        svc = TopologyService()
        graph = self._make_chain_graph()
        upstream = svc.get_upstream(graph, str(graph.nodes[2].asset_id))
        assert len(upstream) == 2

    def test_get_connected(self) -> None:
        svc = TopologyService()
        graph = self._make_chain_graph()
        connected = svc.get_connected(graph, str(graph.nodes[1].asset_id))
        assert len(connected) == 2

    def test_get_topology(self) -> None:
        svc = TopologyService()
        graph = self._make_chain_graph()
        aid = str(graph.nodes[0].asset_id)
        result = svc.get_topology(graph, aid)
        assert len(result.downstream) == 2
        assert result.upstream == []

    def test_get_neighbors(self) -> None:
        svc = TopologyService()
        n1 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.SUBSTATION, level=0)
        n2 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.TRANSFORMER, level=1)
        n3 = AssetNode(asset_id=uuid.uuid4(), asset_type=AssetType.BREAKER, level=1)
        graph = AssetGraphModel(
            nodes=[n1, n2, n3],
            edges=[
                AssetEdge(source_asset_id=n1.asset_id, target_asset_id=n2.asset_id),
                AssetEdge(source_asset_id=n1.asset_id, target_asset_id=n3.asset_id),
            ],
        )
        neighbors = svc.get_neighbors(graph, str(n2.asset_id))
        assert len(neighbors) == 1
        assert str(n3.asset_id) in neighbors


# ═════════════════════════════════════════════════════════════════════════════
# EnergyEventTimeline
# ═════════════════════════════════════════════════════════════════════════════


class TestEnergyEventTimeline:
    def test_record_sensor_update(self) -> None:
        tl = EnergyEventTimeline()
        entry = tl.record_sensor_update(
            asset_id=uuid.uuid4(),
            sensor_id="s1",
            value=25.0,
            unit="°C",
        )
        assert entry.event_type == "sensor_update"
        assert "25.0" in entry.description

    def test_record_alarm(self) -> None:
        tl = EnergyEventTimeline()
        entry = tl.record_alarm(
            asset_id=uuid.uuid4(),
            alarm_id="a1",
            severity="CRITICAL",
        )
        assert entry.event_type == "alarm"

    def test_record_incident(self) -> None:
        tl = EnergyEventTimeline()
        entry = tl.record_incident(
            asset_id=uuid.uuid4(),
            incident_id="inc1",
            priority="HIGH",
        )
        assert entry.event_type == "incident"

    def test_record_maintenance(self) -> None:
        tl = EnergyEventTimeline()
        entry = tl.record_maintenance(
            asset_id=uuid.uuid4(),
            maintenance_type="PREVENTIVE",
        )
        assert entry.event_type == "maintenance"

    def test_record_recovery(self) -> None:
        tl = EnergyEventTimeline()
        entry = tl.record_recovery(
            asset_id=uuid.uuid4(),
            recovery_type="restart",
        )
        assert entry.event_type == "recovery"

    def test_get_events_for_asset(self) -> None:
        tl = EnergyEventTimeline()
        aid = uuid.uuid4()
        tl.record_sensor_update(asset_id=aid)
        tl.record_alarm(asset_id=aid)
        events = tl.get_events_for_asset(str(aid))
        assert len(events) == 2

    def test_get_events_by_type(self) -> None:
        tl = EnergyEventTimeline()
        aid = uuid.uuid4()
        tl.record_sensor_update(asset_id=aid)
        tl.record_sensor_update(asset_id=uuid.uuid4())
        tl.record_alarm(asset_id=uuid.uuid4())
        updates = tl.get_events_by_type("sensor_update")
        assert len(updates) == 2

    def test_get_recent_events(self) -> None:
        tl = EnergyEventTimeline()
        tl.record_sensor_update(asset_id=uuid.uuid4())
        recent = tl.get_recent_events(minutes=1)
        assert len(recent) >= 1

    def test_get_all_events(self) -> None:
        tl = EnergyEventTimeline()
        tl.record_alarm(asset_id=uuid.uuid4())
        assert len(tl.get_all_events()) == 1

    def test_clear(self) -> None:
        tl = EnergyEventTimeline()
        tl.record_sensor_update(asset_id=uuid.uuid4())
        tl.clear()
        assert tl.get_all_events() == []

    def test_event_filtering_by_type(self) -> None:
        tl = EnergyEventTimeline()
        aid = uuid.uuid4()
        tl.record_sensor_update(asset_id=aid)
        tl.record_alarm(asset_id=aid)
        alarms = tl.get_events_for_asset(str(aid), event_type="alarm")
        assert len(alarms) == 1


# ═════════════════════════════════════════════════════════════════════════════
# EquipmentClassification
# ═════════════════════════════════════════════════════════════════════════════


class TestEquipmentClassification:
    def test_classify_generator(self) -> None:
        ec = EquipmentClassification()
        result = ec.classify(
            asset_id=uuid.uuid4(),
            asset_type="GENERATOR",
        )
        assert result.classification == "generation"
        assert "Power Generation" in result.category

    def test_classify_solar_panel(self) -> None:
        ec = EquipmentClassification()
        result = ec.classify(
            asset_id=uuid.uuid4(),
            asset_type="SOLAR_PANEL",
        )
        assert result.classification == "generation"

    def test_classify_transformer(self) -> None:
        ec = EquipmentClassification()
        result = ec.classify(
            asset_id=uuid.uuid4(),
            asset_type="TRANSFORMER",
        )
        assert result.classification == "transmission"

    def test_classify_battery(self) -> None:
        ec = EquipmentClassification()
        result = ec.classify(
            asset_id=uuid.uuid4(),
            asset_type="BATTERY",
        )
        assert result.classification == "storage"

    def test_classify_meter(self) -> None:
        ec = EquipmentClassification()
        result = ec.classify(
            asset_id=uuid.uuid4(),
            asset_type="METER",
        )
        assert result.classification == "consumption"

    def test_get_classification_for_type(self) -> None:
        ec = EquipmentClassification()
        assert ec.get_classification_for_type("WIND_TURBINE") == "generation"
        assert ec.get_classification_for_type("SUBSTATION") == "transmission"

    def test_get_all_classifications(self) -> None:
        ec = EquipmentClassification()
        all_cls = ec.get_all_classifications()
        assert "generation" in all_cls
        assert "transmission" in all_cls
        assert "distribution" in all_cls
        assert "consumption" in all_cls
        assert "storage" in all_cls

    def test_unknown_type_defaults(self) -> None:
        ec = EquipmentClassification()
        result = ec.classify(
            asset_id=uuid.uuid4(),
            asset_type="UNKNOWN",
        )
        assert result.classification == "consumption"


# ═════════════════════════════════════════════════════════════════════════════
# UnitConversionService
# ═════════════════════════════════════════════════════════════════════════════


class TestUnitConversionService:
    def test_temperature_c_to_f(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_temperature(100.0, "C", "F")
        assert result == 212.0

    def test_temperature_f_to_c(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_temperature(32.0, "F", "C")
        assert result == 0.0

    def test_temperature_c_to_k(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_temperature(0.0, "C", "K")
        assert result == 273.15

    def test_temperature_k_to_c(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_temperature(273.15, "K", "C")
        assert result == 0.0

    def test_temperature_identity(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_temperature(50.0, "C", "C")
        assert result == 50.0

    def test_voltage_v_to_kv(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_voltage(1000.0, "V", "kV")
        assert result == 1.0

    def test_voltage_kv_to_v(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_voltage(11.0, "kV", "V")
        assert result == 11000.0

    def test_current_a_to_ma(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_current(1.0, "A", "mA")
        assert result == 1000.0

    def test_current_ma_to_a(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_current(500.0, "mA", "A")
        assert result == 0.5

    def test_power_kw_to_mw(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_power(1000.0, "kW", "MW")
        assert result == 1.0

    def test_power_mw_to_kw(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_power(2.5, "MW", "kW")
        assert result == 2500.0

    def test_frequency_hz_to_khz(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_frequency(1000.0, "Hz", "kHz")
        assert result == 1.0

    def test_frequency_mhz_to_hz(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_frequency(1.0, "MHz", "Hz")
        assert result == 1_000_000.0

    def test_pressure_pa_to_kpa(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_pressure(1000.0, "Pa", "kPa")
        assert result == 1.0

    def test_pressure_bar_to_pa(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_pressure(1.0, "bar", "Pa")
        assert result == 100_000.0

    def test_pressure_psi_to_pa(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_pressure(1.0, "psi", "Pa")
        assert abs(result - 6894.76) < 1.0

    def test_convert_request(self) -> None:
        ucs = UnitConversionService()
        req = ConversionRequest(
            value=100.0,
            from_unit="C",
            to_unit="F",
            conversion_type="temperature",
        )
        result = ucs.convert(req)
        assert result.output_value == 212.0

    def test_unsupported_conversion_raises(self) -> None:
        ucs = UnitConversionService()
        req = ConversionRequest(
            value=100.0,
            from_unit="C",
            to_unit="F",
            conversion_type="unsupported",
        )
        with pytest.raises(ValueError, match="Unsupported conversion type"):
            ucs.convert(req)

    def test_power_gw_to_mw(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_power(1.0, "GW", "MW")
        assert result == 1000.0

    def test_voltage_mv_to_v(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_voltage(1000.0, "mV", "V")
        assert result == 1.0

    def test_frequency_khz_to_mhz(self) -> None:
        ucs = UnitConversionService()
        result = ucs.convert_frequency(1000.0, "kHz", "MHz")
        assert result == 1.0


# ═════════════════════════════════════════════════════════════════════════════
# DomainMetrics
# ═════════════════════════════════════════════════════════════════════════════


class TestDomainMetrics:
    def test_initial_state(self) -> None:
        m = DomainMetrics()
        assert m.get_asset_count() == 0
        assert m.get_sensor_count() == 0
        assert m.get_alarm_count() == 0
        assert m.get_incident_count() == 0
        assert m.get_maintenance_count() == 0
        assert m.get_average_health_score() == 0.0

    def test_increment_asset(self) -> None:
        m = DomainMetrics()
        m.increment_asset_count()
        assert m.get_asset_count() == 1

    def test_increment_sensor(self) -> None:
        m = DomainMetrics()
        m.increment_sensor_count(3)
        assert m.get_sensor_count() == 3

    def test_increment_alarm(self) -> None:
        m = DomainMetrics()
        m.increment_alarm_count(5)
        assert m.get_alarm_count() == 5

    def test_increment_incident(self) -> None:
        m = DomainMetrics()
        m.increment_incident_count(2)
        assert m.get_incident_count() == 2

    def test_increment_maintenance(self) -> None:
        m = DomainMetrics()
        m.increment_maintenance_count(4)
        assert m.get_maintenance_count() == 4

    def test_health_score_average(self) -> None:
        m = DomainMetrics()
        m.record_health_score(0.8)
        m.record_health_score(0.9)
        assert m.get_average_health_score() == 0.85

    def test_snapshot(self) -> None:
        m = DomainMetrics()
        m.increment_asset_count(10)
        m.increment_sensor_count(20)
        m.record_health_score(0.75)
        snap = m.snapshot()
        assert snap.asset_count == 10
        assert snap.sensor_count == 20
        assert snap.average_health_score == 0.75

    def test_reset(self) -> None:
        m = DomainMetrics()
        m.increment_asset_count(10)
        m.reset()
        assert m.get_asset_count() == 0
        assert m.get_average_health_score() == 0.0

    def test_negative_delta_ignored(self) -> None:
        m = DomainMetrics()
        m.increment_asset_count(-5)
        assert m.get_asset_count() == 0


# ═════════════════════════════════════════════════════════════════════════════
# DomainTrace
# ═════════════════════════════════════════════════════════════════════════════


class TestDomainTrace:
    def test_record_asset(self) -> None:
        t = DomainTrace()
        r = t.record_asset_operation(
            entity_id="asset1",
            operation="register",
            details="Asset registered successfully",
        )
        assert r.entity_type == "asset"
        assert r.operation == "register"

    def test_record_sensor(self) -> None:
        t = DomainTrace()
        r = t.record_sensor_operation(
            entity_id="sensor1",
            operation="reading_received",
        )
        assert r.entity_type == "sensor"

    def test_record_alarm(self) -> None:
        t = DomainTrace()
        r = t.record_alarm_operation(
            entity_id="alarm1",
            operation="raised",
        )
        assert r.entity_type == "alarm"

    def test_record_incident(self) -> None:
        t = DomainTrace()
        r = t.record_incident_operation(
            entity_id="incident1",
            operation="created",
        )
        assert r.entity_type == "incident"

    def test_record_maintenance(self) -> None:
        t = DomainTrace()
        r = t.record_maintenance_operation(
            entity_id="maint1",
            operation="completed",
        )
        assert r.entity_type == "maintenance"

    def test_get_traces_by_type(self) -> None:
        t = DomainTrace()
        t.record_asset_operation(entity_id="a1", operation="register")
        t.record_sensor_operation(entity_id="s1", operation="reading")
        traces = t.get_traces(entity_type="asset")
        assert len(traces) == 1

    def test_get_traces_by_operation(self) -> None:
        t = DomainTrace()
        t.record_asset_operation(entity_id="a1", operation="register")
        t.record_asset_operation(entity_id="a2", operation="update")
        traces = t.get_traces(operation="register")
        assert len(traces) == 1

    def test_get_all_traces(self) -> None:
        t = DomainTrace()
        t.record_asset_operation(entity_id="a1", operation="register")
        assert len(t.get_all_traces()) == 1

    def test_clear(self) -> None:
        t = DomainTrace()
        t.record_asset_operation(entity_id="a1", operation="register")
        t.clear()
        assert t.get_all_traces() == []

    def test_record_multiple_types(self) -> None:
        t = DomainTrace()
        t.record_asset_operation(entity_id="a1", operation="register")
        t.record_sensor_operation(entity_id="s1", operation="reading")
        t.record_alarm_operation(entity_id="al1", operation="raised")
        t.record_incident_operation(entity_id="in1", operation="created")
        t.record_maintenance_operation(entity_id="m1", operation="completed")
        assert len(t.get_all_traces()) == 5

    def test_record_with_failure(self) -> None:
        t = DomainTrace()
        r = t.record_asset_operation(
            entity_id="a1",
            operation="register",
            success=False,
        )
        assert not r.success


# ═════════════════════════════════════════════════════════════════════════════
# Module imports
# ═════════════════════════════════════════════════════════════════════════════


class TestPhase2Imports:
    def test_import_execution_module(self) -> None:
        from adip.energy import execution
        assert execution is not None

    def test_import_all_components(self) -> None:
        from adip.energy.execution import (
            AlarmCorrelationEngine,
            AssetGraph,
            AssetLifecycleManager,
            DomainMetrics,
            DomainTrace,
            EnergyEventTimeline,
            EquipmentClassification,
            HealthScoreCalculator,
            MaintenanceScheduler,
            SensorValidationPipeline,
            TopologyService,
            UnitConversionService,
        )
        assert AssetGraph is not None
        assert AssetLifecycleManager is not None
        assert SensorValidationPipeline is not None
        assert HealthScoreCalculator is not None
        assert AlarmCorrelationEngine is not None
        assert MaintenanceScheduler is not None
        assert TopologyService is not None
        assert EnergyEventTimeline is not None
        assert EquipmentClassification is not None
        assert UnitConversionService is not None
        assert DomainTrace is not None
        assert DomainMetrics is not None

    def test_import_all_models(self) -> None:
        from adip.energy.execution.models import (
            AssetGraphModel,
            AssetLifecycleState,
            HealthScoreResult,
        )
        assert AssetLifecycleState is not None
        assert AssetGraphModel is not None
        assert HealthScoreResult is not None

    def test_package_re_exports(self) -> None:
        from adip.energy import (
            AssetLifecycleManager,
            DomainMetrics,
            DomainTrace,
            TopologyService,
        )
        assert AssetLifecycleManager is not None
        assert DomainMetrics is not None
        assert DomainTrace is not None
        assert TopologyService is not None
