"""Phase 3 smoke tests — platform bootstrap validator."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.bootstrap_validator import DefaultBootstrapValidator
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestBootstrapValidator:
    """Verify the bootstrap validator detects registration issues."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_validate_full_registry_passes(self) -> None:
        registry = self.setup()
        validator = DefaultBootstrapValidator()
        result = validator.validate(registry)
        assert result.bootstrap_valid is True
        assert result.platform_valid is True
        assert "passed" in result.message.lower()

    def test_validate_missing_modules_fails(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        validator = DefaultBootstrapValidator()
        result = validator.validate(registry)
        assert result.bootstrap_valid is False
        assert "failed" in result.message.lower()

    def test_validate_empty_registry_fails(self) -> None:
        registry = DefaultServiceRegistry()
        validator = DefaultBootstrapValidator()
        result = validator.validate(registry)
        assert result.bootstrap_valid is False

    def test_validate_returns_details(self) -> None:
        registry = self.setup()
        validator = DefaultBootstrapValidator()
        result = validator.validate(registry)
        assert "registered_modules" in result.details
        assert "service_count" in result.details
        assert result.details["service_count"] == len(ModuleName)
