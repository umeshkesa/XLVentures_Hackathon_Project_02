from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import structlog

from adip.data_import.coordinator import ImportCoordinator

log = structlog.get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adip-import",
        description="ADIP Dataset Import Pipeline — seed PostgreSQL with the complete dataset.",
    )
    parser.add_argument(
        "dataset_root",
        type=str,
        help="Path to the ADIP_Dataset root directory",
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=[
            "REFERENCE",
            "OPERATIONS",
            "BUSINESS_RULES",
            "KNOWLEDGE",
            "TIME_SERIES",
            "SCENARIOS",
        ],
        help="Run only a single phase instead of all phases",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List discoverable dataset files and exit",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report what would be imported without importing",
    )
    return parser


def run_import_cli(argv: list[str] | None = None) -> int:
    """CLI entry point for the ADIP dataset importer."""
    parser = create_parser()
    args = parser.parse_args(argv)

    dataset_root = Path(args.dataset_root).resolve()
    if not dataset_root.is_dir():
        print(f"Error: dataset root not found: {dataset_root}", file=sys.stderr)
        return 1

    coordinator = ImportCoordinator(dataset_root)

    if args.list:
        datasets = coordinator.list_datasets()
        if args.format == "json":
            print(json.dumps(datasets, indent=2))
        else:
            _print_datasets(datasets)
        return 0

    if args.dry_run:
        datasets = coordinator.list_datasets()
        print("DRY RUN - no data will be imported")
        _print_datasets(datasets)
        return 0

    if args.phase:
        print(f"Running single phase: {args.phase}")
        report = coordinator.run_phase(args.phase)
    else:
        print("Running full import pipeline (all 6 phases)...")
        report = coordinator.run_all()

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.print_summary())

    return 0


def _print_datasets(datasets: dict) -> None:
    print(f"\nDataset root: {datasets['dataset_root']}\n")
    for phase_name, phase_data in datasets["phases"].items():
        status = "OK" if not phase_data["missing"] else "MISSING"
        print(f"  [{status}] {phase_name}")
        for f in phase_data["found"]:
            print(f"       + {f}")
        for f in phase_data["missing"]:
            print(f"       - {f} (missing)")
    print(
        f"\nAll datasets available: {datasets['all_found']}\n"
    )


if __name__ == "__main__":
    sys.exit(run_import_cli())
