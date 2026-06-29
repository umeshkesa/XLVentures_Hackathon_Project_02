"""Validation tests for Memory Manager enums."""

from __future__ import annotations

from adip.memory.enums import MemoryOperation, MemoryTier, MemoryType, RetentionPolicy


class TestMemoryType:
    def test_values(self) -> None:
        assert MemoryType.SESSION.value == "SESSION"
        assert MemoryType.CONVERSATION.value == "CONVERSATION"
        assert MemoryType.WORKFLOW.value == "WORKFLOW"
        assert MemoryType.PLANNING.value == "PLANNING"
        assert MemoryType.RECOMMENDATION.value == "RECOMMENDATION"
        assert MemoryType.LEARNING.value == "LEARNING"
        assert MemoryType.USER.value == "USER"
        assert MemoryType.CACHE.value == "CACHE"

    def test_unique_values(self) -> None:
        values = [e.value for e in MemoryType]
        assert len(values) == len(set(values))

    def test_members_count(self) -> None:
        assert len(MemoryType) == 8


class TestMemoryTier:
    def test_values(self) -> None:
        assert MemoryTier.HOT.value == "HOT"
        assert MemoryTier.WARM.value == "WARM"
        assert MemoryTier.COLD.value == "COLD"

    def test_unique_values(self) -> None:
        values = [e.value for e in MemoryTier]
        assert len(values) == len(set(values))

    def test_members_count(self) -> None:
        assert len(MemoryTier) == 3


class TestMemoryOperation:
    def test_values(self) -> None:
        assert MemoryOperation.CREATE.value == "CREATE"
        assert MemoryOperation.READ.value == "READ"
        assert MemoryOperation.UPDATE.value == "UPDATE"
        assert MemoryOperation.DELETE.value == "DELETE"
        assert MemoryOperation.SEARCH.value == "SEARCH"
        assert MemoryOperation.ARCHIVE.value == "ARCHIVE"

    def test_unique_values(self) -> None:
        values = [e.value for e in MemoryOperation]
        assert len(values) == len(set(values))

    def test_members_count(self) -> None:
        assert len(MemoryOperation) == 6


class TestRetentionPolicy:
    def test_values(self) -> None:
        assert RetentionPolicy.TEMPORARY.value == "TEMPORARY"
        assert RetentionPolicy.SHORT_TERM.value == "SHORT_TERM"
        assert RetentionPolicy.LONG_TERM.value == "LONG_TERM"
        assert RetentionPolicy.PERMANENT.value == "PERMANENT"

    def test_unique_values(self) -> None:
        values = [e.value for e in RetentionPolicy]
        assert len(values) == len(set(values))

    def test_members_count(self) -> None:
        assert len(RetentionPolicy) == 4
