from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImportStats:
    phase: str = ""
    total_records: int = 0
    imported: int = 0
    skipped: int = 0
    duplicates: int = 0
    validation_errors: int = 0
    execution_time_seconds: float = 0.0
    file_breakdown: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        if self.total_records == 0:
            return 1.0
        return self.imported / self.total_records

    def merge(self, other: ImportStats) -> None:
        self.total_records += other.total_records
        self.imported += other.imported
        self.skipped += other.skipped
        self.duplicates += other.duplicates
        self.validation_errors += other.validation_errors
        self.execution_time_seconds += other.execution_time_seconds
        for fname, breakdown in other.file_breakdown.items():
            self.file_breakdown[fname] = breakdown

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "total_records": self.total_records,
            "imported": self.imported,
            "skipped": self.skipped,
            "duplicates": self.duplicates,
            "validation_errors": self.validation_errors,
            "execution_time_seconds": round(self.execution_time_seconds, 3),
            "success_rate": round(self.success_rate, 4),
            "file_breakdown": self.file_breakdown,
        }

    def summary_line(self) -> str:
        return (
            f"[{self.phase}] {self.imported} imported, {self.skipped} skipped, "
            f"{self.duplicates} duplicates, {self.validation_errors} errors "
            f"in {self.execution_time_seconds:.2f}s "
            f"(rate: {self.success_rate:.1%})"
        )


class ImportTimer:
    def __init__(self) -> None:
        self._start: float | None = None
        self._elapsed: float = 0.0

    def start(self) -> None:
        self._start = time.perf_counter()

    def stop(self) -> float:
        if self._start is not None:
            self._elapsed = time.perf_counter() - self._start
            self._start = None
        return self._elapsed

    @property
    def elapsed(self) -> float:
        if self._start is not None:
            return time.perf_counter() - self._start
        return self._elapsed


class ImportReport:
    def __init__(self) -> None:
        self.session_id: str = ""
        self.phase_stats: dict[str, ImportStats] = {}
        self.global_stats = ImportStats(phase="GLOBAL")
        self.session_details: dict[str, Any] = {}
        self.timer = ImportTimer()

    def add_phase_stats(self, stats: ImportStats) -> None:
        self.phase_stats[stats.phase] = stats
        self.global_stats.merge(stats)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "execution_time_seconds": round(self.timer.elapsed, 3),
            "global": self.global_stats.to_dict(),
            "phases": {k: v.to_dict() for k, v in self.phase_stats.items()},
            "session_details": self.session_details,
        }

    def print_summary(self) -> str:
        lines = [
            "=" * 60,
            f"  Import Report — Session: {self.session_id}",
            "=" * 60,
            "",
        ]
        for phase_name in [
            "REFERENCE",
            "OPERATIONS",
            "BUSINESS_RULES",
            "KNOWLEDGE",
            "TIME_SERIES",
            "SCENARIOS",
        ]:
            stats = self.phase_stats.get(phase_name)
            if stats:
                lines.append(f"  {stats.summary_line()}")
        lines.extend([
            "",
            f"  TOTAL: {self.global_stats.summary_line()}",
            "=" * 60,
        ])
        return "\n".join(lines)
