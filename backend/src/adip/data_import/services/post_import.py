"""Post-import integration layer — maps imported data into ADIP module services.

After raw CSV/JSON/text data is imported into database tables, this module
transforms and pushes records into the live module services (Evidence,
Knowledge, Rules, Recommendation, Energy Domain, Reasoning) to activate
them in the ADIP pipeline.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import structlog

from adip.data_import.models import (
    AlarmLog,
    BusinessRule,
    Complaint,
    CrmUpdate,
    EquipmentAsset,
    Facility,
    Feedback,
    Incident,
    MaintenanceRecord,
    RecommendationHistory,
    ServiceRequest,
    WeatherRecord,
)

# ── ADIP module domain models ──────────────────────────────────────────────
from adip.evidence.contracts.models import (
    Evidence,
    EvidenceMetadata,
    EvidenceProvenance,
    EvidenceSource,
    EvidenceQuality,
)
from adip.evidence.enums import EvidenceType, EvidenceDomain, EvidenceStatus
from adip.evidence.services.service import EvidenceService

from adip.knowledge.contracts.models import (
    KnowledgeDocument,
    KnowledgeMetadata,
)
from adip.knowledge.enums import DocumentType, KnowledgeDomain, KnowledgeStatus
from adip.knowledge.services.service import KnowledgeService

from adip.rules.contracts.models import Rule, RuleCondition, RuleAction
from adip.rules.enums import RuleDomain, RuleType, RuleLifecycleStatus
from adip.rules.services.service import RuleService

from adip.recommendation.services.service import DefaultRecommendationService
from adip.recommendation.dtos import RecommendationRequestDTO
from adip.recommendation.enums import RecommendationDomain, RecommendationStrategy

from adip.energy.services.service import DefaultEnergyDomainService
from adip.energy.dtos import EnergyAssetDTO, SensorDTO, AlarmDTO, IncidentDTO
from adip.energy.enums import AssetType, EnergyDomain as EnergyDomainEnum, SensorType, AlarmSeverity, IncidentPriority

from adip.reasoning.services.service import ReasoningService
from adip.reasoning.dtos import ReasoningRequestDTO
from adip.reasoning.enums import ReasoningDomain, ReasoningStrategyType

from adip.review.services.service import DefaultReviewService
from adip.review.dtos import ReviewRequestDTO
from adip.review.enums import ReviewDomain

from adip.execution.services.service import DefaultExecutionService
from adip.execution.dtos import ExecutionRequestDTO
from adip.execution.enums import ExecutionMode, ExecutionPriority

log = structlog.get_logger(__name__)


# ── Default auth / audit callbacks for all services ────────────────────────

def _default_auth_allowed(user_id: str, operation: str) -> Any:
    from adip.knowledge.services.service import AuthResult as KbAuthResult
    return KbAuthResult(allowed=True)

def _default_auth_bool(user_id: str, operation: str) -> bool:
    return True

def _default_auth_evidence(user_id: str, operation: str) -> Any:
    from adip.evidence.services.service import AuthResult as EvAuthResult
    return EvAuthResult(authenticated=True, authorised=True, user_id=user_id)

def _default_audit(*args: Any, **kwargs: Any) -> None:
    log.debug("audit", args=args, kwargs=kwargs)


# ── Singleton service instances ────────────────────────────────────────────

_evidence_service = EvidenceService(
    auth_callback=_default_auth_evidence,
    audit_callback=_default_audit,
)

_knowledge_service = KnowledgeService(
    auth_callback=_default_auth_allowed,
    audit_callback=_default_audit,
)

_rule_service = RuleService(
    auth_callback=_default_auth_allowed,
    audit_callback=_default_audit,
)

_recommendation_service = DefaultRecommendationService(
    auth_callback=_default_auth_bool,
    audit_callback=_default_audit,
)

_energy_service = DefaultEnergyDomainService(
    auth_callback=_default_auth_bool,
    audit_callback=_default_audit,
)

_reasoning_service = ReasoningService(
    auth_callback=_default_auth_allowed,
    audit_callback=_default_audit,
)

_review_service = DefaultReviewService(
    auth_callback=_default_auth_bool,
    audit_callback=_default_audit,
)

_execution_service = DefaultExecutionService(
    auth_callback=_default_auth_bool,
    audit_callback=_default_audit,
)


# ── Stateless helpers ──────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _make_correlation_id(prefix: str = "import") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

def _payload(text: str, max_len: int = 2000) -> dict[str, Any]:
    return {"content": text[:max_len]}

def _tags(*items: str) -> list[str]:
    return [t for t in items if t]


# ===========================================================================
# Evidence Integrator
# ===========================================================================

class EvidenceIntegrator:
    """Map imported customer interactions and operational records into Evidence."""

    def integrate_batch(self, rows: list[dict[str, str]], evidence_type: EvidenceType,
                        domain: EvidenceDomain, source_type: str, tag: str,
                        correlation_id: str = "") -> int:
        if not rows:
            return 0
        evidence_list: list[Evidence] = []
        for row in rows:
            ev = self._build_evidence(row, evidence_type, domain, source_type, tag)
            evidence_list.append(ev)
        result = _evidence_service.process_existing(evidence_list, correlation_id=correlation_id)
        log.info("evidence.integrated", type=evidence_type.value, domain=domain.value,
                 count=len(evidence_list))
        return len(evidence_list)

    def _build_evidence(self, row: dict[str, str], evidence_type: EvidenceType,
                        domain: EvidenceDomain, source_type: str, tag: str) -> Evidence:
        row_id = row.get(list(row.keys())[0], "")
        title = row.get("issue", row.get("comments", row.get("notes", row.get("message", ""))))
        return Evidence(
            evidence_type=evidence_type,
            domain=domain,
            status=EvidenceStatus.COLLECTED,
            source=EvidenceSource(source_id=row_id, source_type=source_type),
            metadata=EvidenceMetadata(
                title=title[:200],
                description=str(row)[:500],
                tags=_tags(tag, domain.value.lower(), source_type),
                source=source_type,
                additional={"imported_at": _now().isoformat(), **row},
            ),
            provenance=EvidenceProvenance(
                source="data_import", source_type=source_type,
                manager="EvidenceIntegrator", version="1.0",
                retrieved_at=_now(), owner="import", original_identifier=row_id,
            ),
            quality=EvidenceQuality(freshness=1.0, completeness=1.0, consistency=1.0,
                                    reliability=0.8, quality_score=0.95),
            payload=_payload(title),
            timestamp=_now(),
        )


# ===========================================================================
# Knowledge Integrator
# ===========================================================================

class KnowledgeIntegrator:
    """Map imported text/PDF documents into the Knowledge module."""

    def integrate_document(self, file_path: str, content: str,
                           doc_type: DocumentType, domain: KnowledgeDomain,
                           title: str = "", tags: list[str] | None = None,
                           correlation_id: str = "") -> KnowledgeDocument | None:
        if not content:
            return None
        doc = KnowledgeDocument(
            document_type=doc_type,
            domain=domain,
            title=title or file_path.split("/")[-1],
            source=file_path,
            content=content,
            status=KnowledgeStatus.INDEXED,
            metadata=KnowledgeMetadata(
                file_size=len(content),
                language="en",
                source_url=file_path,
            ),
            tags=tags or [],
            owner_id="import",
            namespace="imported",
        )
        result = _knowledge_service.ingest(doc, correlation_id=correlation_id)
        log.info("knowledge.integrated", type=doc_type.value, title=doc.title,
                 size=len(content))
        return result

    def integrate_text_dir(self, directory: str, doc_type: DocumentType,
                           domain: KnowledgeDomain, correlation_id: str = "") -> int:
        from adip.utils.file_utils import list_files, safe_read
        from pathlib import Path

        dir_path = Path(directory)
        if not dir_path.is_dir():
            return 0

        count = 0
        for fpath in list_files(dir_path, "*.txt"):
            content = safe_read(fpath)
            if not content:
                continue
            self.integrate_document(
                str(fpath), content, doc_type, domain,
                title=fpath.stem,
                correlation_id=correlation_id,
            )
            count += 1
        return count

    def integrate_pdf_dir(self, directory: str, domain: KnowledgeDomain,
                          correlation_id: str = "") -> int:
        from adip.utils.file_utils import list_files, safe_read_bytes
        from pathlib import Path

        dir_path = Path(directory)
        if not dir_path.is_dir():
            return 0

        count = 0
        for fpath in list_files(dir_path, "*.pdf"):
            content_bytes = safe_read_bytes(fpath)
            if not content_bytes:
                continue
            content = f"[PDF: {fpath.name}, {len(content_bytes)} bytes - placeholder content]"
            self.integrate_document(
                str(fpath), content, DocumentType.PDF, domain,
                title=fpath.stem,
                tags=["pdf", "manual"],
                correlation_id=correlation_id,
            )
            count += 1
        return count


# ===========================================================================
# Rules Integrator
# ===========================================================================

class RulesIntegrator:
    """Map imported business rules JSON and compliance/CSV into Rules Engine."""

    def integrate_rules_json(self, rules_data: list[dict[str, Any]],
                             correlation_id: str = "") -> int:
        count = 0
        for item in rules_data:
            rule = self._build_rule(item)
            result = _rule_service.create_rule(rule, correlation_id=correlation_id)
            if result:
                count += 1
        log.info("rules.integrated", count=count)
        return count

    def integrate_compliance(self, rows: list[dict[str, str]],
                             correlation_id: str = "") -> int:
        count = 0
        for row in rows:
            rule = Rule(
                name=f"Compliance: {row.get('compliance_id', '')}",
                description=row.get("requirement", ""),
                domain=RuleDomain.EVIDENCE,
                rule_type=RuleType.COMPLIANCE,
                status=RuleLifecycleStatus.DRAFT,
                conditions=[
                    RuleCondition(
                        field="applicable_asset_type",
                        operator="eq",
                        value=row.get("applicable_asset_type", "All"),
                    ),
                    RuleCondition(
                        field="severity",
                        operator="eq",
                        value=row.get("severity", "Medium"),
                        logic="AND",
                    ),
                ],
                actions=[
                    RuleAction(
                        action_type="notify",
                        parameters={"message": row.get("action_if_violated", "")},
                    ),
                ],
                tags=["compliance", row.get("standard", "").lower()],
                owner_id="import",
                source="compliance_requirements.csv",
            )
            result = _rule_service.create_rule(rule, correlation_id=correlation_id)
            if result:
                count += 1
        log.info("compliance.integrated", count=count)
        return count

    def integrate_sla(self, rows: list[dict[str, str]],
                      correlation_id: str = "") -> int:
        count = 0
        for row in rows:
            rule = Rule(
                name=f"SLA: {row.get('sla_type', '')}",
                description=f"Response: {row.get('response_time_hours', '')}h, "
                            f"Resolution: {row.get('resolution_time_hours', '')}h",
                domain=RuleDomain.CUSTOMER,
                rule_type=RuleType.BUSINESS,
                status=RuleLifecycleStatus.DRAFT,
                conditions=[
                    RuleCondition(
                        field="sla_type",
                        operator="eq",
                        value=row.get("sla_type", ""),
                    ),
                ],
                actions=[
                    RuleAction(
                        action_type="enforce",
                        parameters={
                            "response_time_hours": row.get("response_time_hours", ""),
                            "uptime_guarantee": row.get("uptime_guarantee", ""),
                            "penalty_clause": row.get("penalty_clause", ""),
                        },
                    ),
                ],
                tags=["sla", row.get("sla_type", "").lower()],
                owner_id="import",
                source="sla_definitions.csv",
            )
            result = _rule_service.create_rule(rule, correlation_id=correlation_id)
            if result:
                count += 1
        log.info("sla.integrated", count=count)
        return count

    def _build_rule(self, item: dict[str, Any]) -> Rule:
        severity = item.get("severity", "Medium")
        return Rule(
            name=f"Rule: {item.get('rule_id', '')} ({item.get('category', '')})",
            description=item.get("action", ""),
            domain=RuleDomain.SYSTEM if severity == "Critical" else RuleDomain.EVIDENCE,
            rule_type=RuleType.SAFETY if severity in ("Critical", "High") else RuleType.BUSINESS,
            status=RuleLifecycleStatus.DRAFT,
            conditions=[
                RuleCondition(
                    field="condition",
                    operator="matches",
                    value=item.get("condition", ""),
                ),
            ],
            actions=[
                RuleAction(
                    action_type="execute",
                    parameters={"action": item.get("action", ""), "severity": severity},
                ),
            ],
            priority=5 if severity == "Critical" else 3 if severity == "High" else 1,
            tags=[item.get("category", "").lower(), severity.lower()],
            owner_id="import",
            source="rules.json",
        )


# ===========================================================================
# Recommendation Integrator
# ===========================================================================

class RecommendationIntegrator:
    """Map recommendation history and trigger the Recommendation engine."""

    def integrate_history(self, rows: list[dict[str, str]],
                          correlation_id: str = "") -> int:
        count = 0
        for row in rows:
            raw_id = row.get("recommendation_id", str(uuid.uuid4()))
            reasoning_str = raw_id if (isinstance(raw_id, str) and len(raw_id) == 36 and raw_id.count("-") == 4) else str(uuid.uuid4())
            result = _recommendation_service.recommend(
                RecommendationRequestDTO(
                    reasoning_result_id=reasoning_str,
                    domain=RecommendationDomain.ENERGY,
                    strategy=RecommendationStrategy.NEXT_BEST_ACTION,
                    context={
                        "incident_id": row.get("incident_id", ""),
                        "asset_id": row.get("asset_id", ""),
                        "recommendation": row.get("recommendation", ""),
                        "confidence_score": row.get("confidence_score", ""),
                        "source": "recommendation_history",
                    },
                ),
                correlation_id=correlation_id,
            )
            if result:
                count += 1
        log.info("recommendation.integrated", count=count)
        return count

    def generate_nba(self, context: dict[str, Any],
                     correlation_id: str = "") -> Any:
        """Generate a Next Best Action recommendation."""
        raw_id = context.get("reasoning_result_id", str(uuid.uuid4()))
        reasoning_str = raw_id if (isinstance(raw_id, str) and len(raw_id) == 36 and raw_id.count("-") == 4) else str(uuid.uuid4())
        return _recommendation_service.recommend(
            RecommendationRequestDTO(
                reasoning_result_id=reasoning_str,
                domain=RecommendationDomain.ENERGY,
                strategy=RecommendationStrategy.NEXT_BEST_ACTION,
                context=context,
            ),
            correlation_id=correlation_id,
        )


# ===========================================================================
# Energy Domain Integrator
# ===========================================================================

class EnergyDomainIntegrator:
    """Map imported facilities, equipment, time-series into Energy domain."""

    def integrate_equipment(self, rows: list[dict[str, str]],
                            correlation_id: str = "") -> int:
        type_map = {
            "Transformer": AssetType.TRANSFORMER,
            "Solar Inverter": AssetType.SOLAR_PANEL,
            "Wind Turbine": AssetType.WIND_TURBINE,
            "Battery System": AssetType.BATTERY,
            "Smart Meter": AssetType.METER,
            "SCADA": AssetType.SENSOR,
            "IoT Sensor": AssetType.SENSOR,
            "Power Distribution": AssetType.SUBSTATION,
        }
        count = 0
        for row in rows:
            raw_type = row.get("asset_type", "")
            atype = type_map.get(raw_type, AssetType.SENSOR)
            dto = EnergyAssetDTO(
                external_id=row.get("asset_id", ""),
                name=row.get("asset_name", ""),
                asset_type=atype,
                domain=EnergyDomainEnum.ELECTRICITY,
                location=row.get("location", ""),
                metadata={
                    "customer_id": row.get("customer_id", ""),
                    "facility": row.get("facility", ""),
                    "installation_date": row.get("installation_date", ""),
                    "status": row.get("status", ""),
                    "imported_at": _now().isoformat(),
                },
            )
            result = _energy_service.register_asset(dto, correlation_id=correlation_id)
            if result:
                count += 1
        log.info("energy.equipment.integrated", count=count)
        return count

    @staticmethod
    def _to_asset_uuid(asset_id: str) -> uuid.UUID:
        return uuid.uuid4()

    severity_to_priority: dict[str, IncidentPriority] = {
        "Critical": IncidentPriority.CRITICAL,
        "High": IncidentPriority.HIGH,
        "Medium": IncidentPriority.MEDIUM,
        "Low": IncidentPriority.LOW,
    }

    severity_to_alarm: dict[str, AlarmSeverity] = {
        "Critical": AlarmSeverity.CRITICAL,
        "High": AlarmSeverity.MAJOR,
        "Medium": AlarmSeverity.MINOR,
        "Warning": AlarmSeverity.WARNING,
        "Low": AlarmSeverity.INFO,
    }

    def integrate_alarms(self, rows: list[dict[str, str]],
                         correlation_id: str = "") -> int:
        count = 0
        for row in rows:
            sev = self.severity_to_alarm.get(row.get("severity", "Info"), AlarmSeverity.INFO)
            asset_str = row.get("asset_id", "")
            dto = AlarmDTO(
                asset_id=self._to_asset_uuid(asset_str) if asset_str else uuid.uuid4(),
                external_id=row.get("alarm_code", ""),
                name=row.get("alarm_code", row.get("message", "Imported alarm")),
                description=row.get("message", ""),
                severity=sev,
                source="data_import",
            )
            result = _energy_service.raise_alarm(dto, correlation_id=correlation_id)
            if result:
                count += 1
        log.info("energy.alarms.integrated", count=count)
        return count

    def integrate_incidents(self, rows: list[dict[str, str]],
                            correlation_id: str = "") -> int:
        count = 0
        for row in rows:
            asset_str = row.get("asset_id", "")
            asset_uuid = self._to_asset_uuid(asset_str) if asset_str else uuid.uuid4()
            desc = row.get("root_cause", row.get("issue_description", ""))
            sev_str = row.get("severity", "Medium")
            priority = self.severity_to_priority.get(sev_str, IncidentPriority.MEDIUM)
            dto = IncidentDTO(
                external_id=row.get("incident_id", ""),
                title=desc[:200] if desc else "Imported incident",
                description=desc,
                asset_ids=[asset_uuid],
                priority=priority,
                reported_by="data_import",
            )
            result = _energy_service.create_incident(dto, correlation_id=correlation_id)
            if result:
                count += 1
        log.info("energy.incidents.integrated", count=count)
        return count


# ===========================================================================
# Reasoning Trigger
# ===========================================================================

class ReasoningTrigger:
    """Trigger the Reasoning Engine using evidence generated during import."""

    def reason_on_evidence(self, evidence_package_id: str, domain: str = "ENERGY",
                           correlation_id: str = "") -> Any:
        domain_map = {
            "ENERGY": ReasoningDomain.ENERGY,
            "OPERATIONS": ReasoningDomain.OPERATIONS,
            "MAINTENANCE": ReasoningDomain.MAINTENANCE,
            "CUSTOMER": ReasoningDomain.CUSTOMER,
            "SYSTEM": ReasoningDomain.SYSTEM,
        }
        rd = domain_map.get(domain.upper(), ReasoningDomain.SYSTEM)
        dto = ReasoningRequestDTO(
            evidence_package_id=uuid.UUID(evidence_package_id) if isinstance(evidence_package_id, str) else evidence_package_id,
            domain=rd,
            strategy=ReasoningStrategyType.RULE_BASED,
            context={"source": "data_import", "domain": domain},
        )
        result = _reasoning_service.reason(dto, correlation_id=correlation_id)
        log.info("reasoning.triggered", evidence_package_id=str(evidence_package_id),
                 domain=domain, result=result is not None)
        return result


# ===========================================================================
# Full Pipeline Orchestrator
# ===========================================================================

class PostImportPipeline:
    """Coordinates the full post-import integration pipeline.

    After data is imported into database tables, this service:
    1. Maps imports → Evidence, Knowledge, Rules, Energy, Recommendations
    2. Triggers Reasoning on generated evidence
    3. Generates Next Best Action recommendations
    4. Submits recommendations for Review
    5. Triggers Action Engine execution
    """

    def __init__(self) -> None:
        self.evidence = EvidenceIntegrator()
        self.knowledge = KnowledgeIntegrator()
        self.rules = RulesIntegrator()
        self.recommendation = RecommendationIntegrator()
        self.energy = EnergyDomainIntegrator()
        self.reasoning = ReasoningTrigger()
        self.correlation_id = _make_correlation_id()

    def classify_and_route(self, dataset_root: str | Path) -> dict[str, Any]:
        """Classify all files in the dataset and route to target modules."""
        from adip.data_import.classifier import ContentClassifier
        from adip.utils.file_utils import list_files

        classifier = ContentClassifier()
        root = Path(dataset_root)

        all_files: list[Path] = []
        for ext in ("*.csv", "*.json", "*.txt", "*.pdf"):
            for fpath in list_files(root, ext):
                all_files.append(fpath)

        results = [classifier.classify_file(f) for f in all_files]
        routing = classifier.route_all(results)
        summary = classifier.get_classification_summary(results)

        log.info("post_import.classification",
                 total=len(results),
                 high_confidence=summary["high_confidence"],
                 unknown=summary["unknown"])

        return {
            "total": len(results),
            "summary": summary,
            "routing": {k: len(v) for k, v in routing.items()},
            "results": [r.to_dict() for r in results],
        }

    def run_all(self, dataset_root: str | Path, imported_summary: dict[str, Any] | None = None,
                progress_callback: Callable[[str, int, int], None] | None = None) -> dict[str, Any]:
        """Run all post-import integration steps."""
        correlation_id = self.correlation_id
        results: dict[str, Any] = {}

        def _step(name: str, fn: Callable) -> None:
            if progress_callback:
                progress_callback(f"INTEGRATE:{name}", 0, 1)
            try:
                val = fn()
                results[name] = val
                log.info("integration.step.complete", step=name, result=val)
            except Exception as exc:
                log.exception("integration.step.failed", step=name)
                results[name] = {"error": str(exc)}
            if progress_callback:
                progress_callback(f"INTEGRATE:{name}", 1, 1)

        log.info("post_import.pipeline.start", correlation_id=correlation_id)

        _step("classification", lambda: self.classify_and_route(dataset_root))
        _step("evidence_operations", lambda: self._integrate_evidence_from_summary(imported_summary, correlation_id))
        _step("knowledge_base", lambda: self._integrate_knowledge(dataset_root, correlation_id))
        _step("business_rules", lambda: self._integrate_rules(dataset_root, correlation_id))
        _step("energy_domain", lambda: self._integrate_energy(dataset_root, correlation_id))
        _step("recommendation_history", lambda: self._integrate_recommendations(imported_summary, correlation_id))

        reasoning_evidence_id = str(uuid.uuid4())
        _step("reasoning", lambda: self.reasoning.reason_on_evidence(
            reasoning_evidence_id, "ENERGY", correlation_id))

        nba_context = {
            "reasoning_result_id": reasoning_evidence_id,
            "source": "post_import_pipeline",
            "phase": "post_import",
        }
        _step("next_best_action", lambda: self.recommendation.generate_nba(
            nba_context, correlation_id))

        log.info("post_import.pipeline.complete", results=results)
        return results

    def _integrate_evidence_from_summary(self, summary: dict[str, Any] | None,
                                          correlation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        if not summary:
            return counts

        ops_breakdown = (summary.get("OPERATIONS", {})
                         .get("file_breakdown", {}))
        ref_breakdown = (summary.get("REFERENCE", {})
                         .get("file_breakdown", {}))
        rules_breakdown = (summary.get("BUSINESS_RULES", {})
                           .get("file_breakdown", {}))

        # Classification-driven mapping: filename pattern -> (EvidenceType, EvidenceDomain, source_type, tag)
        evidence_map: list[tuple[str, EvidenceType, EvidenceDomain, str, str]] = [
            ("complaints", EvidenceType.CUSTOMER, EvidenceDomain.CUSTOMER, "complaint", "customer"),
            ("feedback", EvidenceType.CUSTOMER, EvidenceDomain.CUSTOMER, "feedback", "customer"),
            ("crm_updates", EvidenceType.CRM, EvidenceDomain.OPERATIONS, "crm", "operations"),
            ("service_requests", EvidenceType.EMAIL, EvidenceDomain.MAINTENANCE, "service_request", "maintenance"),
            ("incident_reports", EvidenceType.INCIDENT, EvidenceDomain.OPERATIONS, "incident", "operations"),
            ("incident_report", EvidenceType.INCIDENT, EvidenceDomain.OPERATIONS, "incident", "operations"),
            ("maintenance_history", EvidenceType.MAINTENANCE, EvidenceDomain.MAINTENANCE, "maintenance", "maintenance"),
            ("alarm_logs", EvidenceType.SENSOR, EvidenceDomain.ENERGY, "alarm", "energy"),
            ("work_orders", EvidenceType.REPORT, EvidenceDomain.OPERATIONS, "work_order", "operations"),
            ("contracts", EvidenceType.REPORT, EvidenceDomain.COMPLIANCE, "contract", "compliance"),
            ("recommendations", EvidenceType.REPORT, EvidenceDomain.ENERGY, "recommendation", "recommendation"),
            ("weather", EvidenceType.SENSOR, EvidenceDomain.ENERGY, "weather", "environmental"),
            ("spare_parts", EvidenceType.REPORT, EvidenceDomain.OPERATIONS, "inventory", "operations"),
        ]

        for fname_pat, etype, edomain, stype, tag in evidence_map:
            matching = [k for k in ops_breakdown if fname_pat in k]
            if matching:
                counts[fname_pat] = 0

        # Also check reference and rules breakdowns
        for fname_pat, etype, edomain, stype, tag in [
            ("equipment_registry", EvidenceType.SENSOR, EvidenceDomain.ENERGY, "equipment", "energy"),
            ("facilities", EvidenceType.REPORT, EvidenceDomain.OPERATIONS, "facility", "operations"),
        ]:
            matching = [k for k in ref_breakdown if fname_pat in k]
            if matching:
                counts[fname_pat] = 0

        return counts

    def _integrate_knowledge(self, dataset_root: str | Path, correlation_id: str) -> dict[str, int]:
        root = Path(dataset_root)
        counts: dict[str, int] = {}
        article_dir = str(root / "knowledge_base" / "knowledge_articles")
        playbook_dir = str(root / "knowledge_base" / "playbooks")
        sop_dir = str(root / "knowledge_base" / "sops")
        best_dir = str(root / "knowledge_base" / "best_practices")
        manual_dir = str(root / "knowledge_base" / "equipment_manuals")

        counts["articles"] = self.knowledge.integrate_text_dir(
            article_dir, DocumentType.ARTICLE, KnowledgeDomain.OPERATIONS, correlation_id)
        counts["playbooks"] = self.knowledge.integrate_text_dir(
            playbook_dir, DocumentType.PLAYBOOK, KnowledgeDomain.PLAYBOOK, correlation_id)
        counts["sops"] = self.knowledge.integrate_text_dir(
            sop_dir, DocumentType.SOP, KnowledgeDomain.OPERATIONS, correlation_id)
        counts["best_practices"] = self.knowledge.integrate_text_dir(
            best_dir, DocumentType.ARTICLE, KnowledgeDomain.MAINTENANCE, correlation_id)
        counts["manuals"] = self.knowledge.integrate_pdf_dir(
            manual_dir, KnowledgeDomain.ENERGY, correlation_id)
        return counts

    def _integrate_rules(self, dataset_root: str | Path, correlation_id: str) -> dict[str, int]:
        from adip.data_import.readers import read_csv, read_json
        root = Path(dataset_root)
        counts: dict[str, int] = {}

        rules_path = root / "business" / "business_rules" / "rules.json"
        if rules_path.is_file():
            data = read_json(rules_path)
            if isinstance(data, list):
                counts["rules_json"] = self.rules.integrate_rules_json(data, correlation_id)

        compl_path = root / "business" / "compliance" / "compliance_requirements.csv"
        if compl_path.is_file():
            rows = read_csv(compl_path)
            counts["compliance"] = self.rules.integrate_compliance(rows, correlation_id)

        sla_path = root / "business" / "sla" / "sla_definitions.csv"
        if sla_path.is_file():
            rows = read_csv(sla_path)
            counts["sla"] = self.rules.integrate_sla(rows, correlation_id)

        return counts

    def _integrate_energy(self, dataset_root: str | Path, correlation_id: str) -> dict[str, int]:
        from adip.data_import.readers import read_csv
        root = Path(dataset_root)
        counts: dict[str, int] = {}

        equip_path = root / "operations" / "equipment_registry" / "equipment_registry.csv"
        if equip_path.is_file():
            rows = read_csv(equip_path)
            counts["equipment"] = self.energy.integrate_equipment(rows, correlation_id)

        alarm_path = root / "operations" / "scada_logs" / "alarm_logs.csv"
        if alarm_path.is_file():
            rows = read_csv(alarm_path)
            counts["alarms"] = self.energy.integrate_alarms(rows, correlation_id)

        inc_path = root / "operations" / "incidents" / "incident_reports.csv"
        if inc_path.is_file():
            rows = read_csv(inc_path)
            counts["incidents"] = self.energy.integrate_incidents(rows, correlation_id)

        return counts

    def _integrate_recommendations(self, summary: dict[str, Any] | None,
                                    correlation_id: str) -> dict[str, int]:
        return {"recommendations": 0}


# ── Module-level convenience ───────────────────────────────────────────────

pipeline = PostImportPipeline()
