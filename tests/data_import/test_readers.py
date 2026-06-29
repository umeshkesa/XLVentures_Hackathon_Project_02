from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from adip.data_import.readers import (
    get_csv_stats,
    read_csv,
    read_csv_chunked,
    read_json,
    read_text,
)


@pytest.fixture
def sample_csv() -> str:
    return "id,name,value\n1,foo,100\n2,bar,200\n"


@pytest.fixture
def sample_csv_path(sample_csv: str) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write(sample_csv)
        return Path(f.name)


@pytest.fixture
def sample_json_path() -> Path:
    data = [{"id": "RULE001", "category": "Safety"}, {"id": "RULE002", "category": "Ops"}]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(data, f)
        return Path(f.name)


@pytest.fixture
def sample_text_path() -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write("Hello, world!")
        return Path(f.name)


class TestReaders:
    def test_read_csv(self, sample_csv_path: Path) -> None:
        rows = read_csv(sample_csv_path)
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[1]["name"] == "bar"

    def test_read_csv_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            read_csv("/nonexistent/file.csv")

    def test_read_csv_chunked(self, sample_csv_path: Path) -> None:
        chunks = list(read_csv_chunked(sample_csv_path, chunk_size=1))
        assert len(chunks) == 2
        assert chunks[0][0]["id"] == "1"
        assert chunks[1][0]["name"] == "bar"

    def test_get_csv_stats(self, sample_csv_path: Path) -> None:
        stats = get_csv_stats(sample_csv_path)
        assert stats["rows"] == 2
        assert stats["columns"] == ["id", "name", "value"]
        assert stats["column_count"] == 3

    def test_read_json(self, sample_json_path: Path) -> None:
        data = read_json(sample_json_path)
        assert len(data) == 2
        assert data[0]["id"] == "RULE001"

    def test_read_json_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            read_json("/nonexistent/file.json")

    def test_read_text(self, sample_text_path: Path) -> None:
        content = read_text(sample_text_path)
        assert content == "Hello, world!"

    def test_read_text_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            read_text("/nonexistent/file.txt")
