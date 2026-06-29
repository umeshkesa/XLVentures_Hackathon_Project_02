"""EnergyReadinessReportGenerator — generates operational readiness
summaries.

Generates comprehensive operational readiness summaries
from health, sensor, alarm, maintenance, topology, quality,
and compliance checks. Deterministic placeholder.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.energy.orchestration.models import EnergyReadinessReport

log = structlog.get_logger(__name__)


class EnergyReadinessReportGenerator:
    """Generates operational readiness reports for energy assets.

    Produces a comprehensive readiness summary from multiple
    check dimensions. Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._reports: dict[str, EnergyReadinessReport] = {}

    def generate_report(
        self,
        asset_id: str,
        health_ok: bool = True,
        sensors_active: bool = True,
        no_critical_alarms: bool = True,
        maintenance_current: bool = True,
        topology_ok: bool = True,
        quality_ok: bool = True,
        compliance_ok: bool = True,
        correlation_id: str = "",
    ) -> EnergyReadinessReport:
        """Generate an operational readiness report.

        Args:
            asset_id: The asset identifier.
            health_ok: Whether health checks pass.
            sensors_active: Whether required sensors are active.
            no_critical_alarms: Whether no critical alarms exist.
            maintenance_current: Whether maintenance is current.
            topology_ok: Whether topology is valid.
            quality_ok: Whether quality checks pass.
            compliance_ok: Whether compliance checks pass.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            EnergyReadinessReport with readiness summary.
        """
        checks = {
            "health_ok": health_ok,
            "sensors_active": sensors_active,
            "no_critical_alarms": no_critical_alarms,
            "maintenance_current": maintenance_current,
            "topology_ok": topology_ok,
            "quality_ok": quality_ok,
            "compliance_ok": compliance_ok,
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score = round(passed / total, 4) if total > 0 else 1.0

        if score >= 0.85:
            overall_status = "READY"
            summary = "Asset is fully operational and ready"
        elif score >= 0.6:
            overall_status = "PENDING"
            failed = [k for k, v in checks.items() if not v]
            summary = f"Asset partially ready. Issues: {', '.join(failed)}"
        else:
            overall_status = "NOT_READY"
            failed = [k for k, v in checks.items() if not v]
            summary = f"Asset not ready. Critical issues: {', '.join(failed)}"

        report = EnergyReadinessReport(
            asset_id=asset_id,
            overall_status=overall_status,
            health_ok=health_ok,
            sensors_active=sensors_active,
            no_critical_alarms=no_critical_alarms,
            maintenance_current=maintenance_current,
            topology_ok=topology_ok,
            quality_ok=quality_ok,
            compliance_ok=compliance_ok,
            score=score,
            summary=summary,
            timestamp=datetime.now(UTC),
        )
        rid = str(report.report_id)
        self._reports[rid] = report
        log.info(
            "readiness_report.generated",
            report_id=rid,
            asset_id=asset_id,
            status=overall_status,
            score=score,
            correlation_id=correlation_id,
        )
        return report

    def get_report(self, report_id: str) -> EnergyReadinessReport | None:
        """Get a readiness report by ID.

        Args:
            report_id: The report identifier.

        Returns:
            EnergyReadinessReport if found, None otherwise.
        """
        return self._reports.get(report_id)

    def get_reports_for_asset(self, asset_id: str) -> list[EnergyReadinessReport]:
        """Get all readiness reports for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of EnergyReadinessReport instances.
        """
        return [r for r in self._reports.values() if r.asset_id == asset_id]

    def count(self) -> int:
        """Get the number of readiness reports.

        Returns:
            The count of readiness reports.
        """
        return len(self._reports)

    def clear(self) -> None:
        """Clear all readiness reports."""
        self._reports.clear()
        log.info("readiness_reports.cleared")
