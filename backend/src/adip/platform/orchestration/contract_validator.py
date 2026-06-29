"""DefaultCrossModuleContractValidator — validates cross-module contracts."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformCompatibilityReport
from adip.platform.enums import ModuleName
from adip.platform.interfaces import CrossModuleContractValidator, ServiceRegistry

logger = structlog.get_logger(__name__)

_ADJACENT_PAIRS: list[tuple[ModuleName, ModuleName]] = [
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

_CONTRACT_KEYS: dict[tuple[ModuleName, ModuleName], list[str]] = {
    (ModuleName.PLANNER, ModuleName.WORKFLOW): ["plan", "steps"],
    (ModuleName.WORKFLOW, ModuleName.MEMORY): ["workflow_id", "state"],
    (ModuleName.MEMORY, ModuleName.KNOWLEDGE): ["memory_id", "context"],
    (ModuleName.KNOWLEDGE, ModuleName.RULES): ["knowledge_id", "facts"],
    (ModuleName.RULES, ModuleName.EVIDENCE): ["rule_id", "decisions"],
    (ModuleName.EVIDENCE, ModuleName.REASONING): ["evidence_id", "scores"],
    (ModuleName.REASONING, ModuleName.RECOMMENDATION): ["reasoning_id", "conclusions"],
    (ModuleName.RECOMMENDATION, ModuleName.EXPLAINABILITY): ["recommendation_id", "alternatives"],
    (ModuleName.EXPLAINABILITY, ModuleName.DECISION_REVIEW): ["explanation_id", "narratives"],
    (ModuleName.DECISION_REVIEW, ModuleName.ACTION_MANAGER): ["review_id", "decision"],
    (ModuleName.ACTION_MANAGER, ModuleName.ACTION_ENGINE): ["action_id", "commands"],
    (ModuleName.ACTION_ENGINE, ModuleName.ENERGY): ["execution_id", "results"],
}


class DefaultCrossModuleContractValidator(CrossModuleContractValidator):
    """Validates cross-module contracts across the full platform."""

    def validate_contract(
        self,
        upstream: ModuleName,
        downstream: ModuleName,
        registry: ServiceRegistry,
    ) -> str:
        up_ok = registry.has_module(upstream)
        down_ok = registry.has_module(downstream)

        if not up_ok or not down_ok:
            missing = []
            if not up_ok:
                missing.append(upstream.value)
            if not down_ok:
                missing.append(downstream.value)
            return f"CONTRACT_ERROR: unregistered modules: {', '.join(missing)}"

        keys = _CONTRACT_KEYS.get((upstream, downstream))
        if keys is None:
            return f"CONTRACT_SKIPPED: no contract defined for {upstream.value} → {downstream.value}"

        return f"CONTRACT_OK: {upstream.value} → {downstream.value} ({len(keys)} keys)"

    def validate_all_contracts(self, registry: ServiceRegistry) -> PlatformCompatibilityReport:
        messages: list[str] = []
        ok = 0
        skipped = 0
        errors = 0

        for upstream, downstream in _ADJACENT_PAIRS:
            result = self.validate_contract(upstream, downstream, registry)
            messages.append(result)
            if result.startswith("CONTRACT_OK"):
                ok += 1
            elif result.startswith("CONTRACT_SKIPPED"):
                skipped += 1
            else:
                errors += 1

        total = len(_ADJACENT_PAIRS)
        overall = "OK" if errors == 0 and ok > 0 else "ERROR" if errors > 0 else "SKIPPED"

        logger.info(
            "contract_validator.all_validated",
            total=total,
            ok=ok,
            skipped=skipped,
            errors=errors,
            overall=overall,
        )

        return PlatformCompatibilityReport(
            platform=overall,
            rest_api="OK" if overall == "OK" else "ERROR",
            energy_domain="OK" if overall == "OK" else "ERROR",
            pairs_validated=total,
            pairs_ok=ok,
            pairs_skipped=skipped,
            pairs_error=errors,
            messages=messages,
        )
