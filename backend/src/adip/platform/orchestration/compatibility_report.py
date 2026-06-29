"""DefaultPlatformCompatibilityReportGenerator — generates compatibility reports."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformCompatibilityReport
from adip.platform.enums import ModuleName
from adip.platform.interfaces import PlatformCompatibilityReportGenerator, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultPlatformCompatibilityReportGenerator(PlatformCompatibilityReportGenerator):
    """Generates compatibility reports for Platform, REST API, and Energy Domain."""

    def generate_report(self, registry: ServiceRegistry) -> PlatformCompatibilityReport:
        descriptors = registry.get_service_descriptors()
        modules = registry.get_modules()
        module_names = {m["name"] for m in modules}

        platform_ok = ModuleName.PLANNER.value in module_names and ModuleName.ENERGY.value in module_names
        rest_api_ok = ModuleName.API.value in module_names
        energy_ok = ModuleName.ENERGY.value in module_names

        messages: list[str] = []
        total_pairs = 12
        ok_pairs = 0

        pairs = [
            (ModuleName.PLANNER, ModuleName.WORKFLOW),
            (ModuleName.WORKFLOW, ModuleName.MEMORY),
            (ModuleName.MEMORY, ModuleName.KNOWLEDGE),
            (ModuleName.KNOWLEDGE, ModuleName.RULES),
            (ModuleName.RULES, ModuleName.EVIDENCE),
            (ModuleName.EVIDENCE, ModuleName.REASONING),
            (ModuleName.REASONING, ModuleName.RECOMMENDATION),
            (ModuleName.RECOMMENDATION, ModuleName.EXPLAINABILITY),
            (ModuleName.EXPLAINABILITY, ModuleName.DECISION_REVIEW),
            (ModuleName.DECISION_REVIEW, ModuleName.ACTION_MANAGER),
            (ModuleName.ACTION_MANAGER, ModuleName.ACTION_ENGINE),
            (ModuleName.ACTION_ENGINE, ModuleName.ENERGY),
        ]

        for up, down in pairs:
            if registry.has_module(up) and registry.has_module(down):
                ok_pairs += 1
                messages.append(f"OK: {up.value} → {down.value}")
            else:
                messages.append(f"ERROR: {up.value} → {down.value} (one or both unregistered)")

        platform_status = "OK" if platform_ok else "ERROR"
        rest_api_status = "OK" if rest_api_ok else "ERROR"
        energy_status = "OK" if energy_ok else "ERROR"
        skipped = total_pairs - ok_pairs - (total_pairs - len([m for m in messages if m.startswith("ERROR")]))

        logger.info(
            "compatibility_report.generated",
            platform=platform_status,
            rest_api=rest_api_status,
            energy_domain=energy_status,
            ok_pairs=ok_pairs,
            total_pairs=total_pairs,
        )

        return PlatformCompatibilityReport(
            platform=platform_status,
            rest_api=rest_api_status,
            energy_domain=energy_status,
            pairs_validated=total_pairs,
            pairs_ok=ok_pairs,
            pairs_skipped=0,
            pairs_error=total_pairs - ok_pairs,
            messages=messages,
        )
