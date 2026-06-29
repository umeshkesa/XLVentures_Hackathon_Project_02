"""DefaultPlatformDiagnostics — detects platform issues."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformDiagnosticsResult
from adip.platform.enums import ModuleName
from adip.platform.interfaces import PlatformDiagnostics, ServiceRegistry

logger = structlog.get_logger(__name__)

_STAGE_TO_MODULE: dict[str, str] = {
    "planner": "planner",
    "workflow": "workflow",
    "memory": "memory",
    "knowledge": "knowledge",
    "rules": "rules",
    "evidence": "evidence",
    "reasoning": "reasoning",
    "recommendation": "recommendation",
    "explainability": "explainability",
    "decision_review": "decision_review",
    "action_manager": "action_manager",
    "action_engine": "action_engine",
    "energy": "energy",
}


class DefaultPlatformDiagnostics(PlatformDiagnostics):
    """Runs diagnostics on the platform to detect issues.

    Checks:
    - Missing services for each module
    - Circular dependencies in the service graph
    - Invalid registrations (services with wrong module)
    - Pipeline stages with unresolvable services
    """

    def run_diagnostics(self, registry: ServiceRegistry) -> PlatformDiagnosticsResult:
        descriptors = registry.get_service_descriptors()
        module_list = registry.get_modules()
        all_services = registry.resolve_all()

        registered_modules = {m["name"] for m in module_list}
        expected_modules = {m.value for m in ModuleName}

        # Check missing services
        missing_services: list[str] = []
        for mod in sorted(expected_modules - registered_modules):
            missing_services.append(f"{mod}_service")

        # Check circular dependencies via DFS
        circular_deps = self._detect_circular_dependencies(registry)

        # Check invalid registrations
        invalid_regs: list[str] = []
        for name, svc in all_services.items():
            try:
                desc = next(d for d in descriptors if d.name == name)
                if not isinstance(desc.module, ModuleName):
                    invalid_regs.append(f"{name}: invalid module type {type(desc.module).__name__}")
            except StopIteration:
                invalid_regs.append(f"{name}: missing descriptor")

        # Check broken pipeline stages
        broken_pipelines: list[str] = []
        for stage_key, mod_name in _STAGE_TO_MODULE.items():
            module_enum = ModuleName.PLANNER if mod_name == "planner" else ModuleName.WORKFLOW
            for m in ModuleName:
                if m.value == mod_name:
                    module_enum = m
                    break
            if not registry.has_module(module_enum):
                broken_pipelines.append(f"{stage_key} stage: module '{mod_name}' not registered")

        # Check missing exports (Phase 3.5)
        missing_exports: list[str] = []
        for mod in sorted(expected_modules):
            mod_services = [d.name for d in descriptors if d.module.value == mod]
            if not mod_services:
                missing_exports.append(f"{mod}: no services exported")

        # Check invalid imports (Phase 3.5)
        invalid_imports: list[str] = []
        for d in descriptors:
            for dep in d.dependencies:
                resolved = any(dep == sd.name for sd in descriptors)
                if not resolved:
                    invalid_imports.append(f"{d.name} imports '{dep}' which is not registered")

        # Check contract violations (Phase 3.5)
        contract_violations: list[str] = []
        _PAIRS = [
            ("planner", "workflow"), ("workflow", "memory"), ("memory", "knowledge"),
            ("knowledge", "rules"), ("rules", "evidence"), ("evidence", "reasoning"),
            ("reasoning", "recommendation"), ("recommendation", "explainability"),
            ("explainability", "decision_review"), ("decision_review", "action_manager"),
            ("action_manager", "action_engine"), ("action_engine", "energy"),
        ]
        for up, down in _PAIRS:
            up_reg = up in registered_modules
            down_reg = down in registered_modules
            if up_reg and not down_reg:
                contract_violations.append(f"{up} → {down}: downstream missing")
            elif not up_reg and down_reg:
                contract_violations.append(f"{up} → {down}: upstream missing")
            elif not up_reg and not down_reg:
                contract_violations.append(f"{up} → {down}: both missing")

        # Warnings
        warnings: list[str] = []
        if circular_deps:
            warnings.append(f"{len(circular_deps)} circular dependency chain(s) detected")
        if missing_services:
            warnings.append(f"{len(missing_services)} expected service(s) missing")
        if missing_exports:
            warnings.append(f"{len(missing_exports)} module(s) with no exported services")
        if invalid_imports:
            warnings.append(f"{len(invalid_imports)} invalid import(s) detected")
        if contract_violations:
            warnings.append(f"{len(contract_violations)} contract violation(s) detected")

        all_valid = (
            len(missing_services) == 0
            and len(circular_deps) == 0
            and len(invalid_regs) == 0
            and len(broken_pipelines) == 0
            and len(missing_exports) == 0
            and len(invalid_imports) == 0
            and len(contract_violations) == 0
        )

        logger.info(
            "diagnostics.completed",
            all_valid=all_valid,
            services=len(all_services),
            modules=len(module_list),
            missing=len(missing_services),
            circular=len(circular_deps),
            invalid=len(invalid_regs),
            broken=len(broken_pipelines),
            missing_exports=len(missing_exports),
            invalid_imports=len(invalid_imports),
            contract_violations=len(contract_violations),
        )

        return PlatformDiagnosticsResult(
            all_valid=all_valid,
            service_count=len(all_services),
            module_count=len(module_list),
            missing_services=missing_services,
            circular_dependencies=circular_deps,
            invalid_registrations=invalid_regs,
            broken_pipelines=broken_pipelines,
            missing_exports=missing_exports,
            invalid_imports=invalid_imports,
            contract_violations=contract_violations,
            warnings=warnings,
        )

    @staticmethod
    def _detect_circular_dependencies(registry: ServiceRegistry) -> list[list[str]]:
        descriptors = registry.get_service_descriptors()
        adj: dict[str, list[str]] = {}
        for d in descriptors:
            adj.setdefault(d.name, [])
            for dep in d.dependencies:
                adj.setdefault(d.name, []).append(dep)

        visited: set[str] = set()
        path: list[str] = []
        path_set: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str) -> None:
            if node in path_set:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            path_set.add(node)
            for neighbor in adj.get(node, []):
                dfs(neighbor)
            path.pop()
            path_set.discard(node)

        for node in adj:
            dfs(node)

        return cycles
