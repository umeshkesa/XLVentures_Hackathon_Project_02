from __future__ import annotations

from pathlib import Path

import pytest

from adip.data_import.services.bulk_import import BulkImportService


@pytest.fixture
def dataset_path(tmp_path: Path) -> Path:
    from tests.data_import.test_importers import _create_mini_dataset

    return _create_mini_dataset(tmp_path)


class TestBulkImportService:
    def test_import_all(self, dataset_path: Path) -> None:
        service = BulkImportService(dataset_path)
        report = service.import_all()
        assert report.session_id
        assert report.global_stats.imported > 0

    def test_import_phase(self, dataset_path: Path) -> None:
        service = BulkImportService(dataset_path)
        report = service.import_phase("REFERENCE")
        assert "REFERENCE" in report.phase_stats

    def test_progress_callback(self, dataset_path: Path) -> None:
        events: list[str] = []
        service = BulkImportService(dataset_path, progress_callback=lambda s, c, t: events.append(s))
        service.import_all()
        assert "START" in events
        assert "COMPLETE" in events

    def test_validate_dataset(self, dataset_path: Path) -> None:
        service = BulkImportService(dataset_path)
        result = service.validate_dataset()
        assert result["all_found"]

    def test_import_csv_batch(self, dataset_path: Path) -> None:
        service = BulkImportService(dataset_path)
        csv_path = dataset_path / "customer_profiles" / "customers.csv"
        result = service.import_csv_batch(
            csv_path,
            entity_type="customer",
            required_fields=["customer_id", "company_name"],
            key_field="customer_id",
        )
        assert result["total"] == 1
        assert result["imported"] == 1

    def test_import_csv_batch_not_found(self) -> None:
        service = BulkImportService("/nonexistent")
        with pytest.raises(FileNotFoundError):
            service.import_csv_batch("/nonexistent/file.csv", "test")

    def test_import_json_batch(self, dataset_path: Path) -> None:
        service = BulkImportService(dataset_path)
        json_path = dataset_path / "business" / "business_rules" / "rules.json"
        result = service.import_json_batch(json_path, entity_type="rule", key_field="rule_id")
        assert result["total"] == 1
        assert result["imported"] == 1
