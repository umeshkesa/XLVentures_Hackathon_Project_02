from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import structlog

from adip.data_import.deduplicators import InMemoryDeduplicator
from adip.data_import.readers import read_csv, read_csv_chunked, read_json, read_text
from adip.data_import.statistics import ImportStats, ImportTimer
from adip.data_import.validators import ValidationResult, normalize_row

log = structlog.get_logger(__name__)


class BaseImporter(ABC):
    """Abstract base for all phase importers."""

    def __init__(self, dataset_root: str | Path, deduplicator: InMemoryDeduplicator | None = None):
        self.dataset_root = Path(dataset_root).resolve()
        self.dedup = deduplicator or InMemoryDeduplicator()
        self.stats = ImportStats()
        self.timer = ImportTimer()

    @property
    @abstractmethod
    def phase_name(self) -> str:
        ...

    @abstractmethod
    def run(self) -> ImportStats:
        ...

    def resolve_path(self, *parts: str) -> Path:
        return self.dataset_root.joinpath(*parts)

    def csv_path(self, relative: str) -> Path:
        return self.resolve_path(relative)

    def csv_rows(self, relative: str) -> list[dict[str, str]]:
        path = self.csv_path(relative)
        log.info("import.reading_csv", path=str(path))
        try:
            return read_csv(path)
        except FileNotFoundError:
            log.warning("import.file_not_found", path=str(path))
            return []

    def json_data(self, relative: str) -> Any:
        path = self.csv_path(relative)
        try:
            return read_json(path)
        except FileNotFoundError:
            log.warning("import.file_not_found", path=str(path))
            return None

    def text_content(self, relative: str) -> str:
        path = self.csv_path(relative)
        try:
            return read_text(path)
        except FileNotFoundError:
            log.warning("import.file_not_found", path=str(path))
            return ""

    def _import_csv_rows(
        self,
        relative: str,
        required_fields: list[str],
        key_fields: list[str] | None = None,
        use_hash_dedup: bool = True,
    ) -> tuple[list[dict[str, str]], ValidationResult, int, int]:
        """Read, validate, normalize, and deduplicate CSV rows.

        Returns (imported_rows, validation_result, duplicate_count, skip_count).
        """
        rows = self.csv_rows(relative)
        validation = ValidationResult()
        valid_rows: list[dict[str, str]] = []

        for i, row in enumerate(rows, start=1):
            row = normalize_row(row)
            vr = self._validate_row(row, required_fields, i)
            validation.merge(vr)
            if not vr.is_valid:
                continue
            valid_rows.append(row)

        dedup_result = self.dedup.deduplicate(
            valid_rows,
            key_fields=key_fields,
            use_hash=use_hash_dedup,
        )

        return (
            dedup_result.imported,
            validation,
            dedup_result.duplicate_count,
            dedup_result.skipped_count,
        )

    def _validate_row(
        self, row: dict[str, str], required: list[str], row_num: int
    ) -> ValidationResult:
        from adip.data_import.validators import validate_required_fields

        return validate_required_fields(row, required, row_num)
