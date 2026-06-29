"""Tests for Evidence Fusion Engine interfaces."""

from __future__ import annotations

from adip.evidence.interfaces import (
    EvidenceCollector,
    EvidenceCoordinator,
    EvidenceCorrelator,
    EvidenceGraphBuilder,
    EvidenceManager,
    EvidenceNormalizer,
    EvidencePackageBuilder,
    EvidenceScorer,
    EvidenceService,
    EvidenceValidator,
)


class TestEvidenceCollector:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceCollector()  # type: ignore[abstract]
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["collect", "collect_batch"]
        for method in methods:
            assert hasattr(EvidenceCollector, method)


class TestEvidenceValidator:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceValidator()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["validate", "validate_batch"]
        for method in methods:
            assert hasattr(EvidenceValidator, method)


class TestEvidenceNormalizer:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceNormalizer()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["normalize", "normalize_batch"]
        for method in methods:
            assert hasattr(EvidenceNormalizer, method)


class TestEvidenceCorrelator:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceCorrelator()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["correlate", "correlate_batch"]
        for method in methods:
            assert hasattr(EvidenceCorrelator, method)


class TestEvidenceScorer:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceScorer()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["score", "score_batch"]
        for method in methods:
            assert hasattr(EvidenceScorer, method)


class TestEvidenceGraphBuilder:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceGraphBuilder()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["build_graph", "add_to_graph"]
        for method in methods:
            assert hasattr(EvidenceGraphBuilder, method)


class TestEvidencePackageBuilder:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidencePackageBuilder()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["build_package", "add_to_package"]
        for method in methods:
            assert hasattr(EvidencePackageBuilder, method)


class TestEvidenceCoordinator:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceCoordinator()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["collect_and_process", "process_existing", "health", "metrics"]
        for method in methods:
            assert hasattr(EvidenceCoordinator, method)


class TestEvidenceManager:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceManager()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["collect_evidence", "get_evidence", "get_package", "health", "metrics"]
        for method in methods:
            assert hasattr(EvidenceManager, method)


class TestEvidenceService:
    def test_cannot_instantiate(self) -> None:
        try:
            EvidenceService()
            assert False
        except TypeError:
            pass

    def test_abstract_methods_exist(self) -> None:
        methods = ["collect_evidence", "get_evidence", "get_package", "health", "metrics"]
        for method in methods:
            assert hasattr(EvidenceService, method)
