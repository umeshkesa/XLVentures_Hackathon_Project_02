"""DefaultEnergyDomainService — the ONLY public API.

Provides the external interface for energy domain operations
with authentication hooks, audit hooks, integration hooks,
structured logging, metrics, and correlation ID propagation.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.energy.contracts.models import (
    Alarm,
    AssetHealth,
    AssetHierarchy,
    DigitalTwin,
    EnergyAsset,
    EnergyHealth,
    EnergyMetrics,
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
    MaintenanceType,
)
from adip.energy.orchestration.manager import EnergyDomainManager
from adip.energy.orchestration.models import EnergyDecision
from adip.energy.services.hooks import IntegrationHooks
from adip.energy.services.hooks import hooks as global_hooks

log = structlog.get_logger(__name__)


class DefaultEnergyDomainService:
    """Default implementation of the EnergyDomainService interface.

    This is the ONLY public API for all energy domain operations.
    Provides auth/audit hooks, integration hooks, structured logging,
    correlation ID propagation, and delegation to EnergyDomainManager.

    Deterministic placeholder implementation.
    """

    def __init__(
        self,
        manager: EnergyDomainManager | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[[str, str], bool] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or EnergyDomainManager()
        self._hooks = hooks or global_hooks
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def _check_auth(self, user_id: str, operation: str) -> bool:
        """Check if a user is authorised for an operation.

        Args:
            user_id: The user identifier.
            operation: The operation to check.

        Returns:
            True if authorised (or no auth callback configured), False otherwise.
        """
        if self._auth_callback and user_id:
            return self._auth_callback(user_id, operation)
        return True

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.register_asset", name=asset_dto.name, user=user_id, cid=cid)

        if not self._check_auth(user_id, "register_asset"):
            log.warning("service.auth.failed", user=user_id, operation="register_asset")
            return None

        try:
            self._hooks.run_pre_register_asset(
                name=asset_dto.name,
                asset_type=asset_dto.asset_type.value,
                user_id=user_id,
                correlation_id=cid,
            )

            asset = EnergyAsset(
                asset_id=asset_dto.asset_id or uuid.uuid4(),
                external_id=asset_dto.external_id,
                name=asset_dto.name,
                asset_type=asset_dto.asset_type,
                domain=asset_dto.domain,
                status=asset_dto.status,
                location=asset_dto.location,
                latitude=asset_dto.latitude,
                longitude=asset_dto.longitude,
                rated_capacity=asset_dto.rated_capacity,
                tags=asset_dto.tags,
                metadata=asset_dto.metadata,
            )
            result = self._manager.register_asset(asset, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "register_asset",
                    user_id,
                    str(result.asset_id),
                    {"name": result.name, "type": result.asset_type.value},
                )

            self._hooks.run_post_register_asset(
                asset_id=str(result.asset_id),
                name=result.name,
                user_id=user_id,
                correlation_id=cid,
            )

            log.info("service.register_asset.complete", asset_id=str(result.asset_id))
            return result

        except Exception as e:
            log.error("service.register_asset.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="register_asset", error=str(e), correlation_id=cid)
            raise

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_asset", asset_id=asset_id, cid=cid)
        return self._manager.get_asset(asset_id)

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
            Updated EnergyAsset if found and authorised, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.update_asset", asset_id=asset_id, user=user_id, cid=cid)

        if not self._check_auth(user_id, "update_asset"):
            log.warning("service.auth.failed", user=user_id, operation="update_asset")
            return None

        try:
            existing = self._manager.get_asset(asset_id)
            if existing is None:
                log.warning("service.asset.not_found", asset_id=asset_id)
                return None

            asset = EnergyAsset(
                asset_id=existing.asset_id,
                external_id=asset_dto.external_id or existing.external_id,
                name=asset_dto.name or existing.name,
                asset_type=asset_dto.asset_type or existing.asset_type,
                domain=asset_dto.domain or existing.domain,
                status=asset_dto.status or existing.status,
                location=asset_dto.location or existing.location,
                latitude=asset_dto.latitude if asset_dto.latitude is not None else existing.latitude,
                longitude=asset_dto.longitude if asset_dto.longitude is not None else existing.longitude,
                rated_capacity=asset_dto.rated_capacity if asset_dto.rated_capacity is not None else existing.rated_capacity,
                tags=asset_dto.tags or existing.tags,
                metadata=asset_dto.metadata or existing.metadata,
            )
            result = self._manager.update_asset(asset_id, asset, correlation_id=cid)

            if result and self._audit_callback:
                self._audit_callback(
                    "update_asset",
                    user_id,
                    asset_id,
                    {"name": result.name},
                )

            log.info("service.update_asset.complete", asset_id=asset_id)
            return result

        except Exception as e:
            log.error("service.update_asset.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="update_asset", error=str(e), correlation_id=cid)
            raise

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.register_sensor", name=sensor_dto.name, user=user_id, cid=cid)

        if not self._check_auth(user_id, "register_sensor"):
            log.warning("service.auth.failed", user=user_id, operation="register_sensor")
            return None

        try:
            self._hooks.run_pre_register_sensor(
                name=sensor_dto.name,
                sensor_type=sensor_dto.sensor_type.value,
                user_id=user_id,
                correlation_id=cid,
            )

            sensor = Sensor(
                sensor_id=sensor_dto.sensor_id or uuid.uuid4(),
                asset_id=sensor_dto.asset_id,
                external_id=sensor_dto.external_id,
                name=sensor_dto.name,
                sensor_type=sensor_dto.sensor_type,
                unit=sensor_dto.unit,
                is_active=sensor_dto.is_active,
                sampling_interval_seconds=sensor_dto.sampling_interval_seconds,
                location=sensor_dto.location,
                metadata=sensor_dto.metadata,
            )
            result = self._manager.register_sensor(sensor, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "register_sensor",
                    user_id,
                    str(result.sensor_id),
                    {"name": result.name, "type": result.sensor_type.value},
                )

            self._hooks.run_post_register_sensor(
                sensor_id=str(result.sensor_id),
                name=result.name,
                user_id=user_id,
                correlation_id=cid,
            )

            log.info("service.register_sensor.complete", sensor_id=str(result.sensor_id))
            return result

        except Exception as e:
            log.error("service.register_sensor.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="register_sensor", error=str(e), correlation_id=cid)
            raise

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_sensor", sensor_id=sensor_id, cid=cid)
        return self._manager.get_sensor(sensor_id)

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.receive_reading", sensor_id=sensor_id, value=value, cid=cid)

        try:
            sensor = self._manager.get_sensor(sensor_id)
            if sensor is None:
                log.warning("service.sensor.not_found", sensor_id=sensor_id)
                return None

            reading = SensorReading(
                sensor_id=uuid.UUID(sensor_id) if isinstance(sensor_id, str) else sensor_id,
                asset_id=sensor.asset_id,
                value=value,
                unit=unit or sensor.unit,
                quality=quality,
            )
            result = self._manager.receive_reading(reading, correlation_id=cid)

            self._hooks.run_post_receive_reading(
                reading_id=str(result.reading_id),
                sensor_id=sensor_id,
                value=value,
                correlation_id=cid,
            )

            log.info("service.receive_reading.complete", reading_id=str(result.reading_id))
            return result

        except Exception as e:
            log.error("service.receive_reading.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="receive_reading", error=str(e), correlation_id=cid)
            raise

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
            DigitalTwin if created and authorised, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.create_digital_twin", asset_id=str(twin_dto.asset_id), user=user_id, cid=cid)

        if not self._check_auth(user_id, "create_digital_twin"):
            log.warning("service.auth.failed", user=user_id, operation="create_digital_twin")
            return None

        try:
            self._hooks.run_pre_create_twin(
                asset_id=str(twin_dto.asset_id),
                twin_type=twin_dto.twin_type,
                user_id=user_id,
                correlation_id=cid,
            )

            twin = DigitalTwin(
                twin_id=twin_dto.twin_id or uuid.uuid4(),
                asset_id=twin_dto.asset_id,
                twin_type=twin_dto.twin_type,
                model_version=twin_dto.model_version,
                parameters=twin_dto.parameters,
                is_active=twin_dto.is_active,
                metadata=twin_dto.metadata,
            )
            result = self._manager.create_digital_twin(twin, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "create_digital_twin",
                    user_id,
                    str(result.twin_id),
                    {"asset_id": str(result.asset_id), "twin_type": result.twin_type},
                )

            self._hooks.run_post_create_twin(
                twin_id=str(result.twin_id),
                asset_id=str(result.asset_id),
                user_id=user_id,
                correlation_id=cid,
            )

            log.info("service.create_digital_twin.complete", twin_id=str(result.twin_id))
            return result

        except Exception as e:
            log.error("service.create_digital_twin.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="create_digital_twin", error=str(e), correlation_id=cid)
            raise

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
            Alarm if raised and authorised, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.raise_alarm", name=alarm_dto.name, user=user_id, cid=cid)

        if not self._check_auth(user_id, "raise_alarm"):
            log.warning("service.auth.failed", user=user_id, operation="raise_alarm")
            return None

        try:
            self._hooks.run_pre_raise_alarm(
                name=alarm_dto.name,
                severity=alarm_dto.severity.value,
                user_id=user_id,
                correlation_id=cid,
            )

            alarm = Alarm(
                alarm_id=alarm_dto.alarm_id or uuid.uuid4(),
                asset_id=alarm_dto.asset_id,
                external_id=alarm_dto.external_id,
                name=alarm_dto.name,
                description=alarm_dto.description,
                severity=alarm_dto.severity,
                status=alarm_dto.status,
                source=alarm_dto.source,
                metadata=alarm_dto.metadata,
            )
            result = self._manager.raise_alarm(alarm, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "raise_alarm",
                    user_id,
                    str(result.alarm_id),
                    {"name": result.name, "severity": result.severity.value},
                )

            self._hooks.run_post_raise_alarm(
                alarm_id=str(result.alarm_id),
                name=result.name,
                user_id=user_id,
                correlation_id=cid,
            )

            log.info("service.raise_alarm.complete", alarm_id=str(result.alarm_id))
            return result

        except Exception as e:
            log.error("service.raise_alarm.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="raise_alarm", error=str(e), correlation_id=cid)
            raise

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
            Incident if created and authorised, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.create_incident", title=incident_dto.title, user=user_id, cid=cid)

        if not self._check_auth(user_id, "create_incident"):
            log.warning("service.auth.failed", user=user_id, operation="create_incident")
            return None

        try:
            self._hooks.run_pre_create_incident(
                title=incident_dto.title,
                priority=incident_dto.priority.value,
                user_id=user_id,
                correlation_id=cid,
            )

            incident = Incident(
                incident_id=incident_dto.incident_id or uuid.uuid4(),
                external_id=incident_dto.external_id,
                title=incident_dto.title,
                description=incident_dto.description,
                asset_ids=incident_dto.asset_ids,
                alarm_ids=incident_dto.alarm_ids,
                priority=incident_dto.priority,
                impact_area=incident_dto.impact_area,
                customers_affected=incident_dto.customers_affected,
                reported_by=incident_dto.reported_by,
                metadata=incident_dto.metadata,
            )
            result = self._manager.create_incident(incident, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "create_incident",
                    user_id,
                    str(result.incident_id),
                    {"title": result.title, "priority": result.priority.value},
                )

            self._hooks.run_post_create_incident(
                incident_id=str(result.incident_id),
                title=result.title,
                user_id=user_id,
                correlation_id=cid,
            )

            log.info("service.create_incident.complete", incident_id=str(result.incident_id))
            return result

        except Exception as e:
            log.error("service.create_incident.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="create_incident", error=str(e), correlation_id=cid)
            raise

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
            MaintenanceRecord if recorded and authorised, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.record_maintenance", asset_id=asset_id, user=user_id, cid=cid)

        if not self._check_auth(user_id, "record_maintenance"):
            log.warning("service.auth.failed", user=user_id, operation="record_maintenance")
            return None

        try:
            maint_enum = MaintenanceType(maintenance_type.upper()) if maintenance_type else MaintenanceType.PREVENTIVE
        except ValueError:
            maint_enum = MaintenanceType.PREVENTIVE

        try:
            self._hooks.run_pre_record_maintenance(
                asset_id=asset_id,
                maintenance_type=maint_enum.value,
                user_id=user_id,
                correlation_id=cid,
            )

            record = MaintenanceRecord(
                asset_id=uuid.UUID(asset_id) if isinstance(asset_id, str) else asset_id,
                maintenance_type=maint_enum,
                technician=technician,
                description=description,
                duration_hours=duration_hours,
                completed_date=datetime.now(UTC),
            )
            result = self._manager.record_maintenance(record, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "record_maintenance",
                    user_id,
                    str(result.record_id),
                    {"asset_id": asset_id, "type": maint_enum.value},
                )

            self._hooks.run_post_record_maintenance(
                record_id=str(result.record_id),
                asset_id=asset_id,
                user_id=user_id,
                correlation_id=cid,
            )

            log.info("service.record_maintenance.complete", record_id=str(result.record_id))
            return result

        except Exception as e:
            log.error("service.record_maintenance.error", error=str(e), cid=cid)
            self._hooks.run_on_error(operation="record_maintenance", error=str(e), correlation_id=cid)
            raise

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_asset_health", asset_id=asset_id, cid=cid)
        return self._manager.get_asset_health(asset_id)

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_asset_hierarchy", asset_id=asset_id, cid=cid)
        return []

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_health", cid=cid)
        return self._manager.get_health()

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
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_metrics", cid=cid)
        return self._manager.get_metrics()

    def get_decision(self, decision_id: str) -> EnergyDecision | None:
        """Retrieve an energy decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            EnergyDecision if found, None otherwise.
        """
        log.info("service.get_decision", decision_id=decision_id)
        return self._manager.get_decision(decision_id)
