"""DefaultExceptionMapper — standard exception propagation across the platform."""

from __future__ import annotations

import structlog

from adip.platform.enums import PipelineStage
from adip.platform.interfaces import ExceptionMapper

logger = structlog.get_logger(__name__)

# Known platform exception types and their error messages
_KNOWN_EXCEPTIONS: dict[str, str] = {
    "ValueError": "Invalid input: {message}",
    "KeyError": "Resource not found: {message}",
    "TypeError": "Type mismatch: {message}",
    "AuthenticationException": "Authentication failed: {message}",
    "AuthorizationException": "Authorization denied: {message}",
    "TokenException": "Token error: {message}",
    "SessionException": "Session error: {message}",
    "RuleException": "Rule evaluation error: {message}",
    "RuleValidationException": "Rule validation failed: {message}",
    "PluginException": "Plugin error: {message}",
    "KnowledgeException": "Knowledge error: {message}",
    "ReasoningException": "Reasoning error: {message}",
    "RecommendationException": "Recommendation error: {message}",
    "EvidenceException": "Evidence error: {message}",
    "RegistryException": "Registry error: {message}",
    "ExecutionException": "Execution error: {message}",
    "MemoryException": "Memory error: {message}",
    "WorkflowException": "Workflow error: {message}",
    "PlannerException": "Planner error: {message}",
    "EnergyException": "Energy domain error: {message}",
    "ReviewException": "Review error: {message}",
    "ExplainabilityException": "Explainability error: {message}",
}


class DefaultExceptionMapper(ExceptionMapper):
    """Default exception mapper.

    Maps domain exceptions to standardised error messages for
    pipeline responses.
    """

    def map_exception(self, exc: Exception, stage: PipelineStage) -> str:
        """Map an exception to a standard error message.

        Args:
            exc: The exception to map.
            stage: The pipeline stage where the exception occurred.

        Returns:
            A human-readable error message.
        """
        exc_name = type(exc).__name__
        exc_message = str(exc) if str(exc) else "Unknown error"

        # Try to use a known template
        if exc_name in _KNOWN_EXCEPTIONS:
            template = _KNOWN_EXCEPTIONS[exc_name]
            message = template.format(message=exc_message)
        else:
            message = f"[{stage.value}] {exc_name}: {exc_message}"

        logger.debug(
            "exception_mapper.mapped",
            exception=exc_name,
            stage=stage.value,
            message=message,
        )
        return message

    def is_known_exception(self, exc: Exception) -> bool:
        """Check if an exception is a known platform exception.

        Checks by class name against the known exceptions table.
        """
        exc_name = type(exc).__name__
        return exc_name in _KNOWN_EXCEPTIONS
