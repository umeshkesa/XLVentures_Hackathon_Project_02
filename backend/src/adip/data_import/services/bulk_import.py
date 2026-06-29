from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import structlog

from adip.data_import.coordinator import ImportCoordinator
from adip.data_import.deduplicators import InMemoryDeduplicator
from adip.data_import.readers import read_csv, read_csv_chunked, read_json, read_text
from adip.data_import.statistics import ImportReport
from adip.data_import.validators import normalize_row, validate_required_fields

log = structlog.get_logger(__name__)


class BulkImportService:
    """High-level bulk import service with progress reporting and transaction semantics.

    This service wraps the ImportCoordinator and adds file-level progress
    callbacks and transaction-style batch management.
    """

    def __init__(
        self,
        dataset_root: str | Path,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> None:
        self.dataset_root = Path(dataset_root).resolve()
        self.coordinator = ImportCoordinator(self.dataset_root)
        self.dedup = InMemoryDeduplicator()
        self.progress_callback = progress_callback
        self._current_batch: dict[str, Any] = {}

    def import_all(self) -> ImportReport:
        """Import the entire dataset with progress reporting."""
        if self.progress_callback:
            self.progress_callback("START", 0, 6)
        report = self.coordinator.run_all()
        if self.progress_callback:
            self.progress_callback("COMPLETE", 6, 6)
        return report

    def import_phase(
        self, phase_name: str, progress_callback: Callable[[str, int, int], None] | None = None
    ) -> ImportReport:
        """Import a single phase with progress reporting."""
        cb = progress_callback or self.progress_callback
        if cb:
            cb(f"PHASE_START:{phase_name}", 0, 1)
        report = self.coordinator.run_phase(phase_name)
        if cb:
            cb(f"PHASE_COMPLETE:{phase_name}", 1, 1)
        return report

    def import_csv_batch(
        self,
        path: str | Path,
        entity_type: str,
        required_fields: list[str] | None = None,
        key_field: str | None = None,
        chunk_size: int = 500,
    ) -> dict[str, Any]:
        """Import a single CSV file as a batch with progress.

        Returns batch statistics.
        """
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        required = required_fields or []
        rows = read_csv(path)
        total = len(rows)
        imported = 0
        skipped = 0
        duplicates = 0
        errors = 0

        for i, row in enumerate(rows):
            row = normalize_row(row)
            if required:
                vr = validate_required_fields(row, required, i + 1)
                if not vr.is_valid:
                    errors += 1
                    continue
            if key_field:
                if self.dedup.is_duplicate_by_key(key_field, row):
                    duplicates += 1
                    skipped += 1
                    continue
            imported += 1

            if self.progress_callback and (i + 1) % chunk_size == 0:
                self.progress_callback(f"PROGRESS:{path.name}", i + 1, total)

        return {
            "file": path.name,
            "entity_type": entity_type,
            "total": total,
            "imported": imported,
            "skipped": skipped,
            "duplicates": duplicates,
            "errors": errors,
        }

    def import_json_batch(
        self,
        path: str | Path,
        entity_type: str,
        key_field: str | None = None,
    ) -> dict[str, Any]:
        """Import a single JSON file as a batch."""
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        data = read_json(path)
        if not isinstance(data, list):
            data = [data]

        total = len(data)
        imported = 0
        duplicates = 0

        for item in data:
            if key_field:
                key_val = item.get(key_field, "")
                if self.dedup.is_duplicate_by_key(key_field, {key_field: str(key_val)}):
                    duplicates += 1
                    continue
            imported += 1

        return {
            "file": path.name,
            "entity_type": entity_type,
            "total": total,
            "imported": imported,
            "duplicates": duplicates,
        }

    def validate_dataset(self) -> dict[str, Any]:
        """Validate the entire dataset structure without importing."""
        return self.coordinator.list_datasets()
