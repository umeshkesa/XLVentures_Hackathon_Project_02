"""Decision Review Layer — Human-in-the-Loop Governance.

Phase 1: Architecture, Contracts & Models
Phase 2: Execution Pipeline (Governance Pipeline)
Phase 3: Enterprise Orchestration

Re-exports all public interfaces.
"""

from adip.review.contracts import models as review_models
from adip.review.dtos import ReviewDecisionDTO, ReviewRequestDTO, ReviewResponseDTO
from adip.review.enums import (
    ApprovalWorkflowType,
    ReviewDomain,
    ReviewerRole,
    ReviewOutcome,
    ReviewStatus,
)
from adip.review.interfaces import (
    ApprovalWorkflowManager,
    DecisionReviewCoordinator,
    DecisionReviewManager,
    DecisionReviewService,
    EscalationManager,
    ReviewAuditManager,
    ReviewPolicyEngine,
    ReviewValidator,
)
from adip.review.orchestration import (
    ConsensusMode,
    ConsensusResult,
    DelegationManager,
    DelegationRecord,
    GovernanceAuditPackage,
    GovernanceConfidenceCalculator,
    GovernanceLineage,
    ReviewConfidenceCalculator,
    ReviewCoordinator,
    ReviewManager,
    ReviewReadiness,
    ReviewSessionManager,
    ReviewVersionManager,
    VersionRecord,
)
from adip.review.services import DefaultReviewService, IntegrationHooks, hooks

__all__ = [
    # Enums
    "ApprovalWorkflowType",
    "ReviewDomain",
    "ReviewOutcome",
    "ReviewStatus",
    "ReviewerRole",
    # Models
    "review_models",
    # DTOs
    "ReviewRequestDTO",
    "ReviewDecisionDTO",
    "ReviewResponseDTO",
    # Interfaces
    "DecisionReviewService",
    "DecisionReviewManager",
    "DecisionReviewCoordinator",
    "ReviewValidator",
    "ReviewPolicyEngine",
    "EscalationManager",
    "ApprovalWorkflowManager",
    "ReviewAuditManager",
    # Phase 2 execution
    # (imported via execution/)
    # Phase 3 orchestration
    "ReviewSessionManager",
    "ReviewConfidenceCalculator",
    "GovernanceConfidenceCalculator",
    "ReviewerConsensusManager",
    "ConsensusMode",
    "ConsensusResult",
    "DelegationManager",
    "DelegationRecord",
    "ReviewVersionManager",
    "VersionRecord",
    "ReviewReadiness",
    "GovernanceAuditPackage",
    "GovernanceLineage",
    "ReviewCoordinator",
    "ReviewManager",
    # Services
    "DefaultReviewService",
    "IntegrationHooks",
    "hooks",
]
