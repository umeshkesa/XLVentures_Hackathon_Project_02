"""EnergyDomainManager — lightweight facade over the coordinator.

Provides a simplified interface for the EnergyDomainService,
delegating to the EnergyDomainCoordinator for orchestration.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid

import structlog

from adip.energy.contracts.models import (
    Alarm,
    DigitalTwin,
    EnergyAsset,
    EnergyHealth,
    EnergyMetrics,
    Incident,
    MaintenanceRecord,
    Sensor,
    SensorReading,
)
from adip.energy.orchestration.coordinator import EnergyDomainCoordinator
from adip.energy.orchestration.models import EnergyDecision

log = structlog.get_logger(__name__)


class EnergyDomainManager:
    """Lightweight facade over the EnergyDomainCoordinator.

    Delegates energy domain operations to the coordinator and
    provides convenience methods for decision retrieval, health,
    and metrics.
    """

    def __init__(
        self,
        coordinator: EnergyDomainCoordinator | None = None,
    ) -> None:
        self._coordinator = coordinator or EnergyDomainCoordinator()
        self._decisions: dict[str, EnergyDecision] = {}

    def register_asset(
        self,
        asset: EnergyAsset,
        correlation_id: str = "",
    ) -> EnergyAsset:
        """Register a new energy asset.

        Args:
            asset: The asset to register.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The registered EnergyAsset.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.register_asset", asset_id=str(asset.asset_id), cid=cid)
        return self._coordinator.register_asset(asset, correlation_id=cid)

    def get_asset(self, asset_id: str) -> EnergyAsset | None:
        """Retrieve an energy asset by ID.

        Args:
            asset_id: The asset identifier.

        Returns:
            EnergyAsset if found, None otherwise.
        """
        return self._coordinator.get_asset(asset_id)

    def update_asset(
        self,
        asset_id: str,
        asset: EnergyAsset,
        correlation_id: str = "",
    ) -> EnergyAsset | None:
        """Update an existing energy asset.

        Args:
            asset_id: The asset identifier to update.
            asset: The updated asset data.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Updated EnergyAsset if found, None otherwise.
        """
        existing = self._coordinator.get_asset(asset_id)
        if existing is None:
            return None
        self._coordinator.register_asset(asset, correlation_id=correlation_id)
        return asset

    def register_sensor(
        self,
        sensor: Sensor,
        correlation_id: str = "",
    ) -> Sensor:
        """Register a new sensor on an asset.

        Args:
            sensor: The sensor to register.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The registered Sensor.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.register_sensor", sensor_id=str(sensor.sensor_id), cid=cid)
        return self._coordinator.register_sensor(sensor, correlation_id=cid)

    def get_sensor(self, sensor_id: str) -> Sensor | None:
        """Retrieve a sensor by ID.

        Args:
            sensor_id: The sensor identifier.

        Returns:
            Sensor if found, None otherwise.
        """
        return self._coordinator.get_sensor(sensor_id)

    def receive_reading(
        self,
        reading: SensorReading,
        correlation_id: str = "",
    ) -> SensorReading:
        """Receive and record a sensor reading.

        Args:
            reading: The sensor reading to record.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The recorded SensorReading.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.receive_reading", reading_id=str(reading.reading_id), cid=cid)
        return self._coordinator.receive_reading(reading, correlation_id=cid)

    def create_digital_twin(
        self,
        twin: DigitalTwin,
        correlation_id: str = "",
    ) -> DigitalTwin:
        """Create a digital twin for an asset.

        Args:
            twin: The digital twin to create.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created DigitalTwin.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.create_digital_twin", twin_id=str(twin.twin_id), cid=cid)
        return self._coordinator.create_digital_twin(twin, correlation_id=cid)

    def get_digital_twin(self, twin_id: str) -> DigitalTwin | None:
        """Retrieve a digital twin by ID.

        Args:
            twin_id: The digital twin identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        return self._coordinator.get_digital_twin(twin_id)

    def raise_alarm(
        self,
        alarm: Alarm,
        correlation_id: str = "",
    ) -> Alarm:
        """Raise a new alarm for an asset.

        Args:
            alarm: The alarm to raise.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The raised Alarm.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.raise_alarm", alarm_id=str(alarm.alarm_id), cid=cid)
        return self._coordinator.raise_alarm(alarm, correlation_id=cid)

    def get_alarm(self, alarm_id: str) -> Alarm | None:
        """Retrieve an alarm by ID.

        Args:
            alarm_id: The alarm identifier.

        Returns:
            Alarm if found, None otherwise.
        """
        return self._coordinator.get_alarm(alarm_id)

    def create_incident(
        self,
        incident: Incident,
        correlation_id: str = "",
    ) -> Incident:
        """Create a new incident.

        Args:
            incident: The incident to create.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created Incident.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.create_incident", incident_id=str(incident.incident_id), cid=cid)
        return self._coordinator.create_incident(incident, correlation_id=cid)

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
        log.info("manager.record_maintenance", record_id=str(record.record_id), cid=cid)
        return self._coordinator.record_maintenance(record, correlation_id=cid)

    def get_asset_health(self, asset_id: str) -> AssetHealth | None:
        """Get health status for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            AssetHealth if found, None otherwise.
        """
        return self._coordinator.get_asset_health(asset_id)

    def get_decision(self, decision_id: str) -> EnergyDecision | None:
        """Retrieve a decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            EnergyDecision if found, None otherwise.
        """
        return self._coordinator.get_decision(decision_id)

    def get_health(self) -> EnergyHealth:
        """Get the health status of the Energy Domain.

        Returns:
            EnergyHealth with current component statuses.
        """
        return self._coordinator.health()

    def get_metrics(self) -> EnergyMetrics:
        """Get aggregated metrics for the Energy Domain.

        Returns:
            EnergyMetrics with current metric values.
        """
        return self._coordinator.metrics()
