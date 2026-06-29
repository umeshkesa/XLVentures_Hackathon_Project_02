from __future__ import annotations

from adip.data_import.statistics import ImportReport, ImportStats, ImportTimer


class TestImportStats:
    def test_stats_initialization(self) -> None:
        stats = ImportStats(phase="TEST")
        assert stats.phase == "TEST"
        assert stats.total_records == 0
        assert stats.imported == 0

    def test_success_rate(self) -> None:
        stats = ImportStats(phase="TEST", total_records=100, imported=80)
        assert stats.success_rate == 0.8

    def test_success_rate_empty(self) -> None:
        stats = ImportStats()
        assert stats.success_rate == 1.0

    def test_merge(self) -> None:
        a = ImportStats(phase="A", total_records=10, imported=8, skipped=1, duplicates=1, validation_errors=0)
        b = ImportStats(phase="B", total_records=20, imported=15, skipped=2, duplicates=2, validation_errors=1)
        a.merge(b)
        assert a.total_records == 30
        assert a.imported == 23
        assert a.skipped == 3
        assert a.duplicates == 3
        assert a.validation_errors == 1

    def test_to_dict(self) -> None:
        stats = ImportStats(phase="TEST", total_records=10, imported=8)
        d = stats.to_dict()
        assert d["phase"] == "TEST"
        assert d["imported"] == 8

    def test_summary_line(self) -> None:
        stats = ImportStats(phase="TEST", total_records=10, imported=8)
        stats.execution_time_seconds = 5.5
        line = stats.summary_line()
        assert "TEST" in line
        assert "8 imported" in line
        assert "5.50s" in line


class TestImportTimer:
    def test_timer(self) -> None:
        timer = ImportTimer()
        timer.start()
        import time
        time.sleep(0.01)
        elapsed = timer.stop()
        assert elapsed >= 0.01
        assert timer.elapsed == elapsed

    def test_elapsed_without_start(self) -> None:
        timer = ImportTimer()
        assert timer.elapsed == 0.0


class TestImportReport:
    def test_report_initialization(self) -> None:
        report = ImportReport()
        assert report.global_stats.phase == "GLOBAL"

    def test_add_phase_stats(self) -> None:
        report = ImportReport()
        stats = ImportStats(phase="REFERENCE", total_records=10, imported=8)
        report.add_phase_stats(stats)
        assert "REFERENCE" in report.phase_stats
        assert report.global_stats.imported == 8

    def test_multiple_phases(self) -> None:
        report = ImportReport()
        report.add_phase_stats(ImportStats(phase="A", total_records=10, imported=8))
        report.add_phase_stats(ImportStats(phase="B", total_records=20, imported=18))
        assert report.global_stats.total_records == 30
        assert report.global_stats.imported == 26

    def test_to_dict(self) -> None:
        report = ImportReport()
        report.session_id = "test-123"
        report.add_phase_stats(ImportStats(phase="T", total_records=5, imported=5))
        d = report.to_dict()
        assert d["session_id"] == "test-123"
        assert "phases" in d
        assert "global" in d
