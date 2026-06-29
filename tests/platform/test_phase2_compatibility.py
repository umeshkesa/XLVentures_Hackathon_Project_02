"""Phase 2 smoke tests — module compatibility validation."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.compatibility import DefaultCompatibilityValidator
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestCompatibilityValidator:
    """Verify module compatibility validation."""

    def setup_registry(self, *, all_modules: bool = True) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        if all_modules:
            for module in ModuleName:
                registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_validate_adjacent_ok(self) -> None:
        registry = self.setup_registry(all_modules=True)
        validator = DefaultCompatibilityValidator()
        result = validator.validate_adjacent(ModuleName.PLANNER, ModuleName.WORKFLOW, registry)
        assert result.startswith("COMPATIBILITY_OK")

    def test_validate_adjacent_upstream_missing(self) -> None:
        registry = self.setup_registry(all_modules=False)
        registry.register("workflow_service", object(), ModuleName.WORKFLOW)
        validator = DefaultCompatibilityValidator()
        result = validator.validate_adjacent(ModuleName.PLANNER, ModuleName.WORKFLOW, registry)
        assert result.startswith("COMPATIBILITY_ERROR")
        assert "planner" in result

    def test_validate_adjacent_downstream_missing(self) -> None:
        registry = self.setup_registry(all_modules=False)
        registry.register("planner_service", object(), ModuleName.PLANNER)
        validator = DefaultCompatibilityValidator()
        result = validator.validate_adjacent(ModuleName.PLANNER, ModuleName.WORKFLOW, registry)
        assert result.startswith("COMPATIBILITY_ERROR")
        assert "workflow" in result

    def test_validate_all_returns_all_pairs(self) -> None:
        registry = self.setup_registry(all_modules=True)
        validator = DefaultCompatibilityValidator()
        results = validator.validate_all(registry)
        assert len(results) == 12  # 12 adjacent pairs
        assert all(r.startswith("COMPATIBILITY_OK") for r in results)

    def test_validate_all_with_missing_modules(self) -> None:
        registry = self.setup_registry(all_modules=False)
        registry.register("planner_service", object(), ModuleName.PLANNER)
        registry.register("workflow_service", object(), ModuleName.WORKFLOW)
        validator = DefaultCompatibilityValidator()
        results = validator.validate_all(registry)
        assert len(results) == 12  # still 12 pairs, some will error
        # First pair (planner→workflow) should be OK
        assert results[0].startswith("COMPATIBILITY_OK")
        # Most others should error
        errors = [r for r in results if r.startswith("COMPATIBILITY_ERROR")]
        assert len(errors) > 0

    def test_validate_adjacent_unknown_pair(self) -> None:
        registry = self.setup_registry(all_modules=True)
        validator = DefaultCompatibilityValidator()
        # API → AUTH is not an adjacent pair in the pipeline
        result = validator.validate_adjacent(ModuleName.API, ModuleName.AUTH, registry)
        assert result.startswith("COMPATIBILITY_SKIPPED")

    def test_contract_keys_for_all_pairs(self) -> None:
        """Verify every adjacent pair has defined contract keys."""
        registry = self.setup_registry(all_modules=True)
        validator = DefaultCompatibilityValidator()
        results = validator.validate_all(registry)
        for r in results:
            assert r.startswith("COMPATIBILITY_OK"), f"Expected OK but got: {r}"
