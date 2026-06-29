"""Phase 3 smoke tests — cross-module contract validation."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.contract_validator import DefaultCrossModuleContractValidator
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestCrossModuleContractValidator:
    """Verify cross-module contract validation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_validate_contract_ok(self) -> None:
        registry = self.setup()
        validator = DefaultCrossModuleContractValidator()
        result = validator.validate_contract(ModuleName.PLANNER, ModuleName.WORKFLOW, registry)
        assert result.startswith("CONTRACT_OK")

    def test_validate_contract_upstream_missing(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("workflow_service", object(), ModuleName.WORKFLOW)
        validator = DefaultCrossModuleContractValidator()
        result = validator.validate_contract(ModuleName.PLANNER, ModuleName.WORKFLOW, registry)
        assert result.startswith("CONTRACT_ERROR")

    def test_validate_contract_both_missing(self) -> None:
        registry = DefaultServiceRegistry()
        validator = DefaultCrossModuleContractValidator()
        result = validator.validate_contract(ModuleName.PLANNER, ModuleName.WORKFLOW, registry)
        assert result.startswith("CONTRACT_ERROR")

    def test_validate_all_contracts_returns_report(self) -> None:
        registry = self.setup()
        validator = DefaultCrossModuleContractValidator()
        report = validator.validate_all_contracts(registry)
        assert report.pairs_validated == 12
        assert report.pairs_ok == 12
        assert report.pairs_error == 0

    def test_validate_all_with_missing_module(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        validator = DefaultCrossModuleContractValidator()
        report = validator.validate_all_contracts(registry)
        assert report.pairs_error > 0
