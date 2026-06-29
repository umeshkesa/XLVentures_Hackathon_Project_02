"""Phase 3.5 smoke tests — Platform Compliance Manager."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.compliance_manager import DefaultPlatformComplianceManager
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestPlatformComplianceManager:
    """Verify platform compliance validation."""

    def test_compliance_passes(self) -> None:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        cm = DefaultPlatformComplianceManager()
        result = cm.check_compliance(registry)
        assert result.overall_compliant is True
        assert result.solid_principles is True
        assert result.clean_architecture is True
        assert result.layer_isolation is True
        assert result.dependency_rules is True
        assert result.naming_conventions is True

    def test_compliance_returns_messages(self) -> None:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        cm = DefaultPlatformComplianceManager()
        result = cm.check_compliance(registry)
        assert len(result.messages) > 0
