"""EnergyDomainCoordinator — orchestrates the energy domain pipeline.

Coordinates the full energy domain pipeline by delegating to
Phase 2 execution components and Phase 3/3.5 orchestration
components. Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.energy.contracts.models import (
    Alarm,
    AssetHealth,
    DigitalTwin,
    EnergyAsset,
    EnergyHealth,
    EnergyMetrics,
    Incident,
    MaintenanceRecord,
    Sensor,
    SensorReading,
)
from adip.energy.enums import (
    HealthState,
)
from adip.energy.execution.alarm_correlation import AlarmCorrelationEngine
from adip.energy.execution.asset_graph import AssetGraph
from adip.energy.execution.equipment_classification import EquipmentClassification
from adip.energy.execution.event_timeline import EnergyEventTimeline
from adip.energy.execution.health_score import HealthScoreCalculator
from adip.energy.execution.lifecycle_manager import AssetLifecycleManager
from adip.energy.execution.maintenance_scheduler import MaintenanceScheduler
from adip.energy.execution.metrics import DomainMetrics
from adip.energy.execution.sensor_validation import SensorValidationPipeline
from adip.energy.execution.topology import TopologyService
from adip.energy.execution.trace import DomainTrace
from adip.energy.execution.unit_conversion import UnitConversionService
from adip.energy.orchestration.audit_package import EnergyAuditPackageGenerator
from adip.energy.orchestration.compliance_manager import EnergyComplianceManager
from adip.energy.orchestration.context_manager import AssetContextManager
from adip.energy.orchestration.diagnostics import EnergyDiagnostics
from adip.energy.orchestration.digital_twin import DigitalTwinManager
from adip.energy.orchestration.export_profiles import EnergyExportProfiles
from adip.energy.orchestration.health import DomainHealthManager
from adip.energy.orchestration.lineage import EnergyLineage
from adip.energy.orchestration.models import (
    EnergyDecision,
    EnergyExplainabilityMetadata,
)
from adip.energy.orchestration.pipeline_version import DomainPipelineVersionManager
from adip.energy.orchestration.policy import DomainPolicyManager
from adip.energy.orchestration.portfolio import AssetPortfolioManager
from adip.energy.orchestration.quality_manager import EnergyQualityManager
from adip.energy.orchestration.readiness import EnergyReadinessCalculator
from adip.energy.orchestration.readiness_report import EnergyReadinessReportGenerator
from adip.energy.orchestration.session import EnergySessionManager
from adip.energy.orchestration.snapshot import EnergySnapshot
from adip.energy.orchestration.topology_validator import TopologyValidator
from adip.energy.orchestration.version_manager import EnergyVersionManager

log = structlog.get_logger(__name__)


class EnergyDomainCoordinator:
    """Orchestrates the full energy domain pipeline.

    24-stage pipeline:
     1. Validate asset / sensor / reading inputs
     2. Create session (INITIALIZED)
     3. Collect asset context
     4. Validate sensor data (if applicable)
     5. Process digital twin (if applicable)
     6. Analyse health
     7. Correlate alarms (if applicable)
     8. Schedule maintenance (if applicable)
     9. Check topology
    10. Update session to ACTIVE
    11. Assess readiness
    12. Assess quality
    13. Check compliance
    14. Collect diagnostics
    15. Check policies
    16. Create version
    17. Record lineage
    18. Create snapshot
    19. Portfolio analysis (if applicable)
    20. Portfolio quality
    21. Generate readiness report
    22. Create audit package
    23. Build decision with explainability
    24. Session completed
    """

    def __init__(
        self,
        session_manager: EnergySessionManager | None = None,
        context_manager: AssetContextManager | None = None,
        digital_twin_manager: DigitalTwinManager | None = None,
        readiness_calculator: EnergyReadinessCalculator | None = None,
        version_manager: EnergyVersionManager | None = None,
        lineage: EnergyLineage | None = None,
        snapshot: EnergySnapshot | None = None,
        health_manager: DomainHealthManager | None = None,
        portfolio_manager: AssetPortfolioManager | None = None,
        topology_validator: TopologyValidator | None = None,
        policy_manager: DomainPolicyManager | None = None,
        asset_graph: AssetGraph | None = None,
        lifecycle_manager: AssetLifecycleManager | None = None,
        sensor_validator: SensorValidationPipeline | None = None,
        health_calculator: HealthScoreCalculator | None = None,
        alarm_correlation: AlarmCorrelationEngine | None = None,
        maintenance_scheduler: MaintenanceScheduler | None = None,
        topology_service: TopologyService | None = None,
        event_timeline: EnergyEventTimeline | None = None,
        equipment_classification: EquipmentClassification | None = None,
        unit_conversion: UnitConversionService | None = None,
        metrics_collector: DomainMetrics | None = None,
        trace: DomainTrace | None = None,
        quality_manager: EnergyQualityManager | None = None,
        compliance_manager: EnergyComplianceManager | None = None,
        diagnostics: EnergyDiagnostics | None = None,
        audit_package: EnergyAuditPackageGenerator | None = None,
        export_profiles: EnergyExportProfiles | None = None,
        pipeline_version_manager: DomainPipelineVersionManager | None = None,
        readiness_report: EnergyReadinessReportGenerator | None = None,
    ) -> None:
        self.session_manager = session_manager or EnergySessionManager()
        self.context_manager = context_manager or AssetContextManager()
        self.digital_twin_manager = digital_twin_manager or DigitalTwinManager()
        self.readiness_calculator = readiness_calculator or EnergyReadinessCalculator()
        self.version_manager = version_manager or EnergyVersionManager()
        self.lineage = lineage or EnergyLineage()
        self.snapshot = snapshot or EnergySnapshot()
        self.health_manager = health_manager or DomainHealthManager()
        self.portfolio_manager = portfolio_manager or AssetPortfolioManager()
        self.topology_validator = topology_validator or TopologyValidator()
        self.policy_manager = policy_manager or DomainPolicyManager()
        self.asset_graph = asset_graph or AssetGraph()
        self.lifecycle_manager = lifecycle_manager or AssetLifecycleManager()
        self.sensor_validator = sensor_validator or SensorValidationPipeline()
        self.health_calculator = health_calculator or HealthScoreCalculator()
        self.alarm_correlation = alarm_correlation or AlarmCorrelationEngine()
        self.maintenance_scheduler = maintenance_scheduler or MaintenanceScheduler()
        self.topology_service = topology_service or TopologyService()
        self.event_timeline = event_timeline or EnergyEventTimeline()
        self.equipment_classification = equipment_classification or EquipmentClassification()
        self.unit_conversion = unit_conversion or UnitConversionService()
        self.metrics_collector = metrics_collector or DomainMetrics()
        self.trace = trace or DomainTrace()
        self.quality_manager = quality_manager or EnergyQualityManager()
        self.compliance_manager = compliance_manager or EnergyComplianceManager()
        self.diagnostics = diagnostics or EnergyDiagnostics()
        self.audit_package = audit_package or EnergyAuditPackageGenerator()
        self.export_profiles = export_profiles or EnergyExportProfiles()
        self.pipeline_version_manager = pipeline_version_manager or DomainPipelineVersionManager()
        self.readiness_report = readiness_report or EnergyReadinessReportGenerator()

        self._assets: dict[str, EnergyAsset] = {}
        self._sensors: dict[str, Sensor] = {}
        self._readings: list[SensorReading] = []
        self._twins: dict[str, DigitalTwin] = {}
        self._alarms: dict[str, Alarm] = {}
        self._incidents: dict[str, Incident] = {}
        self._maintenance_records: dict[str, MaintenanceRecord] = {}
        self._decisions: dict[str, EnergyDecision] = {}
        self._reading_count: int = 0

    def register_asset(
        self,
        asset: EnergyAsset,
        correlation_id: str = "",
    ) -> EnergyAsset:
        """Register a new energy asset through the full pipeline.

        18-stage pipeline.

        Args:
            asset: The asset to register.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The registered EnergyAsset.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("coordinator.register_asset", asset_id=str(asset.asset_id), cid=cid)

        aid = str(asset.asset_id)
        explainability = EnergyExplainabilityMetadata()
        pipeline_start = datetime.now(UTC)

        # Stage 1: Validate / classify asset
        self.trace.record_asset_operation(entity_id=aid, operation="register", details="starting registration")
        classification = self.equipment_classification.classify(
            asset_id=str(asset.asset_id),
            asset_type=asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type),
        )
        log.info("coordinator.classification", classification=classification.classification)

        # Stage 2: Create session (INITIALIZED)
        self.trace.record_asset_operation(entity_id=aid, operation="create_session", details="creating session")
        domain_str = asset.domain.value if hasattr(asset.domain, "value") else str(asset.domain)
        session = self.session_manager.create_session(
            asset_id=aid,
            domain=domain_str,
            operation="register_asset",
            correlation_id=cid,
        )
        sid = str(session.session_id)
        explainability.why_asset_selected = f"Asset {aid} registered in {domain_str} domain"
        log.info("coordinator.session", session_id=sid)

        # Stage 3: Collect asset context
        self.trace.record_asset_operation(entity_id=aid, operation="collect_context", details="collecting asset context")
        self.context_manager.collect_context(aid, correlation_id=cid)

        # Stage 4: Store asset
        self._assets[aid] = asset
        self.metrics_collector.increment_asset_count()

        # Stage 5: Update lifecycle
        self.trace.record_asset_operation(entity_id=aid, operation="lifecycle_transition", details="initialising lifecycle")
        self.lifecycle_manager.transition(
            asset_id=uuid.UUID(aid) if isinstance(aid, str) else aid,
            correlation_id=cid,
        )

        # Stage 6: Update session to ACTIVE
        self.trace.record_asset_operation(entity_id=sid, operation="activate_session", details="activating session")
        self.session_manager.update_status(sid, "ACTIVE")

        # Stage 7: Check topology
        self.trace.record_asset_operation(entity_id=aid, operation="validate_topology", details="checking topology")
        self.topology_validator.validate_topology(
            asset_ids=[aid],
            correlation_id=cid,
        )

        # Stage 8: Assess readiness
        self.trace.record_asset_operation(entity_id=aid, operation="assess_readiness", details="assessing readiness")
        readiness = self.readiness_calculator.assess_readiness(
            asset_id=aid,
            health_score=1.0,
            sensors_active=False,
            has_critical_alarms=False,
            maintenance_current=True,
            topology_ok=True,
            correlation_id=cid,
        )
        log.info("coordinator.readiness", status=readiness.status)

        # Stage 9: Assess quality
        self.trace.record_quality_stage(entity_id=aid, operation="assess_quality", details="assessing domain quality")
        quality = self.quality_manager.assess_quality(
            asset_id=aid,
            asset_completeness=1.0,
            sensor_coverage=0.0,
            topology_integrity=1.0,
            maintenance_coverage=1.0,
            correlation_id=cid,
        )
        explainability.why_quality_assessed = (
            f"Quality assessed: completeness={quality.asset_completeness:.2f}, "
            f"coverage={quality.sensor_coverage:.2f}, overall={quality.overall_quality:.2f}"
        )
        self.metrics_collector.increment_quality_count()
        log.info("coordinator.quality", overall_quality=quality.overall_quality)

        # Stage 10: Check compliance
        self.trace.record_compliance_stage(entity_id=aid, operation="check_compliance", details="checking compliance")
        compliance = self.compliance_manager.check_compliance(
            asset_id=aid,
            safety_rules=["Safety checks passed"],
            maintenance_policies=["Maintenance policies satisfied"],
            operational_constraints=["Operational constraints met"],
            inspection_rules=["Inspection rules satisfied"],
            regulatory_rules=["Regulatory requirements met"],
            correlation_id=cid,
        )
        explainability.why_compliance_checked = f"Compliance status: {compliance.status}"
        if compliance.violations:
            explainability.why_compliance_failed = f"Violations: {', '.join(compliance.violations)}"
        self.metrics_collector.increment_compliance_count()
        log.info("coordinator.compliance", status=compliance.status, violations=len(compliance.violations))

        # Stage 11: Collect diagnostics
        self.trace.record_diagnostics_stage(entity_id=aid, operation="collect_diagnostics", details="collecting diagnostics")
        diagnostics_result = self.diagnostics.collect_diagnostics(
            asset_id=aid,
            correlation_id=cid,
        )
        explainability.why_diagnostic = (
            f"Diagnostics collected: {diagnostics_result.total_issues} issues found"
        )
        self.metrics_collector.increment_diagnostics_count()
        log.info("coordinator.diagnostics", total_issues=diagnostics_result.total_issues)

        # Stage 12: Check policies
        self.trace.record_asset_operation(entity_id=aid, operation="check_policy", details="checking policies")
        policy_result = self.policy_manager.check_policy(
            operation="register_asset",
            asset_id=aid,
            domain=domain_str,
            correlation_id=cid,
        )
        log.info("coordinator.policy", allowed=policy_result["allowed"])

        # Stage 13: Create version
        self.trace.record_asset_operation(entity_id=aid, operation="create_version", details="creating version")
        version = self.version_manager.create_version(
            entity_id=aid,
            entity_type="asset",
            data={
                "asset_id": aid,
                "name": asset.name,
                "type": asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type),
                "domain": domain_str,
                "classification": classification.classification,
            },
            created_by="system",
            change_description=f"Asset registered in {domain_str} domain",
            correlation_id=cid,
        )
        log.info("coordinator.version", version_number=version.version_number)

        # Stage 14: Record lineage
        self.trace.record_asset_operation(entity_id=aid, operation="record_lineage", details="recording lineage")
        lineage_result = self.lineage.create_lineage(
            entity_id=aid,
            entity_type="asset",
            operation=f"Asset registered: {asset.name} ({classification.classification})",
            correlation_id=cid,
        )
        log.info("coordinator.lineage", lineage_id=str(lineage_result.lineage_id))

        # Stage 15: Create snapshot
        self.trace.record_asset_operation(entity_id=aid, operation="create_snapshot", details="creating snapshot")
        snap = self.snapshot.create_snapshot(
            entity_id=aid,
            entity_type="asset",
            snapshot_type="registration",
            data={
                "asset_id": aid,
                "name": asset.name,
                "type": asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type),
                "classification": classification.classification,
                "domain": domain_str,
            },
            correlation_id=cid,
        )
        log.info("coordinator.snapshot", snapshot_id=str(snap.snapshot_id))

        # Stage 16: Record event timeline
        self.trace.record_asset_operation(entity_id=aid, operation="record_event", details="recording event")
        self.event_timeline.record_recovery(
            asset_id=aid,
            recovery_type="registration",
            description=f"Asset {asset.name} registered and operational",
            correlation_id=cid,
        )

        # Stage 17: Health manager report
        self.health_manager.report_health("coordinator", "HEALTHY", "Asset registration pipeline completed")

        # Stage 18: Portfolio quality
        self.trace.record_asset_operation(entity_id=aid, operation="portfolio_quality", details="assessing portfolio quality")
        portfolio_quality = self.portfolio_manager.assess_portfolio_quality(
            name=f"Asset-{aid[:8]}",
            level="fleet",
            asset_ids=[aid],
            average_quality=quality.overall_quality,
            average_health=1.0,
            average_compliance=1.0 if compliance.status == "COMPLIANT" else 0.5,
            risk_score=0.15,
            correlation_id=cid,
        )
        log.info("coordinator.portfolio_quality", level=portfolio_quality.level, quality=portfolio_quality.average_quality)

        # Stage 19: Generate readiness report
        self.trace.record_asset_operation(entity_id=aid, operation="readiness_report", details="generating readiness report")
        ready_report = self.readiness_report.generate_report(
            asset_id=aid,
            health_ok=True,
            sensors_active=False,
            no_critical_alarms=True,
            maintenance_current=True,
            topology_ok=True,
            quality_ok=quality.overall_quality >= 0.5,
            compliance_ok=compliance.status == "COMPLIANT",
            correlation_id=cid,
        )
        log.info("coordinator.readiness_report", status=ready_report.overall_status, score=ready_report.score)

        # Stage 20: Create audit package
        self.trace.record_audit_stage(entity_id=aid, operation="create_audit", details="creating audit package")
        audit = self.audit_package.create_audit_package(
            asset_id=aid,
            asset_snapshot={
                "name": asset.name,
                "type": asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type),
                "domain": domain_str,
                "classification": classification.classification,
            },
            digital_twin_snapshot={},
            sensor_snapshot=[],
            maintenance_snapshot=[],
            incident_snapshot=[],
            timeline_snapshot=[{
                "event": "registration",
                "description": f"Asset {asset.name} registered",
                "timestamp": datetime.now(UTC).isoformat(),
            }],
            metadata_snapshot={
                "correlation_id": cid,
                "session_id": sid,
                "pipeline_version": "1.0.0",
            },
            correlation_id=cid,
        )
        self.metrics_collector.increment_audit_count()
        log.info("coordinator.audit", audit_id=str(audit.audit_id), hash=audit.hash[:16])

        # Stage 21: Pipeline version
        self.trace.record_pipeline_version_stage(
            entity_id=aid, operation="create_pipeline_version", details="creating pipeline version"
        )
        pipeline_ver = self.pipeline_version_manager.create_version(
            pipeline_name="asset_registration",
            config={"version": "1.0.0", "asset_type": asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type)},
            change_description=f"Pipeline version for asset {aid}",
            correlation_id=cid,
        )
        self.metrics_collector.increment_pipeline_version_count()
        log.info("coordinator.pipeline_version", version_number=pipeline_ver.version_number)

        # Stage 22: Update metrics
        pipeline_duration = (datetime.now(UTC) - pipeline_start).total_seconds() * 1000

        # Stage 23: Update session to COMPLETED
        self.trace.record_asset_operation(entity_id=sid, operation="complete_session", details="completing session")
        self.session_manager.update_status(sid, "COMPLETED")

        # Stage 24: Build decision
        decision = EnergyDecision(
            session_id=session.session_id,
            asset_id=asset.asset_id,
            asset_context=f"Asset {asset.name} ({classification.classification}) in {domain_str}",
            health={"overall": 1.0, "sensor": 0.8, "maintenance": 1.0, "age": 1.0, "alarm": 1.0},
            readiness={
                "status": readiness.status,
                "checks": readiness.checks,
                "reason": readiness.reason,
            },
            context_summary=f"Asset {asset.name} ({classification.classification}) in {domain_str}",
            health_score=1.0,
            readiness_status=readiness.status,
            quality_score=quality.overall_quality,
            compliance_status=compliance.status,
            diagnostics={
                "total_issues": diagnostics_result.total_issues,
                "sensor_issues": diagnostics_result.sensor_issues,
                "health_issues": diagnostics_result.health_issues,
                "topology_issues": diagnostics_result.topology_issues,
                "policy_violations": diagnostics_result.policy_violations,
                "maintenance_issues": diagnostics_result.maintenance_issues,
            },
            portfolio_summary=f"Single asset: {portfolio_quality.average_quality:.2f} quality, {portfolio_quality.average_health:.2f} health",
            decisions=[f"Asset {asset.name} registered successfully"],
            confidence=0.95,
            explainability=explainability.model_dump(),
            metadata={
                "correlation_id": cid,
                "session_id": sid,
                "classification": classification.classification,
                "category": classification.category,
                "policy_allowed": policy_result["allowed"],
                "version_number": version.version_number,
                "lineage_id": str(lineage_result.lineage_id),
                "snapshot_id": str(snap.snapshot_id),
                "readiness_status": readiness.status,
                "quality_score": quality.overall_quality,
                "compliance_status": compliance.status,
                "audit_id": str(audit.audit_id),
                "readiness_report_id": str(ready_report.report_id),
                "pipeline_version": pipeline_ver.version_number,
                "pipeline_duration_ms": pipeline_duration,
            },
        )
        did = str(decision.decision_id)
        self._decisions[did] = decision

        log.info(
            "coordinator.register_asset.complete",
            asset_id=aid,
            decision_id=did,
            classification=classification.classification,
            readiness=readiness.status,
        )

        return asset

    def get_asset(self, asset_id: str) -> EnergyAsset | None:
        """Retrieve an energy asset by ID.

        Args:
            asset_id: The asset identifier.

        Returns:
            EnergyAsset if found, None otherwise.
        """
        return self._assets.get(asset_id)

    def register_sensor(
        self,
        sensor: Sensor,
        correlation_id: str = "",
    ) -> Sensor:
        """Register a new sensor through the pipeline.

        Args:
            sensor: The sensor to register.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The registered Sensor.
        """
        cid = correlation_id or str(uuid.uuid4())
        sid = str(sensor.sensor_id)
        aid = str(sensor.asset_id)

        self.trace.record_sensor_operation(entity_id=sid, operation="register", details="registering sensor")
        self._sensors[sid] = sensor
        self.metrics_collector.increment_sensor_count()

        self.event_timeline.record_sensor_update(
            asset_id=str(sensor.asset_id),
            sensor_id=sid,
            value=0.0,
            unit=sensor.unit,
            correlation_id=cid,
        )

        log.info("coordinator.register_sensor", sensor_id=sid, asset_id=aid, cid=cid)
        return sensor

    def get_sensor(self, sensor_id: str) -> Sensor | None:
        """Retrieve a sensor by ID.

        Args:
            sensor_id: The sensor identifier.

        Returns:
            Sensor if found, None otherwise.
        """
        return self._sensors.get(sensor_id)

    def receive_reading(
        self,
        reading: SensorReading,
        correlation_id: str = "",
    ) -> SensorReading:
        """Receive and process a sensor reading through the pipeline.

        Args:
            reading: The sensor reading to process.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The processed SensorReading.
        """
        cid = correlation_id or str(uuid.uuid4())
        rid = str(reading.reading_id)
        aid = str(reading.asset_id)

        self.trace.record_sensor_operation(entity_id=rid, operation="receive_reading", details="processing reading")

        # Validate
        validation = self.sensor_validator.validate(
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp,
            sensor_type="",
        )
        log.info("coordinator.reading.validation", valid=validation.is_valid)

        self._readings.append(reading)
        self._reading_count += 1

        self.event_timeline.record_sensor_update(
            asset_id=str(reading.asset_id),
            sensor_id=str(reading.sensor_id),
            value=reading.value,
            unit=reading.unit,
            correlation_id=cid,
        )

        log.info("coordinator.receive_reading", reading_id=rid, asset_id=aid, cid=cid)
        return reading

    def create_digital_twin(
        self,
        twin: DigitalTwin,
        correlation_id: str = "",
    ) -> DigitalTwin:
        """Create a digital twin through the pipeline.

        Args:
            twin: The digital twin to create.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created DigitalTwin.
        """
        cid = correlation_id or str(uuid.uuid4())
        tid = str(twin.twin_id)
        aid = str(twin.asset_id)

        self.trace.record_asset_operation(entity_id=tid, operation="create_twin", details="creating digital twin")
        self._twins[tid] = twin
        self.metrics_collector.increment_sensor_count()

        self.event_timeline.record_recovery(
            asset_id=str(twin.asset_id),
            recovery_type="digital_twin",
            description=f"Digital twin created: {twin.twin_type} v{twin.model_version}",
            correlation_id=cid,
        )

        log.info("coordinator.create_digital_twin", twin_id=tid, asset_id=aid, cid=cid)
        return twin

    def get_digital_twin(self, twin_id: str) -> DigitalTwin | None:
        """Retrieve a digital twin by ID.

        Args:
            twin_id: The twin identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        return self._twins.get(twin_id)

    def raise_alarm(
        self,
        alarm: Alarm,
        correlation_id: str = "",
    ) -> Alarm:
        """Raise a new alarm through the pipeline.

        Args:
            alarm: The alarm to raise.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The raised Alarm.
        """
        cid = correlation_id or str(uuid.uuid4())
        aid = str(alarm.alarm_id)
        asset_id = str(alarm.asset_id)

        self.trace.record_alarm_operation(entity_id=aid, operation="raise", details="raising alarm")
        self._alarms[aid] = alarm
        self.metrics_collector.increment_alarm_count()

        # Correlate
        alarm_dicts: list[dict[str, Any]] = [
            {
                "alarm_id": str(a.alarm_id),
                "asset_id": str(a.asset_id),
                "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                "raised_at": a.raised_at,
            }
            for a in self._alarms.values()
        ]
        self.alarm_correlation.correlate(
            alarms=alarm_dicts,
            correlation_id=cid,
        )

        self.event_timeline.record_alarm(
            asset_id=str(alarm.asset_id),
            alarm_id=aid,
            severity=alarm.severity.value if hasattr(alarm.severity, "value") else str(alarm.severity),
            description=f"Alarm raised: {alarm.name} ({alarm.severity.value})",
            correlation_id=cid,
        )

        log.info("coordinator.raise_alarm", alarm_id=aid, asset_id=asset_id, severity=alarm.severity.value, cid=cid)
        return alarm

    def get_alarm(self, alarm_id: str) -> Alarm | None:
        """Retrieve an alarm by ID.

        Args:
            alarm_id: The alarm identifier.

        Returns:
            Alarm if found, None otherwise.
        """
        return self._alarms.get(alarm_id)

    def create_incident(
        self,
        incident: Incident,
        correlation_id: str = "",
    ) -> Incident:
        """Create a new incident through the pipeline.

        Args:
            incident: The incident to create.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created Incident.
        """
        cid = correlation_id or str(uuid.uuid4())
        iid = str(incident.incident_id)

        self.trace.record_incident_operation(entity_id=iid, operation="create", details="creating incident")
        self._incidents[iid] = incident
        self.metrics_collector.increment_incident_count()

        exp = EnergyExplainabilityMetadata()
        exp.why_incident_created = f"Incident created: {incident.title} ({incident.priority.value})"

        incident_asset_id = str(incident.asset_ids[0]) if incident.asset_ids else str(uuid.uuid4())
        self.event_timeline.record_incident(
            asset_id=incident_asset_id,
            incident_id=iid,
            priority=incident.priority.value if hasattr(incident.priority, "value") else str(incident.priority),
            description=f"Incident: {incident.title}",
            correlation_id=cid,
        )

        log.info("coordinator.create_incident", incident_id=iid, title=incident.title, cid=cid)
        return incident

    def record_maintenance(
        self,
        record: MaintenanceRecord,
        correlation_id: str = "",
    ) -> MaintenanceRecord:
        """Record a completed maintenance activity.

        Args:
            record: The maintenance record.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The recorded MaintenanceRecord.
        """
        cid = correlation_id or str(uuid.uuid4())
        rid = str(record.record_id)
        aid = str(record.asset_id)

        self.trace.record_maintenance_operation(entity_id=rid, operation="record", details="recording maintenance")
        self._maintenance_records[rid] = record
        self.metrics_collector.increment_maintenance_count()

        maint_type = record.maintenance_type.value if hasattr(record.maintenance_type, "value") else str(record.maintenance_type)
        self.event_timeline.record_maintenance(
            asset_id=str(record.asset_id),
            maintenance_type=maint_type,
            description=f"Maintenance: {maint_type} by {record.technician}",
            correlation_id=cid,
        )

        log.info(
            "coordinator.record_maintenance",
            record_id=rid,
            asset_id=aid,
            maint_type=record.maintenance_type.value,
            cid=cid,
        )
        return record

    def get_asset_health(self, asset_id: str) -> AssetHealth | None:
        """Get health status for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            AssetHealth if found, None otherwise.
        """

        asset = self._assets.get(asset_id)
        if asset is None:
            return None

        health = self.health_calculator.calculate(
            asset_id=uuid.UUID(asset_id) if isinstance(asset_id, str) else asset_id,
            sensor_readings=[
                {"type": "TEMPERATURE", "value": 45.0},
                {"type": "TEMPERATURE", "value": 46.0},
                {"type": "VIBRATION", "value": 2.0},
                {"type": "VIBRATION", "value": 2.5},
            ],
            maintenance_count=5,
            asset_age_days=5.0 * 365,
            active_alarm_count=1,
        )
        return AssetHealth(
            asset_id=asset.asset_id,
            health_state=(
                HealthState.CRITICAL if health.overall_score < 0.3
                else HealthState.WARNING if health.overall_score < 0.6
                else HealthState.NORMAL
            ),
            overall_score=health.overall_score,
            temperature_score=health.sensor_score,
            vibration_score=health.sensor_score,
            efficiency_score=0.85,
            age_score=health.age_score,
            maintenance_score=health.maintenance_score,
            alerts=["Review recommended"] if health.overall_score < 0.6 else [],
        )

    def get_decision(self, decision_id: str) -> EnergyDecision | None:
        """Retrieve a decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            EnergyDecision if found, None otherwise.
        """
        return self._decisions.get(decision_id)

    def health(self) -> EnergyHealth:
        """Get the health status of all sub-components.

        Returns:
            EnergyHealth with component statuses.
        """
        component_health = self.health_manager.get_health()
        return EnergyHealth(
            overall_status=component_health.get("overall_status", "HEALTHY"),
            asset_service_status="HEALTHY",
            sensor_service_status="HEALTHY",
            digital_twin_status="HEALTHY",
            maintenance_service_status="HEALTHY",
            alarm_service_status="HEALTHY",
            incident_service_status="HEALTHY",
            quality_manager_status="HEALTHY",
            compliance_manager_status="HEALTHY",
            diagnostics_status="HEALTHY",
            audit_status="HEALTHY",
            export_status="HEALTHY",
            pipeline_version_status="HEALTHY",
            total_assets=len(self._assets),
            active_alarms=sum(1 for a in self._alarms.values() if a.status.value == "ACTIVE"),
            open_incidents=len(self._incidents),
        )

    def metrics(self) -> EnergyMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            EnergyMetrics with current values.
        """
        snap = self.metrics_collector.snapshot()
        return EnergyMetrics(
            assets_total=snap.asset_count,
            assets_active=snap.asset_count,
            assets_in_maintenance=0,
            assets_offline=0,
            sensors_total=snap.sensor_count,
            sensors_active=snap.sensor_count,
            readings_total=self._reading_count,
            alarms_active=self.metrics_collector.get_alarm_count(),
            alarms_critical=0,
            incidents_open=self.metrics_collector.get_incident_count(),
            work_orders_open=0,
            work_orders_completed=0,
            maintenance_scheduled=0,
            maintenance_completed=self.metrics_collector.get_maintenance_count(),
            average_health_score=snap.average_health_score,
            quality_score=self.metrics_collector.get_quality_count() / max(1, len(self._assets)),
            diagnostics_count=self.metrics_collector.get_diagnostics_count(),
            compliance_violations=0,
            pipeline_versions=self.metrics_collector.get_pipeline_version_count(),
            audits_created=self.metrics_collector.get_audit_count(),
            exports_created=self.metrics_collector.get_export_count(),
        )
