from __future__ import annotations

import pytest

from adip.data_import.deduplicators import (
    DatabaseDeduplicator,
    InMemoryDeduplicator,
)


class TestInMemoryDeduplicator:
    def test_hash_dedup(self) -> None:
        dedup = InMemoryDeduplicator()
        row = {"id": "1", "name": "test"}
        hash_result = dedup.is_duplicate_by_hash(row)
        assert not hash_result
        assert dedup.is_duplicate_by_hash(row)

    def test_key_dedup(self) -> None:
        dedup = InMemoryDeduplicator()
        dedup.add_key_index("id")
        row = {"id": "1", "name": "test"}
        assert not dedup.is_duplicate_by_key("id", row)
        assert dedup.is_duplicate_by_key("id", row)

    def test_deduplicate_result_counts(self) -> None:
        dedup = InMemoryDeduplicator()
        rows = [
            {"id": "1", "name": "foo"},
            {"id": "2", "name": "bar"},
            {"id": "1", "name": "foo"},
        ]
        result = dedup.deduplicate(rows, key_fields=["id"])
        assert result.imported_count == 2
        assert result.duplicate_count == 1
        assert result.skipped_count == 0

    def test_reset(self) -> None:
        dedup = InMemoryDeduplicator()
        row = {"id": "1"}
        assert not dedup.is_duplicate_by_key("id", row)
        dedup.reset()
        assert not dedup.is_duplicate_by_key("id", row)


class TestDatabaseDeduplicator:
    def test_duplicate_detection(self) -> None:
        dedup = DatabaseDeduplicator()
        dedup.load_existing_keys("customer_id", {"CUS001", "CUS002"})
        assert dedup.is_duplicate("customer_id", "CUS001")
        assert not dedup.is_duplicate("customer_id", "CUS003")

    def test_new_keys_tracking(self) -> None:
        dedup = DatabaseDeduplicator()
        assert not dedup.is_duplicate("asset_id", "AST001")
        assert dedup.is_duplicate("asset_id", "AST001")
        new_keys = dedup.new_keys_since_last_check("asset_id")
        assert "AST001" in new_keys
        assert not dedup.is_duplicate("asset_id", "AST001")
