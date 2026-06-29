from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path
from typing import Any, Generator

from adip.utils.file_utils import safe_read, safe_read_bytes


def read_csv(path: str | Path, delimiter: str = ",") -> list[dict[str, str]]:
    """Read a CSV file and return a list of row-dicts."""
    content = safe_read(path)
    if content is None:
        raise FileNotFoundError(f"CSV file not found: {path}")
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    return [row for row in reader]


def read_csv_chunked(
    path: str | Path, chunk_size: int = 1000, delimiter: str = ","
) -> Generator[list[dict[str, str]], None, None]:
    """Yield rows from a CSV file in chunks."""
    content = safe_read(path)
    if content is None:
        raise FileNotFoundError(f"CSV file not found: {path}")
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    chunk: list[dict[str, str]] = []
    for row in reader:
        chunk.append(row)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def read_csv_sample(path: str | Path, n: int = 5, delimiter: str = ",") -> list[dict[str, str]]:
    """Read the first *n* rows of a CSV file."""
    content = safe_read(path)
    if content is None:
        raise FileNotFoundError(f"CSV file not found: {path}")
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    rows: list[dict[str, str]] = []
    for i, row in enumerate(reader):
        if i >= n:
            break
        rows.append(row)
    return rows


def read_json(path: str | Path) -> Any:
    """Read a JSON file and return the parsed data."""
    content = safe_read(path)
    if content is None:
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(content)


def read_text(path: str | Path) -> str:
    """Read a plain text file and return its content."""
    content = safe_read(path)
    if content is None:
        raise FileNotFoundError(f"Text file not found: {path}")
    return content


def read_zip_entry(zip_path: str | Path, entry_path: str) -> str | None:
    """Read a specific entry from a ZIP archive as text."""
    with zipfile.ZipFile(str(zip_path), "r") as zf:
        if entry_path not in zf.namelist():
            return None
        return zf.read(entry_path).decode("utf-8")


def list_zip_entries(zip_path: str | Path, suffix: str = "") -> list[str]:
    """List entries in a ZIP archive, optionally filtered by suffix."""
    with zipfile.ZipFile(str(zip_path), "r") as zf:
        names = zf.namelist()
    if suffix:
        names = [n for n in names if n.endswith(suffix)]
    return names


def detect_delimiter(path: str | Path, sample_size: int = 1024) -> str:
    """Auto-detect CSV delimiter (comma, semicolon, tab, pipe)."""
    content = safe_read(path)
    if content is None:
        return ","
    sample = content[:sample_size]
    dialect = csv.Sniffer().sniff(sample)
    return dialect.delimiter


def get_csv_stats(path: str | Path, delimiter: str = ",") -> dict[str, Any]:
    """Return basic stats about a CSV file: row count, column names, column count."""
    rows = read_csv(path, delimiter=delimiter)
    if not rows:
        return {"rows": 0, "columns": [], "column_count": 0}
    return {
        "rows": len(rows),
        "columns": list(rows[0].keys()),
        "column_count": len(rows[0].keys()),
    }
