"""DefaultBootstrapValidator — validates platform bootstrap completion."""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.platform.contracts.models import PlatformValidationResult
from adip.platform.enums import ModuleName
from adip.platform.interfaces import BootstrapValidator, ServiceRegistry

logger = structlog.get_logger(__name__)

_EXPECTED_MODULES: set[str] = {m.value for m in ModuleName}


class DefaultBootstrapValidator(BootstrapValidator):
    """Validates that the platform bootstrap completed successfully.

    Checks:
    - All 17 module services registered
    - Each module has at least one service
    - Service descriptors are present
    """

    def validate(self, registry: ServiceRegistry) -> PlatformValidationResult:
        descriptors = registry.get_service_descriptors()
        module_list = registry.get_modules()
        registered_modules = {m["name"] for m in module_list}
        missing = _EXPECTED_MODULES - registered_modules

        service_count = len(descriptors)
        module_count = len(module_list)
        modules_with_multiple = sum(1 for m in module_list if m.get("service_count", 0) >= 2)

        all_registered = len(missing) == 0
        has_services = service_count > 0
        has_modules = module_count > 0

        valid = all_registered and has_services and has_modules

        details = {
            "registered_modules": sorted(registered_modules),
            "missing_modules": sorted(missing),
            "service_count": service_count,
            "module_count": module_count,
            "modules_with_multiple_services": modules_with_multiple,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if valid:
            message = (
                f"Bootstrap validation passed: {module_count} modules, "
                f"{service_count} services registered"
            )
            logger.info("bootstrap_validator.passed", **details)
        else:
            issues = []
            if not all_registered:
                issues.append(f"missing modules: {', '.join(sorted(missing))}")
            if not has_services:
                issues.append("no services registered")
            if not has_modules:
                issues.append("no modules registered")
            message = "Bootstrap validation failed: " + "; ".join(issues)
            logger.warning("bootstrap_validator.failed", issues=issues, **details)

        return PlatformValidationResult(
            platform_valid=valid,
            bootstrap_valid=valid,
            contracts_valid=False,
            diagnostics_valid=False,
            health_status="healthy" if valid else "degraded",
            message=message,
            details=details,
        )
