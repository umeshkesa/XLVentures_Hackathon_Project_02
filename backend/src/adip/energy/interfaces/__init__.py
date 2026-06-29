"""Abstract interfaces for the Energy Domain Package.

Defines all abstract interfaces for energy domain operations
following the Dependency Inversion Principle.

FROZEN — All interfaces are frozen after Phase 3.5.
Do not modify without RFC process.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from adip.energy.contracts.models import (
    Alarm,
    AssetHealth,
    AssetHierarchy,
    AssetRelationship,
    DigitalTwin,
    EnergyAsset,
    EnergyContext,
    EnergyHealth,
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


class EnergyDomainService(ABC):
    """Service-layer interface for the Energy Domain Package.

    This is the ONLY public API for external consumers.
    All energy domain operations MUST go through this interface.
    """

    @abstractmethod
    def register_asset(
        self,
        asset_dto: EnergyAssetDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> EnergyAsset | None:
        """Register a new energy asset.

        Args:
            asset_dto: The asset data transfer object.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            EnergyAsset if authorised, None otherwise.
        """
        ...

    @abstractmethod
    def get_asset(
        self,
        asset_id: str,
        correlation_id: str = "",
    ) -> EnergyAsset | None:
        """Retrieve an energy asset by ID.

        Args:
            asset_id: The asset identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            EnergyAsset if found, None otherwise.
        """
        ...

    @abstractmethod
    def update_asset(
        self,
        asset_id: str,
        asset_dto: EnergyAssetDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> EnergyAsset | None:
        """Update an existing energy asset.

        Args:
            asset_id: The asset identifier to update.
            asset_dto: The updated asset data.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Updated EnergyAsset if found, None otherwise.
        """
        ...

    @abstractmethod
    def register_sensor(
        self,
        sensor_dto: SensorDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Sensor | None:
        """Register a new sensor on an asset.

        Args:
            sensor_dto: The sensor data transfer object.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Sensor if authorised, None otherwise.
        """
        ...

    @abstractmethod
    def get_sensor(
        self,
        sensor_id: str,
        correlation_id: str = "",
    ) -> Sensor | None:
        """Retrieve a sensor by ID.

        Args:
            sensor_id: The sensor identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Sensor if found, None otherwise.
        """
        ...

    @abstractmethod
    def receive_reading(
        self,
        sensor_id: str,
        value: float,
        unit: str = "",
        quality: str = "good",
        correlation_id: str = "",
    ) -> SensorReading | None:
        """Receive and record a sensor reading.

        Args:
            sensor_id: The sensor identifier.
            value: The measured value.
            unit: Unit of measurement.
            quality: Quality of the reading.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            SensorReading if recorded, None otherwise.
        """
        ...

    @abstractmethod
    def create_digital_twin(
        self,
        twin_dto: DigitalTwinDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> DigitalTwin | None:
        """Create a digital twin for an asset.

        Args:
            twin_dto: The digital twin data transfer object.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            DigitalTwin if created, None otherwise.
        """
        ...

    @abstractmethod
    def raise_alarm(
        self,
        alarm_dto: AlarmDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Alarm | None:
        """Raise a new alarm for an asset.

        Args:
            alarm_dto: The alarm data transfer object.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Alarm if raised, None otherwise.
        """
        ...

    @abstractmethod
    def create_incident(
        self,
        incident_dto: IncidentDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Incident | None:
        """Create a new incident.

        Args:
            incident_dto: The incident data transfer object.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Incident if created, None otherwise.
        """
        ...

    @abstractmethod
    def record_maintenance(
        self,
        asset_id: str,
        maintenance_type: str,
        technician: str = "",
        description: str = "",
        duration_hours: float = 0.0,
        user_id: str = "",
        correlation_id: str = "",
    ) -> MaintenanceRecord | None:
        """Record a completed maintenance activity.

        Args:
            asset_id: The asset identifier.
            maintenance_type: Type of maintenance performed.
            technician: Technician who performed the work.
            description: Description of maintenance performed.
            duration_hours: Duration in hours.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            MaintenanceRecord if recorded, None otherwise.
        """
        ...

    @abstractmethod
    def get_asset_health(
        self,
        asset_id: str,
        correlation_id: str = "",
    ) -> AssetHealth | None:
        """Get health status for an asset.

        Args:
            asset_id: The asset identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            AssetHealth if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_asset_hierarchy(
        self,
        asset_id: str,
        correlation_id: str = "",
    ) -> list[AssetHierarchy]:
        """Get the hierarchy for an asset.

        Args:
            asset_id: The asset identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of AssetHierarchy records.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> EnergyHealth:
        """Get the health status of the Energy Domain.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            EnergyHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> EnergyMetrics:
        """Get aggregated metrics for the Energy Domain.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            EnergyMetrics with current metric values.
        """
        ...


