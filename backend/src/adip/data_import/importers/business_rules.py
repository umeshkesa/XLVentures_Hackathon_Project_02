from __future__ import annotations

import structlog

from adip.data_import.importers.base import BaseImporter
from adip.data_import.readers import read_json
from adip.data_import.statistics import ImportStats

log = structlog.get_logger(__name__)


class BusinessRulesImporter(BaseImporter):
    """Phase 3: Import business rules, compliance, contracts, SLA, recommendations."""

    @property
    def phase_name(self) -> str:
        return "BUSINESS_RULES"

    def run(self) -> ImportStats:
        self.timer.start()
        self.stats.phase = self.phase_name
        log.info("import.phase.business_rules.start")

        self._import_csv("business/sla/sla_definitions.csv", "sla_definitions.csv",
                         ["sla_id", "sla_type"], "sla_id")
        self._import_csv("business/compliance/compliance_requirements.csv", "compliance_requirements.csv",
                         ["compliance_id", "standard"], "compliance_id")
        self._import_csv("business/contracts/contracts.csv", "contracts.csv",
                         ["contract_id", "customer_id"], "contract_id")
        self._import_rules_json()
        self._import_csv("business/recommendation_history/recommendations.csv", "recommendations.csv",
                         ["recommendation_id", "incident_id"], "recommendation_id")

        self.timer.stop()
        self.stats.execution_time_seconds = self.timer.elapsed
        log.info("import.phase.business_rules.complete", stats=self.stats.to_dict())
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

    def _import_rules_json(self) -> None:
        path = self.csv_path("business/business_rules/rules.json")
        try:
            data = read_json(path)
        except FileNotFoundError:
            log.warning("import.file_not_found", path=str(path))
            return

        if not isinstance(data, list):
            log.warning("import.invalid_json_format", path=str(path))
            return

        imported = 0
        duplicates = 0
        for rule in data:
            rule_id = rule.get("rule_id", "")
            if self.dedup.is_duplicate_by_key("rule_id", {"rule_id": rule_id}):
                duplicates += 1
                continue
            imported += 1

        self.stats.total_records += len(data)
        self.stats.imported += imported
        self.stats.duplicates += duplicates
        self.stats.file_breakdown["rules.json"] = {
            "total": len(data),
            "imported": imported,
            "duplicates": duplicates,
        }
        log.info("import.file.complete", file="rules.json", imported=imported,
                 total=len(data), duplicates=duplicates)
