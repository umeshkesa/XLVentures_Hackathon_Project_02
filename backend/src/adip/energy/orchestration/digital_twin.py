"""DigitalTwinManager — manages digital twin synchronization.

Coordinates digital twin state with placeholder synchronization logic.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.energy.contracts.models import DigitalTwin

log = structlog.get_logger(__name__)


class DigitalTwinManager:
    """Manages digital twin creation, synchronization, and lifecycle.

    Provides digital twin operations with placeholder synchronization
    logic. No actual device communication or twin synchronization.
    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._twins: dict[str, DigitalTwin] = {}
        self._sync_history: dict[str, list[dict[str, Any]]] = {}

    def create_twin(
        self,
        asset_id: str,
        twin_type: str = "simulation",
        model_version: str = "1.0.0",
        parameters: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> DigitalTwin:
        """Create a new digital twin for an asset.

        Args:
            asset_id: The asset identifier.
            twin_type: Type of twin (simulation, monitoring, predictive).
            model_version: Version of the digital twin model.
            parameters: Twin model parameters.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created DigitalTwin.
        """
        twin = DigitalTwin(
            asset_id=uuid.UUID(asset_id) if isinstance(asset_id, str) else asset_id,
            twin_type=twin_type,
            model_version=model_version,
            parameters=parameters or {},
            state={"initialized": True, "last_update": datetime.now(UTC).isoformat()},
            is_active=True,
        )
        tid = str(twin.twin_id)
        self._twins[tid] = twin
        self._sync_history[tid] = []
        log.info(
            "digital_twin.created",
            twin_id=tid,
            asset_id=asset_id,
            correlation_id=correlation_id,
        )
        return twin

    def get_twin(self, twin_id: str) -> DigitalTwin | None:
        """Get a digital twin by ID.

        Args:
            twin_id: The twin identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        return self._twins.get(twin_id)

    def get_twin_for_asset(self, asset_id: str) -> DigitalTwin | None:
        """Get the digital twin for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            DigitalTwin if found, None otherwise.
        """
        for twin in self._twins.values():
            if str(twin.asset_id) == asset_id:
                return twin
        return None

    def synchronise(
        self,
        twin_id: str,
        sensor_data: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> DigitalTwin | None:
        """Synchronise a digital twin with placeholder sensor data.

        Args:
            twin_id: The twin identifier.
            sensor_data: Optional sensor data to synchronise.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Updated DigitalTwin if found, None otherwise.
        """
        twin = self._twins.get(twin_id)
        if twin is None:
            log.warning("digital_twin.not_found", twin_id=twin_id)
            return None

        sync_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "sensor_data": sensor_data or {},
            "status": "synchronised",
        }
        self._sync_history[twin_id].append(sync_record)

        twin.last_synchronised = datetime.now(UTC)
        twin.state = {
            "initialized": True,
            "last_update": datetime.now(UTC).isoformat(),
            "synchronisations": len(self._sync_history[twin_id]),
            "latest_data": sensor_data or {},
        }
        self._twins[twin_id] = twin
        log.info(
            "digital_twin.synchronised",
            twin_id=twin_id,
            correlation_id=correlation_id,
        )
        return twin

    def get_sync_history(
        self,
        twin_id: str,
    ) -> list[dict[str, Any]]:
        """Get synchronisation history for a twin.

        Args:
            twin_id: The twin identifier.

        Returns:
            List of sync history records.
        """
        return self._sync_history.get(twin_id, [])

    def activate(self, twin_id: str) -> DigitalTwin | None:
        """Activate a digital twin.

        Args:
            twin_id: The twin identifier.

        Returns:
            Updated DigitalTwin if found, None otherwise.
        """
        twin = self._twins.get(twin_id)
        if twin is None:
            return None
        twin.is_active = True
        twin.updated_at = datetime.now(UTC)
        self._twins[twin_id] = twin
        log.info("digital_twin.activated", twin_id=twin_id)
        return twin

    def deactivate(self, twin_id: str) -> DigitalTwin | None:
        """Deactivate a digital twin.

        Args:
            twin_id: The twin identifier.

        Returns:
            Updated DigitalTwin if found, None otherwise.
        """
        twin = self._twins.get(twin_id)
        if twin is None:
            return None
        twin.is_active = False
        twin.updated_at = datetime.now(UTC)
        self._twins[twin_id] = twin
        log.info("digital_twin.deactivated", twin_id=twin_id)
        return twin

    def count(self) -> int:
        """Get the number of digital twins.

        Returns:
            The number of digital twins.
        """
        return len(self._twins)

    def clear(self) -> None:
        """Clear all digital twins and sync history."""
        self._twins.clear()
        self._sync_history.clear()
        log.info("digital_twins.cleared")