class EnergyDomainManager(ABC):
    """Internal manager interface for the Energy Domain.

    Lightweight facade over the EnergyDomainCoordinator for
    internal use by EnergyDomainService. Not intended for
    external consumers.
    """

    @abstractmethod
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
        ...

    @abstractmethod
    def get_asset(
        self,
        asset_id: str,
    ) -> EnergyAsset | None:
        """Retrieve an energy asset by ID.

        Args:
            asset_id: The asset identifier.

        Returns:
            EnergyAsset if found, None otherwise.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def get_sensor(
        self,
        sensor_id: str,
    ) -> Sensor | None:
        """Retrieve a sensor by ID.

        Args:
            sensor_id: The sensor identifier.

        Returns:
            Sensor if found, None otherwise.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def get_digital_twin(
        self,
        twin_id: str,
    ) -> DigitalTwin | None:
        """Retrieve a digital twin by ID.

        Args:
            twin_id: The digital twin identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def get_alarm(
        self,
        alarm_id: str,
    ) -> Alarm | None:
        """Retrieve an alarm by ID.

        Args:
            alarm_id: The alarm identifier.

        Returns:
            Alarm if found, None otherwise.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def get_asset_health(
        self,
        asset_id: str,
    ) -> AssetHealth | None:
        """Get health status for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            AssetHealth if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> EnergyHealth:
        """Get the health status of the Energy Domain.

        Returns:
            EnergyHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> EnergyMetrics:
        """Get aggregated metrics for the Energy Domain.

        Returns:
            EnergyMetrics with current metric values.
        """
        ...


class EnergyDomainCoordinator(ABC):
    """Coordinator interface for the energy domain pipeline.

    Orchestrates energy domain operations by delegating
    to sub-components in the correct order.
    """

    @abstractmethod
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
        ...

    @abstractmethod
    def get_asset(
        self,
        asset_id: str,
    ) -> EnergyAsset | None:
        """Retrieve an energy asset by ID.

        Args:
            asset_id: The asset identifier.

        Returns:
            EnergyAsset if found, None otherwise.
        """
        ...

    @abstractmethod
    def register_sensor(
        self,
        sensor: Sensor,
        correlation_id: str = "",
    ) -> Sensor:
        """Register a new sensor.

        Args:
            sensor: The sensor to register.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The registered Sensor.
        """
        ...

    @abstractmethod
    def get_sensor(
        self,
        sensor_id: str,
    ) -> Sensor | None:
        """Retrieve a sensor by ID.

        Args:
            sensor_id: The sensor identifier.

        Returns:
            Sensor if found, None otherwise.
        """
        ...

    @abstractmethod
    def receive_reading(
        self,
        reading: SensorReading,
        correlation_id: str = "",
    ) -> SensorReading:
        """Receive and process a sensor reading.

        Args:
            reading: The sensor reading to process.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The processed SensorReading.
        """
        ...

    @abstractmethod
    def create_digital_twin(
        self,
        twin: DigitalTwin,
        correlation_id: str = "",
    ) -> DigitalTwin:
        """Create a digital twin.

        Args:
            twin: The digital twin to create.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created DigitalTwin.
        """
        ...

    @abstractmethod
    def raise_alarm(
        self,
        alarm: Alarm,
        correlation_id: str = "",
    ) -> Alarm:
        """Raise a new alarm.

        Args:
            alarm: The alarm to raise.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The raised Alarm.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def health(self) -> EnergyHealth:
        """Get the health status of all sub-components.

        Returns:
            EnergyHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> EnergyMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            EnergyMetrics with current values.
        """
        ...


class AssetRepository(ABC):
    """Repository interface for energy asset persistence.

    Defines the contract for storing and retrieving energy
    assets from a data store.
    """

    @abstractmethod
    def save(self, asset: EnergyAsset) -> EnergyAsset:
        """Save an energy asset.

        Args:
            asset: The asset to save.

        Returns:
            The saved EnergyAsset.
        """
        ...

    @abstractmethod
    def find_by_id(self, asset_id: str) -> EnergyAsset | None:
        """Find an asset by its identifier.

        Args:
            asset_id: The asset identifier.

        Returns:
            EnergyAsset if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_type(self, asset_type: str) -> list[EnergyAsset]:
        """Find assets by type.

        Args:
            asset_type: The asset type to filter by.

        Returns:
            List of matching EnergyAsset objects.
        """
        ...

    @abstractmethod
    def find_by_domain(self, domain: str) -> list[EnergyAsset]:
        """Find assets by utility domain.

        Args:
            domain: The utility domain to filter by.

        Returns:
            List of matching EnergyAsset objects.
        """
        ...

    @abstractmethod
    def find_all(self) -> list[EnergyAsset]:
        """Retrieve all energy assets.

        Returns:
            List of all EnergyAsset objects.
        """
        ...

    @abstractmethod
    def delete(self, asset_id: str) -> bool:
        """Delete an energy asset.

        Args:
            asset_id: The asset identifier to delete.

        Returns:
            True if deleted, False otherwise.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Get the total number of assets.

        Returns:
            Total asset count.
        """
        ...


