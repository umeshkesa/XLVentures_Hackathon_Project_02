"""Execution-layer components for the Explainability Engine Phase 2.

Deterministic placeholder implementations for the explanation
processing, citation management, formatting, and tracing pipeline.
"""

from __future__ import annotations

from adip.explainability.execution.audience_formatter import AudienceFormatter
from adip.explainability.execution.audience_validator import AudienceValidator
from adip.explainability.execution.builder import ExplanationBuilder
from adip.explainability.execution.citation_manager import CitationManager
from adip.explainability.execution.metrics import ExplainabilityMetricsCollector
from adip.explainability.execution.models import (
    AudienceFormat,
    ExplainabilityMetrics,
    ExplanationSection,
    ExplanationTimeline,
    NarrativeTemplate,
    PolicyRule,
    QualityScore,
    SectionContent,
    TraceRecord,
)
from adip.explainability.execution.narrative_builder import NarrativeBuilder
from adip.explainability.execution.policy_engine import PolicyEngine
from adip.explainability.execution.quality_manager import ExplanationQualityManager
from adip.explainability.execution.sections import ExplanationSections
from adip.explainability.execution.template_manager import TemplateManager
from adip.explainability.execution.timeline_builder import TimelineBuilder
from adip.explainability.execution.trace import ExplainabilityTrace
from adip.explainability.execution.trace_aggregator import TraceAggregator

__all__ = [
    "AudienceFormat",
    "AudienceFormatter",
    "AudienceValidator",
    "CitationManager",
    "ExplainabilityMetrics",
    "ExplainabilityTrace",
    "ExplainabilityMetricsCollector",
    "ExplainabilityTrace",
    "ExplanationBuilder",
    "ExplanationQualityManager",
    "ExplanationSection",
    "ExplanationSections",
    "ExplanationTimeline",
    "NarrativeBuilder",
    "NarrativeTemplate",
    "PolicyEngine",
    "PolicyRule",
    "QualityScore",
    "SectionContent",
    "TemplateManager",
    "TimelineBuilder",
    "TraceAggregator",
    "TraceRecord",
]
