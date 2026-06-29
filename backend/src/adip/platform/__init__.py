"""Platform Integration Module for the ADIP Platform.

Wires all platform modules (Planner, Workflow, Memory, Knowledge, Rules,
Plugins, Registry, Evidence Fusion, Reasoning, Recommendation,
Explainability, Decision Review, Action Manager, Action Engine, Energy
Domain, REST API) into a single working platform with unified health,
tracing, metrics, exception propagation, and manifest generation.

Architecture::
    External Systems (API / CLI / Tests)
         │
         ▼
    PlatformService  ←  ONLY public API
         │
         ▼
    PlatformManager  ←  internal facade
         │
         ▼
    PlatformCoordinator  ←  orchestrates pipeline
         │
         ├── ServiceRegistry      ←  DI wiring of all module services
         ├── HealthAggregator    ←  aggregate module health
         ├── TraceManager        ←  unified tracing
         ├── MetricsCollector    ←  unified metrics
         ├── ExceptionMapper     ←  standard exception propagation
         └── ManifestBuilder     ←  platform manifest
"""

from __future__ import annotations

from adip.platform.orchestration.bootstrap import DefaultPlatformBootstrap
from adip.platform.orchestration.compatibility import DefaultCompatibilityValidator
from adip.platform.orchestration.integration_metrics import DefaultIntegrationMetrics
from adip.platform.orchestration.integration_trace import DefaultIntegrationTrace
from adip.platform.orchestration.pipeline_validator import DefaultPipelineValidator
from adip.platform.orchestration.shared_context import DefaultContextManager
