from __future__ import annotations

from pathlib import Path

import pytest

from adip.data_import.coordinator import ImportCoordinator


@pytest.fixture
def dataset_path(tmp_path: Path) -> Path:
    from tests.data_import.test_importers import _create_mini_dataset

    return _create_mini_dataset(tmp_path)


class TestImportCoordinator:
    def test_list_datasets(self, dataset_path: Path) -> None:
        coordinator = ImportCoordinator(dataset_path)
        result = coordinator.list_datasets()
        assert "phases" in result
        assert "REFERENCE" in result["phases"]
        assert "OPERATIONS" in result["phases"]
        assert result["all_found"]

    def test_run_all_phases(self, dataset_path: Path) -> None:
        coordinator = ImportCoordinator(dataset_path)
        report = coordinator.run_all()
        assert report.session_id
        assert len(report.phase_stats) == 6
        assert report.global_stats.total_records > 0
        assert report.global_stats.imported > 0

    def test_run_single_phase(self, dataset_path: Path) -> None:
        coordinator = ImportCoordinator(dataset_path)
        report = coordinator.run_phase("REFERENCE")
        assert "REFERENCE" in report.phase_stats
        assert report.phase_stats["REFERENCE"].imported >= 4

    def test_run_invalid_phase(self, dataset_path: Path) -> None:
        coordinator = ImportCoordinator(dataset_path)
        with pytest.raises(ValueError):
            coordinator.run_phase("INVALID")

    def test_report_print_summary(self, dataset_path: Path) -> None:
        coordinator = ImportCoordinator(dataset_path)
        report = coordinator.run_all()
        summary = report.print_summary()
        assert "Import Report" in summary
        assert "GLOBAL" in summary
        assert report.global_stats.imported > 0

    def test_report_to_dict(self, dataset_path: Path) -> None:
        coordinator = ImportCoordinator(dataset_path)
        report = coordinator.run_phase("REFERENCE")
        d = report.to_dict()
        assert "session_id" in d
        assert "phases" in d
        assert "global" in d
