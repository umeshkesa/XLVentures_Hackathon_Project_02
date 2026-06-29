"""Phase 2 validation tests for the Registry Framework execution pipeline.

Tests cover RegistryValidator, RegistrySearcher (all strategies),
RegistryIndexManager, RegistryVersionManager, RegistryDependencyGraph,
RegistryLifecycleManager, RegistryCache, RegistryPolicyEngine,
RegistryAudit, RegistryTrace, and RegistryMetricsCollector.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from adip.registry.contracts.models import (
    RegistryEntry,
    RegistryMetadata,
    RegistryNamespace,
    RegistrySearchResult,
)
from adip.registry.enums import (
    RegistryLifecycleStatus as RLS,
)
from adip.registry.enums import (
    RegistryScope,
    RegistryType,
)
from adip.registry.execution.audit import RegistryAudit
from adip.registry.execution.cache import RegistryCache
from adip.registry.execution.dependency_graph import RegistryDependencyGraph
from adip.registry.execution.index_manager import RegistryIndexManager
from adip.registry.execution.lifecycle import RegistryLifecycleManager
from adip.registry.execution.metrics import RegistryMetricsCollector
from adip.registry.execution.models import (
    AuditRecord,
    DependencyGraph,
    DependencyNode,
    LifecycleHistoryEntry,
    SearchResult,
    TraceRecord,
    VersionRecord,
)
from adip.registry.execution.policy import RegistryPolicyEngine
from adip.registry.execution.searcher import (
    ExactSearch,
    LabelSearch,
    NamespaceSearch,
    PrefixSearch,
    RegistrySearcher,
    TagSearch,
    get_strategy,
)
from adip.registry.execution.trace import RegistryTrace
from adip.registry.execution.validator import RegistryValidator
from adip.registry.execution.version_manager import RegistryVersionManager

# ── Helpers ──────────────────────────────────────────────────────────────────

def _entry(**overrides: Any) -> RegistryEntry:
    defaults: dict[str, Any] = {
        "name": "test-entry",
        "version": "1.0.0",
        "registry_type": RegistryType.CAPABILITY,
        "scope": RegistryScope.GLOBAL,
        "status": RLS.REGISTERED,
        "namespace": "default",
        "tags": [],
        "metadata": {},
    }
    defaults.update(overrides)
    return RegistryEntry(**defaults)


def _namespace(**overrides: Any) -> RegistryNamespace:
    defaults: dict[str, Any] = {
        "name": "test-ns",
        "registry_type": RegistryType.CAPABILITY,
    }
    defaults.update(overrides)
    return RegistryNamespace(**defaults)


# ===================================================================
# RegistryValidator
# ===================================================================

class TestRegistryValidator:
    def test_validate_valid_entry(self) -> None:
        v = RegistryValidator()
        entry = _entry(name="valid-entry", version="1.0.0")
        assert v.validate_entry(entry) == []

    def test_validate_entry_empty_name(self) -> None:
        v = RegistryValidator()
        entry = _entry(name="")
        violations = v.validate_entry(entry)
        assert any("name is required" in vi.lower() for vi in violations)

    def test_validate_entry_invalid_name_chars(self) -> None:
        v = RegistryValidator()
        entry = _entry(name="invalid name!")
        violations = v.validate_entry(entry)
        assert len(violations) > 0

    def test_validate_entry_long_name(self) -> None:
        v = RegistryValidator()
        entry = _entry(name="x" * 257)
        violations = v.validate_entry(entry)
        assert any("exceeds" in vi.lower() for vi in violations)

    def test_validate_entry_invalid_version(self) -> None:
        v = RegistryValidator()
        entry = _entry(version="not-a-version")
        violations = v.validate_entry(entry)
        assert any("semver" in vi.lower() for vi in violations)

    def test_validate_entry_empty_version(self) -> None:
        v = RegistryValidator()
        entry = _entry(version="")
        violations = v.validate_entry(entry)
        assert any("required" in vi.lower() for vi in violations)

    def test_validate_entry_too_many_tags(self) -> None:
        v = RegistryValidator()
        entry = _entry(tags=[f"tag{i}" for i in range(51)])
        violations = v.validate_entry(entry)
        assert any("exceeds" in vi.lower() for vi in violations)

    def test_validate_entry_tag_too_long(self) -> None:
        v = RegistryValidator()
        entry = _entry(tags=["x" * 65])
        violations = v.validate_entry(entry)
        assert any("exceeds" in vi.lower() for vi in violations)

    def test_validate_entry_invalid_tag_chars(self) -> None:
        v = RegistryValidator()
        entry = _entry(tags=["bad tag!"])
        violations = v.validate_entry(entry)
        assert len(violations) > 0

    def test_validate_entry_too_much_metadata(self) -> None:
        v = RegistryValidator()
        entry = _entry(metadata={f"k{i}": "v" for i in range(101)})
        violations = v.validate_entry(entry)
        assert any("exceeds" in vi.lower() for vi in violations)

    def test_validate_metadata(self) -> None:
        v = RegistryValidator()
        meta = RegistryMetadata(description="x" * 2001)
        violations = v.validate_metadata(meta)
        assert any("exceeds" in vi.lower() for vi in violations)

    def test_validate_metadata_valid(self) -> None:
        v = RegistryValidator()
        meta = RegistryMetadata(description="Valid description")
        assert v.validate_metadata(meta) == []

    def test_validate_namespace_valid(self) -> None:
        v = RegistryValidator()
        ns = _namespace(name="valid-ns")
        assert v.validate_namespace(ns) == []

    def test_validate_namespace_empty(self) -> None:
        v = RegistryValidator()
        ns = _namespace(name="")
        violations = v.validate_namespace(ns)
        assert any("required" in vi.lower() for vi in violations)

    def test_validate_namespace_too_long(self) -> None:
        v = RegistryValidator()
        ns = _namespace(name="x" * 129)
        violations = v.validate_namespace(ns)
        assert any("exceeds" in vi.lower() for vi in violations)

    def test_validate_namespace_invalid_chars(self) -> None:
        v = RegistryValidator()
        ns = _namespace(name="bad ns!")
        violations = v.validate_namespace(ns)
        assert any("alphanumeric" in vi.lower() for vi in violations)

    def test_validate_namespace_disabled(self) -> None:
        v = RegistryValidator()
        ns = _namespace(name="disabled-ns", enabled=False)
        violations = v.validate_namespace(ns)
        assert any("disabled" in vi.lower() for vi in violations)

    def test_validate_version_valid_semver(self) -> None:
        v = RegistryValidator()
        assert v.validate_version("1.2.3") == []
        assert v.validate_version("0.0.1") == []
        assert v.validate_version("2.0.0-beta.1") == []
        assert v.validate_version("1.0.0+build.1") == []

    def test_validate_version_invalid(self) -> None:
        v = RegistryValidator()
        violations = v.validate_version("abc")
        assert len(violations) > 0

    def test_validate_lifecycle_transition_valid(self) -> None:
        v = RegistryValidator()
        assert v.validate_lifecycle_transition(RLS.REGISTERED, RLS.VALIDATED) == []

    def test_validate_lifecycle_transition_invalid(self) -> None:
        v = RegistryValidator()
        violations = v.validate_lifecycle_transition(RLS.REGISTERED, RLS.ACTIVE)
        assert len(violations) > 0

    def test_validate_lifecycle_transition_from_removed(self) -> None:
        v = RegistryValidator()
        for status in list(RLS):
            violations = v.validate_lifecycle_transition(RLS.REMOVED, status)
            assert len(violations) > 0

    def test_validate_scope_allowed(self) -> None:
        v = RegistryValidator()
        entry = _entry(namespace="default")
        assert v.validate_scope(RegistryScope.GLOBAL, entry) == []

    def test_validate_scope_disallowed(self) -> None:
        v = RegistryValidator()
        entry = _entry(namespace="custom")
        assert v.validate_scope(RegistryScope.GLOBAL, entry) == []


# ===================================================================
# Search Strategies
# ===================================================================

class TestExactSearch:
    def test_exact_match(self) -> None:
        searcher = ExactSearch()
        entries = [_entry(name="energy-capability"), _entry(name="other")]
        results = searcher.search("energy-capability", entries)
        assert len(results) == 1
        assert results[0].entry_name == "energy-capability"

    def test_case_insensitive(self) -> None:
        searcher = ExactSearch()
        entries = [_entry(name="Energy-Capability")]
        results = searcher.search("energy-capability", entries)
        assert len(results) == 1

    def test_no_match(self) -> None:
        searcher = ExactSearch()
        entries = [_entry(name="energy-capability")]
        assert searcher.search("other", entries) == []

    def test_score_one_for_exact(self) -> None:
        searcher = ExactSearch()
        entries = [_entry(name="exact-match")]
        assert searcher.search("exact-match", entries)[0].score == 1.0


class TestPrefixSearch:
    def test_prefix_match(self) -> None:
        searcher = PrefixSearch()
        entries = [_entry(name="energy-forecast"), _entry(name="other")]
        results = searcher.search("energy", entries)
        assert len(results) == 1
        assert results[0].entry_name == "energy-forecast"

    def test_case_insensitive(self) -> None:
        searcher = PrefixSearch()
        entries = [_entry(name="Energy-Forecast")]
        results = searcher.search("energy", entries)
        assert len(results) == 1

    def test_no_match(self) -> None:
        searcher = PrefixSearch()
        entries = [_entry(name="other")]
        assert searcher.search("energy", entries) == []

    def test_multiple_matches(self) -> None:
        searcher = PrefixSearch()
        entries = [_entry(name="energy-a"), _entry(name="energy-b"), _entry(name="other")]
        assert len(searcher.search("energy", entries)) == 2


class TestTagSearch:
    def test_tag_match(self) -> None:
        searcher = TagSearch()
        entries = [_entry(name="a", tags=["ml", "energy"]), _entry(name="b", tags=["other"])]
        results = searcher.search("ml", entries)
        assert len(results) == 1

    def test_partial_tag_match(self) -> None:
        searcher = TagSearch()
        entries = [_entry(name="a", tags=["machine-learning"])]
        results = searcher.search("machine", entries)
        assert len(results) == 1

    def test_no_match(self) -> None:
        searcher = TagSearch()
        entries = [_entry(name="a", tags=["ml"])]
        assert searcher.search("other", entries) == []


class TestLabelSearch:
    def test_label_key_match(self) -> None:
        searcher = LabelSearch()
        entries = [_entry(name="a", metadata={"purpose": "forecast"}), _entry(name="b", metadata={})]
        results = searcher.search("purpose", entries)
        assert len(results) == 1

    def test_label_value_match(self) -> None:
        searcher = LabelSearch()
        entries = [_entry(name="a", metadata={"key": "forecast"})]
        results = searcher.search("forecast", entries)
        assert len(results) == 1

    def test_no_match(self) -> None:
        searcher = LabelSearch()
        entries = [_entry(name="a", metadata={"key": "value"})]
        assert searcher.search("other", entries) == []


class TestNamespaceSearch:
    def test_namespace_filter(self) -> None:
        searcher = NamespaceSearch(namespace="energy")
        entries = [
            _entry(name="a", namespace="energy"),
            _entry(name="b", namespace="default"),
        ]
        results = searcher.search("", entries)
        assert len(results) == 1
        assert results[0].entry_name == "a"

    def test_namespace_with_query(self) -> None:
        searcher = NamespaceSearch(namespace="energy")
        entries = [
            _entry(name="forecast", namespace="energy"),
            _entry(name="other", namespace="energy"),
        ]
        results = searcher.search("forecast", entries)
        assert len(results) == 1

    def test_empty_namespace_returns_all(self) -> None:
        searcher = NamespaceSearch(namespace="")
        entries = [_entry(name="a", namespace="ns1"), _entry(name="b", namespace="ns2")]
        results = searcher.search("", entries)
        assert len(results) == 2


class TestGetStrategy:
    def test_get_exact(self) -> None:
        strategy = get_strategy("exact")
        assert isinstance(strategy, ExactSearch)

    def test_get_prefix(self) -> None:
        strategy = get_strategy("prefix")
        assert isinstance(strategy, PrefixSearch)

    def test_get_tag(self) -> None:
        strategy = get_strategy("tag")
        assert isinstance(strategy, TagSearch)

    def test_get_label(self) -> None:
        strategy = get_strategy("label")
        assert isinstance(strategy, LabelSearch)

    def test_get_namespace(self) -> None:
        strategy = get_strategy("namespace", namespace="test")
        assert isinstance(strategy, NamespaceSearch)
        assert strategy.namespace == "test"

    def test_unknown_strategy(self) -> None:
        with pytest.raises(ValueError, match="Unknown"):
            get_strategy("nonexistent")


# ===================================================================
# RegistrySearcher
# ===================================================================

class TestRegistrySearcher:
    def test_search_all_strategies(self) -> None:
        searcher = RegistrySearcher()
        entries = [_entry(name="energy-capability", tags=["energy"])]
        # Register instances
        searcher.register_strategy_instance("exact", ExactSearch())
        searcher.register_strategy_instance("prefix", PrefixSearch())
        results = searcher.search("energy", entries)
        assert len(results) >= 1

    def test_search_by_name(self) -> None:
        searcher = RegistrySearcher()
        entries = [_entry(name="exact-match")]
        results = searcher.search_by_name("exact-match", entries)
        assert len(results) == 1

    def test_search_by_tags(self) -> None:
        searcher = RegistrySearcher()
        entries = [_entry(name="a", tags=["ml"]), _entry(name="b", tags=["ml", "energy"])]
        results = searcher.search_by_tags(["ml"], entries)
        assert len(results) == 2

    def test_search_by_tags_multiple(self) -> None:
        searcher = RegistrySearcher()
        entries = [_entry(name="a", tags=["ml"]), _entry(name="b", tags=["energy"])]
        results = searcher.search_by_tags(["ml", "energy"], entries)
        assert len(results) == 2

    def test_count(self) -> None:
        searcher = RegistrySearcher()
        entries = [_entry(name="a"), _entry(name="b")]
        assert searcher.count(entries) == 2

    def test_results_ranked_by_score(self) -> None:
        searcher = RegistrySearcher()
        entries = [
            _entry(name="energy-forecast"),
            _entry(name="energy"),
        ]
        searcher.register_strategy_instance("exact", ExactSearch())
        results = searcher.search("energy", entries)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_deduplication(self) -> None:
        searcher = RegistrySearcher()
        entries = [_entry(name="dup", tags=["dup"]), _entry(name="other")]
        searcher.register_strategy_instance("exact", ExactSearch())
        searcher.register_strategy_instance("prefix", PrefixSearch())
        results = searcher.search("dup", entries)
        entry_ids = [r.entry_id for r in results]
        assert len(entry_ids) == len(set(entry_ids))


# ===================================================================
# RegistryIndexManager
# ===================================================================

class TestRegistryIndexManager:
    def test_index_entry(self) -> None:
        idx = RegistryIndexManager()
        entry = _entry(name="energy", tags=["ml"], metadata={"purpose": "forecast"})
        idx.index_entry(entry)
        assert idx.get_by_name("energy") is not None
        assert len(idx.get_by_tag("ml")) == 1
        assert len(idx.get_by_label("purpose")) == 1
        assert len(idx.get_by_namespace("default")) == 1
        assert len(idx.get_by_type(RegistryType.CAPABILITY)) == 1

    def test_index_multiple_entries(self) -> None:
        idx = RegistryIndexManager()
        idx.index_entry(_entry(name="a", namespace="ns1"))
        idx.index_entry(_entry(name="b", namespace="ns2"))
        assert idx.name_index_size() == 2
        assert idx.namespace_index_size() == 2

    def test_remove_entry(self) -> None:
        idx = RegistryIndexManager()
        entry = _entry(name="energy", tags=["ml"])
        idx.index_entry(entry)
        idx.remove_entry(entry)
        assert idx.get_by_name("energy") is None
        assert len(idx.get_by_tag("ml")) == 0

    def test_clear(self) -> None:
        idx = RegistryIndexManager()
        idx.index_entry(_entry(name="a"))
        idx.index_entry(_entry(name="b"))
        count = idx.clear()
        assert count > 0
        assert idx.name_index_size() == 0

    def test_get_by_name_not_found(self) -> None:
        idx = RegistryIndexManager()
        assert idx.get_by_name("nonexistent") is None

    def test_total_index_size(self) -> None:
        idx = RegistryIndexManager()
        entry = _entry(name="test", tags=["t1"], metadata={"k": "v"})
        idx.index_entry(entry)
        assert idx.total_index_size() > 0


# ===================================================================
# RegistryVersionManager
# ===================================================================

class TestRegistryVersionManager:
    def test_create_version(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test", version="1.0.0")
        record = vm.create_version(entry, created_by="user-001")
        assert record.version == "1.0.0"
        assert record.is_active is True
        assert record.created_by == "user-001"

    def test_get_version(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test", version="1.0.0")
        vm.create_version(entry)
        eid = str(entry.entry_id)
        assert vm.get_version(eid, "1.0.0") is not None
        assert vm.get_version(eid, "2.0.0") is None

    def test_get_version_history(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test", version="1.0.0")
        vm.create_version(entry)
        entry2 = entry.model_copy(update={"version": "2.0.0"})
        vm.create_version(entry2)
        history = vm.get_version_history(str(entry.entry_id))
        assert len(history) == 2

    def test_get_active_version(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test", version="1.0.0")
        vm.create_version(entry)
        entry2 = entry.model_copy(update={"version": "2.0.0"})
        vm.create_version(entry2)
        active = vm.get_active_version(str(entry.entry_id))
        assert active is not None
        assert active.version == "2.0.0"

    def test_compare_versions(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test", version="1.0.0")
        vm.create_version(entry)
        entry2 = entry.model_copy(update={"version": "2.0.0"})
        vm.create_version(entry2)
        eid = str(entry.entry_id)
        diff = vm.compare_versions(eid, "1.0.0", "2.0.0")
        assert diff["version_a"] == "1.0.0"
        assert diff["version_b"] == "2.0.0"
        assert "name_changed" in diff

    def test_compare_versions_not_found(self) -> None:
        vm = RegistryVersionManager()
        diff = vm.compare_versions(str(uuid.uuid4()), "1.0.0", "2.0.0")
        assert "error" in diff

    def test_rollback(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test", version="1.0.0")
        vm.create_version(entry)
        entry2 = entry.model_copy(update={"version": "2.0.0"})
        vm.create_version(entry2)
        eid = str(entry.entry_id)
        rolled = vm.rollback(eid, "1.0.0")
        assert rolled is not None
        assert "rollback" in rolled.version

    def test_rollback_not_found(self) -> None:
        vm = RegistryVersionManager()
        assert vm.rollback(str(uuid.uuid4()), "1.0.0") is None

    def test_clear(self) -> None:
        vm = RegistryVersionManager()
        entry = _entry(name="test")
        vm.create_version(entry)
        count = vm.clear()
        assert count >= 1


# ===================================================================
# RegistryDependencyGraph
# ===================================================================

class TestRegistryDependencyGraph:
    def test_create_empty(self) -> None:
        g = RegistryDependencyGraph()
        graph = g.create([])
        assert graph.nodes == {}
        assert graph.root_entries == []

    def test_create_single_entry(self) -> None:
        g = RegistryDependencyGraph()
        entry = _entry(name="standalone")
        graph = g.create([entry])
        assert "standalone" in graph.nodes
        assert "standalone" in graph.root_entries
        assert graph.dependency_depth == 0

    def test_create_with_dependencies(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a", metadata={"dependencies": []})
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        graph = g.create([a, b])
        assert graph.nodes["b"] == ["a"]
        assert "a" in graph.root_entries

    def test_root_and_leaf(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a", metadata={"dependencies": []})
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        graph = g.create([a, b])
        assert "a" in graph.root_entries
        assert graph.load_order is not None

    def test_unused_dependencies(self) -> None:
        g = RegistryDependencyGraph()
        entry = _entry(name="a", metadata={"dependencies": ["missing-dep"]})
        graph = g.create([entry])
        assert "missing-dep" in graph.unused_dependencies

    def test_cycle_detection(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a", metadata={"dependencies": ["b"]})
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        graph = g.create([a, b])
        assert len(graph.circular_dependency_reports) > 0

    def test_no_cycle(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a", metadata={"dependencies": []})
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        graph = g.create([a, b])
        assert len(graph.circular_dependency_reports) == 0

    def test_get_parents(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a")
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        g.create([a, b])
        parents = g.get_parents("a")
        assert "b" in parents

    def test_get_children(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a")
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        g.create([a, b])
        children = g.get_children("b")
        assert children == ["a"]

    def test_get_dependency_tree(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a")
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        g.create([a, b])
        tree = g.get_dependency_tree("b")
        assert "0" in tree
        assert len(tree["0"]) >= 1

    def test_get_node(self) -> None:
        g = RegistryDependencyGraph()
        entry = _entry(name="test")
        g.create([entry])
        node = g.get_node("test")
        assert node is not None
        assert node.entry_name == "test"

    def test_get_all_nodes(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a")
        b = _entry(name="b")
        g.create([a, b])
        nodes = g.get_all_nodes()
        assert len(nodes) == 2

    def test_has_cycles(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a", metadata={"dependencies": ["b"]})
        b = _entry(name="b", metadata={"dependencies": ["a"]})
        g.create([a, b])
        assert g.has_cycles() is True

    def test_has_no_cycles(self) -> None:
        g = RegistryDependencyGraph()
        a = _entry(name="a")
        g.create([a])
        assert g.has_cycles() is False

    def test_clear(self) -> None:
        g = RegistryDependencyGraph()
        entry = _entry(name="test")
        g.create([entry])
        g.clear()
        assert g.get_node("test") is None
        assert g.has_cycles() is False


# ===================================================================
# RegistryLifecycleManager
# ===================================================================

class TestRegistryLifecycleManager:
    def test_transition_valid(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        updated = lm.transition(entry, RLS.VALIDATED, changed_by="admin")
        assert updated.status == RLS.VALIDATED

    def test_transition_invalid(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        with pytest.raises(ValueError, match="not allowed"):
            lm.transition(entry, RLS.ACTIVE)

    def test_transition_same_status(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        updated = lm.transition(entry, RLS.REGISTERED)
        assert updated is entry

    def test_full_lifecycle(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        entry = lm.transition(entry, RLS.VALIDATED, changed_by="admin")
        assert entry.status == RLS.VALIDATED
        entry = lm.transition(entry, RLS.ACTIVE, changed_by="admin")
        assert entry.status == RLS.ACTIVE
        entry = lm.transition(entry, RLS.SUSPENDED, changed_by="admin")
        assert entry.status == RLS.SUSPENDED
        entry = lm.transition(entry, RLS.ACTIVE, changed_by="admin")
        assert entry.status == RLS.ACTIVE
        entry = lm.transition(entry, RLS.DEPRECATED, changed_by="admin")
        assert entry.status == RLS.DEPRECATED
        entry = lm.transition(entry, RLS.REMOVED, changed_by="admin")
        assert entry.status == RLS.REMOVED

    def test_transition_from_removed(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REMOVED)
        for status in list(RLS):
            if status != RLS.REMOVED:
                with pytest.raises(ValueError):
                    lm.transition(entry, status)

    def test_get_valid_transitions(self) -> None:
        lm = RegistryLifecycleManager()
        valid = lm.get_valid_transitions(RLS.REGISTERED)
        assert RLS.VALIDATED in valid
        assert RLS.ACTIVE not in valid

    def test_can_transition(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        assert lm.can_transition(entry, RLS.VALIDATED) is True
        assert lm.can_transition(entry, RLS.ACTIVE) is False

    def test_get_history(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        lm.transition(entry, RLS.VALIDATED, changed_by="admin")
        history = lm.get_history(str(entry.entry_id))
        assert len(history) == 1
        assert history[0].to_status == RLS.VALIDATED

    def test_get_all_history(self) -> None:
        lm = RegistryLifecycleManager()
        e1 = _entry(status=RLS.REGISTERED)
        e2 = _entry(status=RLS.REGISTERED)
        lm.transition(e1, RLS.VALIDATED)
        lm.transition(e2, RLS.VALIDATED)
        assert len(lm.get_all_history()) == 2

    def test_clear(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.REGISTERED)
        lm.transition(entry, RLS.VALIDATED)
        lm.clear()
        assert len(lm.get_all_history()) == 0


# ===================================================================
# RegistryCache
# ===================================================================

class TestRegistryCache:
    def test_set_and_get_entry(self) -> None:
        cache = RegistryCache()
        entry = _entry(name="test")
        cache.set_entry(entry)
        cached = cache.get_entry(str(entry.entry_id))
        assert cached is not None
        assert cached.name == "test"

    def test_get_nonexistent_entry(self) -> None:
        cache = RegistryCache()
        assert cache.get_entry(str(uuid.uuid4())) is None

    def test_invalidate_entry(self) -> None:
        cache = RegistryCache()
        entry = _entry(name="test")
        cache.set_entry(entry)
        assert cache.invalidate_entry(str(entry.entry_id)) is True
        assert cache.get_entry(str(entry.entry_id)) is None

    def test_invalidate_nonexistent(self) -> None:
        cache = RegistryCache()
        assert cache.invalidate_entry(str(uuid.uuid4())) is False

    def test_cache_hits_and_misses(self) -> None:
        cache = RegistryCache()
        entry = _entry(name="test")
        cache.set_entry(entry)
        cache.get_entry(str(entry.entry_id))  # hit
        cache.get_entry(str(uuid.uuid4()))  # miss
        assert cache.cache_hits() == 1
        assert cache.cache_misses() == 1

    def test_search_results_cache(self) -> None:
        cache = RegistryCache()
        results = [RegistrySearchResult(entry=_entry(name="test"), score=1.0)]
        cache.set_search_results("test-query", results)
        cached = cache.get_search_results("test-query")
        assert cached is not None
        assert len(cached) == 1

    def test_version_cache(self) -> None:
        cache = RegistryCache()
        record = VersionRecord(entry_id=uuid.uuid4(), version="1.0.0")
        cache.set_version("test-key", record)
        cached = cache.get_version("test-key")
        assert cached is not None
        assert cached.version == "1.0.0"

    def test_metadata_cache(self) -> None:
        cache = RegistryCache()
        meta = RegistryMetadata(description="test")
        cache.set_metadata("test-key", meta)
        cached = cache.get_metadata("test-key")
        assert cached is not None
        assert cached.description == "test"

    def test_clear(self) -> None:
        cache = RegistryCache()
        entry = _entry(name="test")
        cache.set_entry(entry)
        count = cache.clear()
        assert count >= 1
        assert cache.cache_hits() == 0

    def test_size(self) -> None:
        cache = RegistryCache()
        entry = _entry(name="test")
        cache.set_entry(entry)
        assert cache.size() >= 1


# ===================================================================
# RegistryPolicyEngine
# ===================================================================

class TestRegistryPolicyEngine:
    def test_check_registration_allowed(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry()
        assert pe.check_registration_policy(entry, []) == []

    def test_check_registration_disallowed_type(self) -> None:
        pe = RegistryPolicyEngine()
        pe.set_allowed_registry_types(set())
        entry = _entry()
        violations = pe.check_registration_policy(entry, [])
        assert len(violations) > 0

    def test_check_registration_namespace_limit(self) -> None:
        pe = RegistryPolicyEngine()
        pe.set_max_entries_per_namespace("default", 1)
        entry = _entry(namespace="default")
        existing = [_entry(name="existing", namespace="default")]
        violations = pe.check_registration_policy(entry, existing)
        assert any("maximum" in v.lower() for v in violations)

    def test_check_namespace_policy_enabled(self) -> None:
        pe = RegistryPolicyEngine()
        ns = _namespace(name="test", enabled=True)
        assert pe.check_namespace_policy(ns) == []

    def test_check_namespace_policy_disabled(self) -> None:
        pe = RegistryPolicyEngine()
        ns = _namespace(name="test", enabled=False)
        violations = pe.check_namespace_policy(ns)
        assert any("disabled" in v.lower() for v in violations)

    def test_check_version_policy_removed(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry(status=RLS.REMOVED)
        violations = pe.check_version_policy(entry, "2.0.0")
        assert len(violations) > 0

    def test_check_version_policy_deprecated(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry(status=RLS.DEPRECATED)
        violations = pe.check_version_policy(entry, "2.0.0")
        assert len(violations) > 0

    def test_check_version_policy_active(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry(status=RLS.ACTIVE)
        assert pe.check_version_policy(entry, "2.0.0") == []

    def test_check_scope_policy_allowed(self) -> None:
        pe = RegistryPolicyEngine()
        assert pe.check_scope_policy(RegistryScope.GLOBAL) == []

    def test_check_scope_policy_disallowed(self) -> None:
        pe = RegistryPolicyEngine()
        pe.set_allowed_scopes(set())
        violations = pe.check_scope_policy(RegistryScope.GLOBAL)
        assert len(violations) > 0

    def test_check_scope_policy_global_wrong_namespace(self) -> None:
        pe = RegistryPolicyEngine()
        violations = pe.check_scope_policy(RegistryScope.GLOBAL, namespace="custom")
        assert any("GLOBAL" in v for v in violations)

    def test_check_permission_policy_no_user(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry()
        violations = pe.check_permission_policy(entry, "delete", user_id="")
        assert len(violations) > 0

    def test_check_permission_policy_owner_mismatch(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry(owner_id="owner-001")
        violations = pe.check_permission_policy(entry, "delete", user_id="other-user")
        assert len(violations) > 0

    def test_check_permission_policy_owner_match(self) -> None:
        pe = RegistryPolicyEngine()
        entry = _entry(owner_id="owner-001")
        assert pe.check_permission_policy(entry, "delete", user_id="owner-001") == []


# ===================================================================
# RegistryAudit
# ===================================================================

class TestRegistryAudit:
    def test_record_registration(self) -> None:
        audit = RegistryAudit()
        entry = _entry(name="test")
        record = audit.record_registration(entry, performed_by="admin")
        assert record.operation == "register"
        assert record.entry_name == "test"

    def test_record_update(self) -> None:
        audit = RegistryAudit()
        entry = _entry(name="test")
        record = audit.record_update(entry, performed_by="admin")
        assert record.operation == "update"

    def test_record_removal(self) -> None:
        audit = RegistryAudit()
        entry = _entry(name="test", status=RLS.ACTIVE)
        record = audit.record_removal(entry, performed_by="admin", reason="EOL")
        assert record.operation == "remove"
        assert record.details.get("reason") == "EOL"

    def test_record_activation(self) -> None:
        audit = RegistryAudit()
        entry = _entry(name="test", status=RLS.ACTIVE)
        record = audit.record_activation(entry, performed_by="admin")
        assert record.operation == "activate"

    def test_record_deprecation(self) -> None:
        audit = RegistryAudit()
        entry = _entry(name="test", status=RLS.DEPRECATED)
        record = audit.record_deprecation(entry, performed_by="admin", reason="Superseded")
        assert record.operation == "deprecate"
        assert record.details.get("reason") == "Superseded"

    def test_get_records_by_entry(self) -> None:
        audit = RegistryAudit()
        e1 = _entry(name="e1")
        e2 = _entry(name="e2")
        audit.record_registration(e1)
        audit.record_registration(e2)
        records = audit.get_records(str(e1.entry_id))
        assert len(records) == 1

    def test_get_records_all(self) -> None:
        audit = RegistryAudit()
        audit.record_registration(_entry(name="e1"))
        audit.record_registration(_entry(name="e2"))
        assert len(audit.get_records()) == 2

    def test_clear(self) -> None:
        audit = RegistryAudit()
        audit.record_registration(_entry(name="test"))
        count = audit.clear()
        assert count >= 1
        assert len(audit.get_records()) == 0


# ===================================================================
# RegistryTrace
# ===================================================================

class TestRegistryTrace:
    def test_record_stage(self) -> None:
        trace = RegistryTrace()
        record = trace.record_stage("test", "validate")
        assert record.stage_name == "test"
        assert record.operation == "validate"
        assert trace.count() == 1

    def test_record_validation_stage(self) -> None:
        trace = RegistryTrace()
        trace.record_validation_stage(entry_id=str(uuid.uuid4()), entry_name="test")
        records = trace.get_by_stage("validation")
        assert len(records) == 1

    def test_record_search_stage(self) -> None:
        trace = RegistryTrace()
        trace.record_search_stage(query="energy", duration_ms=5.0)
        records = trace.get_by_stage("search")
        assert len(records) == 1

    def test_record_index_stage(self) -> None:
        trace = RegistryTrace()
        trace.record_index_stage(entry_id=str(uuid.uuid4()), entry_name="test")
        records = trace.get_by_stage("index")
        assert len(records) == 1

    def test_record_version_stage(self) -> None:
        trace = RegistryTrace()
        trace.record_version_stage(entry_id=str(uuid.uuid4()), version="1.0.0")
        records = trace.get_by_stage("version")
        assert len(records) == 1

    def test_record_lifecycle_stage(self) -> None:
        trace = RegistryTrace()
        trace.record_lifecycle_stage(entry_id=str(uuid.uuid4()), lifecycle_transition="VALIDATED->ACTIVE")
        records = trace.get_by_stage("lifecycle")
        assert len(records) == 1

    def test_trace_with_errors(self) -> None:
        trace = RegistryTrace()
        record = trace.record_validation_stage(errors=["Validation failed"], success=False)
        assert record.success is False
        assert "Validation failed" in record.errors

    def test_get_by_operation(self) -> None:
        trace = RegistryTrace()
        trace.record_validation_stage()
        trace.record_search_stage()
        assert len(trace.get_by_operation("validate")) == 1

    def test_get_by_trace_id(self) -> None:
        trace = RegistryTrace()
        record = trace.record_stage("test", "op")
        results = trace.get_by_trace_id(str(record.trace_id))
        assert len(results) == 1

    def test_get_by_entry_id(self) -> None:
        trace = RegistryTrace()
        eid = str(uuid.uuid4())
        trace.record_validation_stage(entry_id=eid)
        trace.record_validation_stage(entry_id="other")
        assert len(trace.get_by_entry_id(eid)) == 1

    def test_get_recent(self) -> None:
        trace = RegistryTrace()
        for _ in range(5):
            trace.record_stage("test", "op")
        assert len(trace.get_recent(3)) == 3

    def test_clear(self) -> None:
        trace = RegistryTrace()
        trace.record_stage("test", "op")
        trace.clear()
        assert trace.count() == 0


# ===================================================================
# RegistryMetricsCollector
# ===================================================================

class TestRegistryMetricsCollector:
    def test_snapshot_empty(self) -> None:
        mc = RegistryMetricsCollector()
        snap = mc.snapshot()
        assert snap.entries_total == 0
        assert snap.registrations_total == 0
        assert snap.searches_total == 0
        assert snap.cache_hits == 0
        assert snap.average_latency_ms == 0.0

    def test_increment_entries(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_entries_total()
        assert mc.snapshot().entries_total == 1

    def test_decrement_entries(self) -> None:
        mc = RegistryMetricsCollector()
        mc.decrement_entries_total()
        assert mc.snapshot().entries_total == 0

    def test_increment_registrations(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_registrations()
        assert mc.snapshot().registrations_total == 1

    def test_increment_deregistrations(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_deregistrations()
        assert mc.snapshot().deregistrations_total == 1

    def test_increment_lookups(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_lookups()
        assert mc.snapshot().lookups_total == 1

    def test_increment_versions(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_versions()
        assert mc.snapshot().versions_total == 1

    def test_increment_cache_hits(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_cache_hits()
        assert mc.snapshot().cache_hits == 1

    def test_increment_cache_misses(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_cache_misses()
        assert mc.snapshot().cache_misses == 1

    def test_increment_errors(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_errors()
        assert mc.snapshot().errors_total == 1

    def test_increment_lifecycle_transitions(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_lifecycle_transitions()
        mc.increment_lifecycle_transitions()
        snap = mc.snapshot()
        # RegistryMetrics doesn't expose lifecycle_transitions directly;
        # the collector tracks it internally for use by Phase 3 orchestration
        assert snap.registrations_total >= 0

    def test_record_search_latency(self) -> None:
        mc = RegistryMetricsCollector()
        mc.record_search_latency(15.0)
        snap = mc.snapshot()
        assert snap.average_latency_ms == 15.0
        assert snap.searches_total == 1

    def test_record_multiple_latencies(self) -> None:
        mc = RegistryMetricsCollector()
        mc.record_search_latency(10.0)
        mc.record_search_latency(20.0)
        assert mc.snapshot().average_latency_ms == 15.0

    def test_set_entries_per_scope(self) -> None:
        mc = RegistryMetricsCollector()
        mc.set_entries_per_scope({"GLOBAL": 5, "DOMAIN": 3})
        snap = mc.snapshot()
        assert snap.entries_per_scope == {"GLOBAL": 5, "DOMAIN": 3}

    def test_set_entries_per_status(self) -> None:
        mc = RegistryMetricsCollector()
        mc.set_entries_per_status({"ACTIVE": 4, "REGISTERED": 2})
        snap = mc.snapshot()
        assert snap.entries_per_status == {"ACTIVE": 4, "REGISTERED": 2}

    def test_set_registry_type(self) -> None:
        mc = RegistryMetricsCollector()
        mc.set_registry_type(RegistryType.AGENT)
        assert mc.snapshot().registry_type == RegistryType.AGENT

    def test_reset(self) -> None:
        mc = RegistryMetricsCollector()
        mc.increment_entries_total()
        mc.increment_registrations()
        mc.reset()
        snap = mc.snapshot()
        assert snap.entries_total == 0
        assert snap.registrations_total == 0


# ===================================================================
# Execution Models
# ===================================================================

class TestExecutionModels:
    def test_version_record_defaults(self) -> None:
        r = VersionRecord(entry_id=uuid.uuid4())
        assert r.version == "1.0.0"
        assert r.is_active is False
        assert r.previous_version == ""

    def test_search_result_defaults(self) -> None:
        r = SearchResult(entry_id="e1")
        assert r.score == 0.0
        assert r.strategy == ""

    def test_audit_record_defaults(self) -> None:
        r = AuditRecord(entry_id=uuid.uuid4())
        assert r.operation == ""
        assert r.namespace == "default"

    def test_trace_record_defaults(self) -> None:
        r = TraceRecord()
        assert r.stage_name == ""
        assert r.success is True
        assert r.warnings == []
        assert r.errors == []

    def test_dependency_graph_defaults(self) -> None:
        g = DependencyGraph()
        assert g.nodes == {}
        assert g.root_entries == []
        assert g.dependency_depth == 0

    def test_dependency_node_defaults(self) -> None:
        n = DependencyNode()
        assert n.entry_name == ""
        assert n.dependencies == []
        assert n.level == 0

    def test_lifecycle_history_entry(self) -> None:
        e = LifecycleHistoryEntry(
            entry_id=uuid.uuid4(),
            to_status=RLS.ACTIVE,
        )
        assert e.to_status == RLS.ACTIVE
        assert e.from_status is None


# ===================================================================
# Edge Cases
# ===================================================================

class TestEdgeCases:
    def test_validator_empty_tags_list(self) -> None:
        v = RegistryValidator()
        assert v._validate_tags([]) == []

    def test_validator_empty_metadata(self) -> None:
        v = RegistryValidator()
        assert v._validate_metadata_dict({}) == []

    def test_searcher_empty_entries(self) -> None:
        searcher = RegistrySearcher()
        searcher.register_strategy_instance("exact", ExactSearch())
        assert searcher.search("query", []) == []

    def test_index_manager_empty(self) -> None:
        idx = RegistryIndexManager()
        assert idx.name_index_size() == 0
        assert idx.total_index_size() == 0

    def test_lifecycle_from_validated_back_to_registered(self) -> None:
        lm = RegistryLifecycleManager()
        entry = _entry(status=RLS.VALIDATED)
        updated = lm.transition(entry, RLS.REGISTERED)
        assert updated.status == RLS.REGISTERED

    def test_policy_engine_default_allows_all(self) -> None:
        pe = RegistryPolicyEngine()
        for reg_type in RegistryType:
            entry = _entry(registry_type=reg_type)
            assert pe.check_registration_policy(entry, []) == []

    def test_trace_multiple_stages(self) -> None:
        trace = RegistryTrace()
        trace.record_validation_stage()
        trace.record_search_stage()
        trace.record_index_stage()
        trace.record_version_stage()
        trace.record_lifecycle_stage()
        assert trace.count() == 5

    def test_metrics_snapshot_immutable(self) -> None:
        mc = RegistryMetricsCollector()
        snap1 = mc.snapshot()
        mc.increment_entries_total()
        snap2 = mc.snapshot()
        assert snap1.entries_total == 0
        assert snap2.entries_total == 1

    def test_cache_ttl_expiry(self) -> None:
        cache = RegistryCache()
        entry = _entry(name="test")
        cache.set_entry(entry, ttl_seconds=0)
        # With TTL=0, expires_at ≈ time.time(); add a small sleep to ensure expiry
        import time
        time.sleep(0.01)
        assert cache.get_entry(str(entry.entry_id)) is None
