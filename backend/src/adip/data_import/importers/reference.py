from __future__ import annotations

import structlog

from adip.data_import.importers.base import BaseImporter
from adip.data_import.statistics import ImportStats

log = structlog.get_logger(__name__)


class ReferenceImporter(BaseImporter):
    """Phase 1: Import reference/master data."""

    @property
    def phase_name(self) -> str:
        return "REFERENCE"

    def run(self) -> ImportStats:
        self.timer.start()
        self.stats.phase = self.phase_name
        log.info("import.phase.reference.start")

        self._import("customer_profiles/customers.csv",
                     "customers.csv",
                     ["customer_id", "company_name"],
                     "customer_id")
        self._import("operations/facility_profiles/facilities.csv",
                     "facilities.csv",
                     ["facility_id", "facility_name", "customer_id"],
                     "facility_id")
        self._import("operations/equipment_registry/equipment_registry.csv",
                     "equipment_registry.csv",
                     ["asset_id", "asset_name", "asset_type", "customer_id"],
                     "asset_id")
        self._import("operations/technician_profiles/technicians.csv",
                     "technicians.csv",
                     ["technician_id", "name"],
                     "technician_id")

        self.timer.stop()
        self.stats.execution_time_seconds = self.timer.elapsed
        log.info("import.phase.reference.complete", stats=self.stats.to_dict())
        return self.stats

    def _import(self, rel_path: str, fname: str, required: list[str], key: str) -> None:
        rows, validation, dup_count, skip_count = self._import_csv_rows(
            rel_path,
            required_fields=required,
            key_fields=[key],
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
        if not rows:
            log.info("import.no_rows", file=fname)
