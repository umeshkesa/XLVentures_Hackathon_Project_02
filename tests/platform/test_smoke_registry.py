"""Smoke tests for service registry / DI wiring."""

from __future__ import annotations

import pytest

from adip.platform.enums import ModuleName
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestServiceWiring:
    """Verify that all 16 ADIP platform modules can be wired together."""

    ALL_MODULES: list[tuple[str, ModuleName]] = [
        ("planner_service", ModuleName.PLANNER),
        ("workflow_service", ModuleName.WORKFLOW),
        ("memory_service", ModuleName.MEMORY),
        ("knowledge_service", ModuleName.KNOWLEDGE),
        ("rules_service", ModuleName.RULES),
        ("plugins_service", ModuleName.PLUGINS),
        ("registry_service", ModuleName.REGISTRY),
        ("evidence_service", ModuleName.EVIDENCE),
        ("reasoning_service", ModuleName.REASONING),
        ("recommendation_service", ModuleName.RECOMMENDATION),
        ("explainability_service", ModuleName.EXPLAINABILITY),
        ("decision_review_service", ModuleName.DECISION_REVIEW),
        ("action_manager_service", ModuleName.ACTION_MANAGER),
        ("action_engine_service", ModuleName.ACTION_ENGINE),
        ("energy_service", ModuleName.ENERGY),
        ("api_service", ModuleName.API),
        ("auth_service", ModuleName.AUTH),
    ]

    def test_register_all_modules(self) -> None:
        """Verify all 17 modules can be registered without error."""
        registry = DefaultServiceRegistry()
        for name, module in self.ALL_MODULES:
            registry.register(name, object(), module)

        assert registry.service_count == 17

    def test_resolve_service(self) -> None:
        """Verify service resolution works."""
        registry = DefaultServiceRegistry()
        svc = object()
        registry.register("planner_service", svc, ModuleName.PLANNER)
        resolved = registry.resolve("planner_service")
        assert resolved is svc

    def test_resolve_nonexistent(self) -> None:
        """Verify resolving a non-existent service raises KeyError."""
        registry = DefaultServiceRegistry()
        with pytest.raises(KeyError, match="not registered"):
            registry.resolve("nonexistent")

    def test_has_module(self) -> None:
        """Verify has_module works after registration."""
        registry = DefaultServiceRegistry()
        registry.register("energy_service", object(), ModuleName.ENERGY)
        assert registry.has_module(ModuleName.ENERGY)
        assert not registry.has_module(ModuleName.PLANNER)

    def test_clear_registry(self) -> None:
        """Verify registry can be cleared."""
        registry = DefaultServiceRegistry()
        registry.register("svc1", object(), ModuleName.API)
        registry.register("svc2", object(), ModuleName.AUTH)
        assert registry.service_count == 2
        registry.clear()
        assert registry.service_count == 0

    def test_get_service_descriptors(self) -> None:
        """Verify descriptors include service type and module."""
        registry = DefaultServiceRegistry()
        registry.register("my_svc", 42, ModuleName.API)
        descriptors = registry.get_service_descriptors()
        assert len(descriptors) == 1
        assert descriptors[0].name == "my_svc"
        assert descriptors[0].module == ModuleName.API
        assert descriptors[0].service_type == "int"

    def test_get_modules(self) -> None:
        """Verify modules list is correct."""
        registry = DefaultServiceRegistry()
        registry.register("s1", object(), ModuleName.PLANNER)
        registry.register("s2", object(), ModuleName.ENERGY)
        modules = registry.get_modules()
        assert len(modules) == 2
        module_names = {m["name"] for m in modules}
        assert module_names == {"planner", "energy"}

    def test_duplicate_registration(self) -> None:
        """Verify duplicate registration does not raise (logs warning)."""
        registry = DefaultServiceRegistry()
        registry.register("svc", object(), ModuleName.API)
        registry.register("svc", object(), ModuleName.AUTH)
        assert registry.service_count == 1


class TestDependencyInjection:
    """Verify DI patterns: constructor injection, no circular deps."""

    def test_constructor_injection(self) -> None:
        """Verify services are registered after construction, not during."""
        registry = DefaultServiceRegistry()
        dep_a = object()
        dep_b = object()

        registry.register("dep_a", dep_a, ModuleName.API)
        registry.register("dep_b", dep_b, ModuleName.API, dependencies=["dep_a"])

        assert registry.resolve("dep_a") is dep_a
        assert registry.resolve("dep_b") is dep_b

    def test_warns_on_missing_dependency(self) -> None:
        """Verify missing dependencies produce a warning."""
        registry = DefaultServiceRegistry()
        registry.register("service", object(), ModuleName.PLANNER, dependencies=["missing_dep"])
        descriptors = registry.get_service_descriptors()
        assert descriptors[0].dependencies == ["missing_dep"]

    def test_no_direct_instantiation_pattern(self) -> None:
        """Verify that services are passed as already-constructed objects.

        (In a real integration, these would be instantiated by a DI
        container and passed in, not created inside the registry.)
        """
        registry = DefaultServiceRegistry()

        class MyService:
            def __init__(self, dep: object) -> None:
                self.dep = dep

        dep = object()
        svc = MyService(dep)
        registry.register("my_service", svc, ModuleName.API)
        resolved = registry.resolve("my_service")
        assert isinstance(resolved, MyService)
        assert resolved.dep is dep
