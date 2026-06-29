from __future__ import annotations

import structlog

from adip.data_import.importers.base import BaseImporter
from adip.data_import.readers import read_json, read_text
from adip.data_import.statistics import ImportStats

log = structlog.get_logger(__name__)


class ScenarioImporter(BaseImporter):
    """Phase 6: Import scenario data (5 multi-file scenario bundles)."""

    @property
    def phase_name(self) -> str:
        return "SCENARIOS"

    SCENARIO_DIRS = [
        "SCN001_Transformer_Overheating",
        "SCN002_Cooling_Failure",
        "SCN003_Wind_Vibration",
        "SCN004_Power_Spike",
        "SCN005_SLA_Breach",
    ]

    def run(self) -> ImportStats:
        self.timer.start()
        self.stats.phase = self.phase_name

        log.info("import.phase.scenarios.start")

        for scenario_dir in self.SCENARIO_DIRS:
            self._import_scenario(scenario_dir)

        self.timer.stop()
        self.stats.execution_time_seconds = self.timer.elapsed
        log.info("import.phase.scenarios.complete", stats=self.stats.to_dict())
        return self.stats

    def _import_scenario(self, scenario_dir: str) -> None:
        base = f"scenarios/{scenario_dir}"
        log.info("import.scenario", directory=scenario_dir)

        incident_report = self.text_content(f"{base}/incident_report.txt")
        customer_email = self.text_content(f"{base}/customer_email.txt")
        outcome = self.json_data(f"{base}/outcome.json")
        recommendation = self.json_data(f"{base}/recommendation.json")

        scenario_id = scenario_dir.split("_")[0]
        if self.dedup.is_duplicate_by_key("scenario_id", {"scenario_id": scenario_id}):
            self.stats.duplicates += 1
            log.info("import.scenario.duplicate", scenario_id=scenario_id)
            return

        self.stats.total_records += 1
        self.stats.imported += 1
        self.stats.file_breakdown[scenario_dir] = {
            "total": 1,
            "imported": 1,
        }

        log.info(
            "import.scenario.complete",
            scenario=scenario_dir,
            incident=bool(incident_report),
            email=bool(customer_email),
            outcome=outcome is not None,
            recommendation=recommendation is not None,
        )