class SensorRepository(ABC):
    """Repository interface for sensor persistence.

    Defines the contract for storing and retrieving sensors
    and their readings from a data store.
    """

    @abstractmethod
    def save(self, sensor: Sensor) -> Sensor:
        """Save a sensor.

        Args:
            sensor: The sensor to save.

        Returns:
            The saved Sensor.
        """
        ...

    @abstractmethod
    def find_by_id(self, sensor_id: str) -> Sensor | None:
        """Find a sensor by its identifier.

        Args:
            sensor_id: The sensor identifier.

        Returns:
            Sensor if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_asset(self, asset_id: str) -> list[Sensor]:
        """Find sensors attached to an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of Sensor objects for the asset.
        """
        ...

    @abstractmethod
    def save_reading(self, reading: SensorReading) -> SensorReading:
        """Save a sensor reading.

        Args:
            reading: The reading to save.

        Returns:
            The saved SensorReading.
        """
        ...

    @abstractmethod
    def find_readings(
        self,
        sensor_id: str,
        limit: int = 100,
    ) -> list[SensorReading]:
        """Find recent readings for a sensor.

        Args:
            sensor_id: The sensor identifier.
            limit: Maximum number of readings to return.

        Returns:
            List of SensorReading objects.
        """
        ...

    @abstractmethod
    def delete(self, sensor_id: str) -> bool:
        """Delete a sensor.

        Args:
            sensor_id: The sensor identifier to delete.

        Returns:
            True if deleted, False otherwise.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Get the total number of sensors.

        Returns:
            Total sensor count.
        """
        ...


class DigitalTwinRepository(ABC):
    """Repository interface for digital twin persistence.

    Defines the contract for storing and retrieving digital
    twins from a data store.
    """

    @abstractmethod
    def save(self, twin: DigitalTwin) -> DigitalTwin:
        """Save a digital twin.

        Args:
            twin: The digital twin to save.

        Returns:
            The saved DigitalTwin.
        """
        ...

    @abstractmethod
    def find_by_id(self, twin_id: str) -> DigitalTwin | None:
        """Find a digital twin by its identifier.

        Args:
            twin_id: The twin identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_asset(self, asset_id: str) -> DigitalTwin | None:
        """Find the digital twin for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        ...

    @abstractmethod
    def delete(self, twin_id: str) -> bool:
        """Delete a digital twin.

        Args:
            twin_id: The twin identifier to delete.

        Returns:
            True if deleted, False otherwise.
        """
        ...


class MaintenanceRepository(ABC):
    """Repository interface for maintenance persistence.

    Defines the contract for storing and retrieving maintenance
    records and plans from a data store.
    """

    @abstractmethod
    def save_record(self, record: MaintenanceRecord) -> MaintenanceRecord:
        """Save a maintenance record.

        Args:
            record: The maintenance record to save.

        Returns:
            The saved MaintenanceRecord.
        """
        ...

    @abstractmethod
    def find_record_by_id(
        self,
        record_id: str,
    ) -> MaintenanceRecord | None:
        """Find a maintenance record by its identifier.

        Args:
            record_id: The record identifier.

        Returns:
            MaintenanceRecord if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_records_by_asset(
        self,
        asset_id: str,
    ) -> list[MaintenanceRecord]:
        """Find maintenance records for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of MaintenanceRecord objects.
        """
        ...

    @abstractmethod
    def save_plan(self, plan: MaintenancePlan) -> MaintenancePlan:
        """Save a maintenance plan.

        Args:
            plan: The maintenance plan to save.

        Returns:
            The saved MaintenancePlan.
        """
        ...

    @abstractmethod
    def find_plan_by_id(self, plan_id: str) -> MaintenancePlan | None:
        """Find a maintenance plan by its identifier.

        Args:
            plan_id: The plan identifier.

        Returns:
            MaintenancePlan if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_plans_by_asset(
        self,
        asset_id: str,
    ) -> list[MaintenancePlan]:
        """Find maintenance plans for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of MaintenancePlan objects.
        """
        ...


class AlarmRepository(ABC):
    """Repository interface for alarm persistence.

    Defines the contract for storing and retrieving alarms
    from a data store.
    """

    @abstractmethod
    def save(self, alarm: Alarm) -> Alarm:
        """Save an alarm.

        Args:
            alarm: The alarm to save.

        Returns:
            The saved Alarm.
        """
        ...

    @abstractmethod
    def find_by_id(self, alarm_id: str) -> Alarm | None:
        """Find an alarm by its identifier.

        Args:
            alarm_id: The alarm identifier.

        Returns:
            Alarm if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_asset(self, asset_id: str) -> list[Alarm]:
        """Find alarms for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of Alarm objects.
        """
        ...

    @abstractmethod
    def find_active(self) -> list[Alarm]:
        """Find all active alarms.

        Returns:
            List of active Alarm objects.
        """
        ...

    @abstractmethod
    def find_by_severity(self, severity: str) -> list[Alarm]:
        """Find alarms by severity level.

        Args:
            severity: The severity to filter by.

        Returns:
            List of matching Alarm objects.
        """
        ...

    @abstractmethod
    def delete(self, alarm_id: str) -> bool:
        """Delete an alarm.

        Args:
            alarm_id: The alarm identifier to delete.

        Returns:
            True if deleted, False otherwise.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Get the total number of alarms.

        Returns:
            Total alarm count.
        """
        ...
