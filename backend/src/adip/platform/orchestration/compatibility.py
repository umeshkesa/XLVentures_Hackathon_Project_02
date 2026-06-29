"""DefaultCompatibilityValidator — verifies contracts between adjacent modules."""

from __future__ import annotations

import structlog

from adip.platform.enums import ModuleName
from adip.platform.interfaces import CompatibilityValidator, ServiceRegistry

logger = structlog.get_logger(__name__)

# ── Adjacent module pairs in the pipeline ────────────────────────────
# Each pair is (upstream, downstream) — the output of upstream should
# be consumable by downstream.
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

# ── Expected output key contracts between adjacent modules ───────────
# These are the keys that each upstream module is expected to produce
# and the downstream module is expected to consume.
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


class DefaultCompatibilityValidator(CompatibilityValidator):
    """Default compatibility validator.

    Checks that adjacent modules in the pipeline have matching
    contracts by verifying that both are registered and that
    the expected contract keys exist (deterministic placeholder).
    """

    def validate_adjacent(
        self,
        upstream: ModuleName,
        downstream: ModuleName,
        registry: ServiceRegistry,
    ) -> str:
        upstream_reg = registry.has_module(upstream)
        downstream_reg = registry.has_module(downstream)
        pair = (upstream, downstream)

        if not upstream_reg:
            return f"COMPATIBILITY_ERROR: upstream module '{upstream.value}' is not registered"
        if not downstream_reg:
            return f"COMPATIBILITY_ERROR: downstream module '{downstream.value}' is not registered"

        contract_keys = _CONTRACT_KEYS.get(pair)
        if contract_keys is None:
            return f"COMPATIBILITY_SKIPPED: no contract defined for {upstream.value} → {downstream.value}"

        logger.debug(
            "compatibility.adjacent_valid",
            upstream=upstream.value,
            downstream=downstream.value,
            contract_keys=contract_keys,
        )
        return f"COMPATIBILITY_OK: {upstream.value} → {downstream.value} ({len(contract_keys)} contract keys)"

    def validate_all(self, registry: ServiceRegistry) -> list[str]:
        results: list[str] = []
        for upstream, downstream in _ADJACENT_PAIRS:
            result = self.validate_adjacent(upstream, downstream, registry)
            results.append(result)
            logger.debug("compatibility.pair_validated", pair=f"{upstream.value}→{downstream.value}", result=result)

        total_pairs = len(_ADJACENT_PAIRS)
        ok_count = sum(1 for r in results if r.startswith("COMPATIBILITY_OK"))
        logger.info("compatibility.all_validated", total=total_pairs, ok=ok_count)
        return results
