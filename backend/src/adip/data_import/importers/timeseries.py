from __future__ import annotations

from pathlib import Path

import structlog

from adip.data_import.importers.base import BaseImporter
from adip.data_import.readers import get_csv_stats, read_csv_chunked
from adip.data_import.statistics import ImportStats

log = structlog.get_logger(__name__)


class TimeSeriesImporter(BaseImporter):
    """Phase 5: Import time-series data (ai4i2020 sensor data, CU-BEMS building energy)."""

    @property
    def phase_name(self) -> str:
        return "TIME_SERIES"

    def run(self) -> ImportStats:
        self.timer.start()
        self.stats.phase = self.phase_name

        log.info("import.phase.timeseries.start")

        self._import_ai4i2020()
        self._import_cu_bems_sample()

        self.timer.stop()
        self.stats.execution_time_seconds = self.timer.elapsed
        log.info("import.phase.timeseries.complete", stats=self.stats.to_dict())
        return self.stats

    def _import_ai4i2020(self) -> None:
        path = self.csv_path("operations/sensor_data/ai4i2020.csv")
        if not path.is_file():
            log.warning("import.file_not_found", path=str(path))
            return

        stats = get_csv_stats(path)
        total = stats["rows"]
        chunk_size = 1000
        imported = 0

        for chunk in read_csv_chunked(path, chunk_size=chunk_size):
            chunk_imported = 0
            for row in chunk:
                if self.dedup.is_duplicate_by_key("udi", row):
                    self.stats.duplicates += 1
                    continue
                chunk_imported += 1
            imported += chunk_imported

        self.stats.total_records += total
        self.stats.imported += imported
        self.stats.file_breakdown["ai4i2020.csv"] = {
            "total": total,
            "imported": imported,
        }
        log.info("import.ai4i2020.complete", total=total, imported=imported)

    def _import_cu_bems_sample(self) -> None:
        base_dir = "operations/energy_reports/CU-BEMS dataset files"
        dir_path = self.resolve_path(base_dir)
        if not dir_path.is_dir():
            log.warning("import.directory_not_found", path=str(dir_path))
            return

        csv_files = sorted(dir_path.glob("*.csv"))
        total_files = len(csv_files)
        imported = 0
        total_rows = 0

        for fpath in csv_files:
            stats = get_csv_stats(fpath)
            total_rows += stats["rows"]
        imported = total_files

        self.stats.total_records += total_rows
        self.stats.imported += imported
        self.stats.file_breakdown["CU-BEMS"] = {
            "total_files": total_files,
            "imported_files": imported,
            "total_rows": total_rows,
        }
        log.info(
            "import.cu_bems.complete",
            files=total_files,
            imported=imported,
            total_rows=total_rows,
        )
