"""EnergyReadinessCalculator — assesses readiness for energy operations.

Determines whether an asset is ready for operations based on
health, sensor, maintenance, alarm, and topology checks.
Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.energy.orchestration.models import EnergyReadiness

log = structlog.get_logger(__name__)

_READINESS_WEIGHTS: dict[str, float] = {
    "health_ok": 0.30,
    "sensors_active": 0.25,
    "no_critical_alarms": 0.20,
    "maintenance_uptodate": 0.15,
    "topology_connected": 0.10,
}


class EnergyReadinessCalculator:
    """Assesses readiness of an energy asset for operations.

    Evaluates multiple dimensions of asset readiness and produces
    a composite status. Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._readiness_records: dict[str, EnergyReadiness] = {}

    def assess_readiness(
        self,
        asset_id: str,
        health_score: float = 1.0,
        sensors_active: bool = True,
        has_critical_alarms: bool = False,
        maintenance_current: bool = True,
        topology_ok: bool = True,
        correlation_id: str = "",
    ) -> EnergyReadiness:
        """Assess the readiness of an asset.

        Args:
            asset_id: The asset identifier.
            health_score: Current health score (0.0 to 1.0).
            sensors_active: Whether all required sensors are active.
            has_critical_alarms: Whether critical alarms are active.
            maintenance_current: Whether maintenance is up-to-date.
            topology_ok: Whether topology connectivity is OK.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            EnergyReadiness with the readiness assessment.
        """
        checks: dict[str, bool] = {
            "health_ok": health_score >= 0.5,
            "sensors_active": sensors_active,
            "no_critical_alarms": not has_critical_alarms,
            "maintenance_uptodate": maintenance_current,
            "topology_connected": topology_ok,
        }

        weighted_score = sum(
            _READINESS_WEIGHTS[k] * (1.0 if v else 0.0)
            for k, v in checks.items()
        )

        if weighted_score >= 0.8:
            status = "READY"
            reason = "All readiness conditions met"
        elif weighted_score >= 0.5:
            status = "PENDING"
            failed = [k for k, v in checks.items() if not v]
            reason = f"Some checks pending: {', '.join(failed)}"
        else:
            status = "BLOCKED"
            failed = [k for k, v in checks.items() if not v]
            reason = f"Critical checks failed: {', '.join(failed)}"

        readiness = EnergyReadiness(
            asset_id=uuid.UUID(asset_id) if isinstance(asset_id, str) else asset_id,
            status=status,
            checks=checks,
            reason=reason,
            timestamp=datetime.now(UTC),
        )
        rid = str(readiness.readiness_id)
        self._readiness_records[rid] = readiness

        log.info(
            "readiness.assessed",
            readiness_id=rid,
            asset_id=asset_id,
            status=status,
            weighted_score=round(weighted_score, 2),
            correlation_id=correlation_id,
        )
        return readiness

    def get_readiness(self, readiness_id: str) -> EnergyReadiness | None:
        """Get a readiness record by ID.

        Args:
            readiness_id: The readiness identifier.

        Returns:
            EnergyReadiness if found, None otherwise.
        """
        return self._readiness_records.get(readiness_id)

    def get_readiness_for_asset(self, asset_id: str) -> EnergyReadiness | None:
        """Get the latest readiness record for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            EnergyReadiness if found, None otherwise.
        """
        for record in self._readiness_records.values():
            if str(record.asset_id) == asset_id:
                return record
        return None

    def count(self) -> int:
        """Get the number of readiness records.

        Returns:
            The count of readiness records.
        """
        return len(self._readiness_records)

    def clear(self) -> None:
        """Clear all readiness records."""
        self._readiness_records.clear()
        log.info("readiness.cleared")
