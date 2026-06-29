"""Tests for RuleVersionManager."""

from __future__ import annotations

import pytest

from adip.rules.contracts.models import Rule
from adip.rules.execution.version_manager import RuleVersionManager


class TestRuleVersionManager:
    def test_create_version(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vr = vm.create_version(rule, created_by="admin", change_summary="Initial version")
        assert vr.version_number == 1
        assert vr.created_by == "admin"
        assert vr.change_summary == "Initial version"
        assert vr.active is True

    def test_create_version_increments(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        v1 = vm.create_version(rule, change_summary="v1")
        v2 = vm.create_version(rule, change_summary="v2")
        assert v1.version_number == 1
        assert v2.version_number == 2
        assert v1.active is False
        assert v2.active is True

    def test_get_version(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule, change_summary="v1")
        vm.create_version(rule, change_summary="v2")
        rule_id = str(rule.rule_id)
        v1 = vm.get_version(rule_id, 1)
        assert v1 is not None
        assert v1.version_number == 1
        v3 = vm.get_version(rule_id, 99)
        assert v3 is None

    def test_list_versions(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule, change_summary="v1")
        vm.create_version(rule, change_summary="v2")
        vm.create_version(rule, change_summary="v3")
        versions = vm.list_versions(str(rule.rule_id))
        assert len(versions) == 3
        assert [v.version_number for v in versions] == [1, 2, 3]

    def test_get_active_version(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule)
        vm.create_version(rule)
        active = vm.get_active_version(str(rule.rule_id))
        assert active is not None
        assert active.version_number == 2

    def test_mark_active(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule)
        vm.create_version(rule)
        rule_id = str(rule.rule_id)
        result = vm.mark_active(rule_id, 1)
        assert result is True
        active = vm.get_active_version(rule_id)
        assert active is not None
        assert active.version_number == 1

    def test_mark_active_not_found(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule)
        result = vm.mark_active(str(rule.rule_id), 99)
        assert result is False

    def test_compare_versions(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule, created_by="admin", change_summary="Initial")
        vm.create_version(rule, created_by="user-1", change_summary="Updated priority")
        comparison = vm.compare_versions(str(rule.rule_id), 1, 2)
        assert comparison["version_a"] == 1
        assert comparison["version_b"] == 2
        assert comparison["a_summary"] == "Initial"
        assert comparison["b_summary"] == "Updated priority"

    def test_compare_versions_missing(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule)
        with pytest.raises(ValueError, match="Version not found"):
            vm.compare_versions(str(rule.rule_id), 1, 99)

    def test_restore_version(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule, change_summary="v1")
        v2 = vm.create_version(rule, change_summary="v2")
        rule_id = str(rule.rule_id)
        restored = vm.restore_version(rule_id, 1)
        assert restored is not None
        assert restored.change_summary == "Restored from version 1"
        assert restored.active is True
        # v2 should no longer be active
        assert vm.get_version(rule_id, 2).active is False

    def test_restore_version_not_found(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        result = vm.restore_version(str(rule.rule_id), 99)
        assert result is None

    def test_clear(self) -> None:
        rule = Rule(name="Test")
        vm = RuleVersionManager()
        vm.create_version(rule)
        vm.clear()
        assert vm.list_versions(str(rule.rule_id)) == []
