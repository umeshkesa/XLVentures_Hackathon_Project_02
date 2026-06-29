from __future__ import annotations

import structlog

from adip.data_import.importers.base import BaseImporter
from adip.data_import.statistics import ImportStats

log = structlog.get_logger(__name__)


class OperationsImporter(BaseImporter):
    """Phase 2: Import operational data."""

    @property
    def phase_name(self) -> str:
        return "OPERATIONS"

    def run(self) -> ImportStats:
        self.timer.start()
        self.stats.phase = self.phase_name
        log.info("import.phase.operations.start")

        self._import_csv("operations/incidents/incident_reports.csv", "incident_reports.csv",
                         ["incident_id", "asset_id", "customer_id", "severity"], "incident_id")
        self._import_csv("operations/work_orders/work_orders.csv", "work_orders.csv",
                         ["work_order_id", "asset_id", "customer_id"], "work_order_id")
        self._import_csv("operations/maintenance/maintenance_history.csv", "maintenance_history.csv",
                         ["maintenance_id", "asset_id"], "maintenance_id")
        self._import_csv("operations/scada_logs/alarm_logs.csv", "alarm_logs.csv",
                         ["timestamp", "asset_id"], None)
        self._import_csv("customer_interactions/service_requests/service_requests.csv", "service_requests.csv",
                         ["request_id", "customer_id", "asset_id"], "request_id")
        self._import_csv("customer_interactions/complaints/complaints.csv", "complaints.csv",
                         ["complaint_id", "customer_id"], "complaint_id")
        self._import_csv("customer_interactions/feedback/feedback.csv", "feedback.csv",
                         ["feedback_id", "customer_id"], "feedback_id")
        self._import_csv("customer_interactions/crm_updates/crm_updates.csv", "crm_updates.csv",
                         ["crm_id", "customer_id"], "crm_id")
        self._import_csv("operations/inventory/spare_parts_inventory.csv", "spare_parts_inventory.csv",
                         ["part_id", "part_name"], "part_id")
        self._import_csv("operations/weather_data/weather_india.csv", "weather_india.csv",
                         ["city"], None)

        self.timer.stop()
        self.stats.execution_time_seconds = self.timer.elapsed
        log.info("import.phase.operations.complete", stats=self.stats.to_dict())
        return self.stats

    def _import_csv(self, rel_path: str, fname: str,
                    required: list[str], key: str | None) -> None:
        rows, validation, dup_count, skip_count = self._import_csv_rows(
            rel_path,
            required_fields=required,
            key_fields=[key] if key else None,
        )
        self.stats.total_records += len(rows) + validation.dict()["error_count"] + dup_count
        self.stats.imported += len(rows)
        self.stats.validation_errors += validation.dict()["error_count"]
        self.stats.duplicates += dup_count
        self.stats.skipped += skip_count
        self.stats.file_breakdown[fname] = {
            "total": len(rows) + validation.dict()["error_count"] + dup_count,
            "imported": len(rows),
            "errors": validation.dict()["error_count"],
            "duplicates": dup_count,
            "skipped": skip_count,
        }
        log.info("import.file.complete", file=fname, imported=len(rows),
                 errors=validation.dict()["error_count"], duplicates=dup_count)
