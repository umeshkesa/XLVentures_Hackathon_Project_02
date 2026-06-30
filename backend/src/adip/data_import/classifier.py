"""Intelligent Content Classification — automatically identifies and classifies
uploaded files/records and routes them to the correct ADIP module.
"""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path, PurePath
from typing import Any

import structlog

log = structlog.get_logger(__name__)


# ===========================================================================
# Content Category Enum — all identifiable content types
# ===========================================================================


class ContentCategory(StrEnum):
    CUSTOMER_PROFILE = "CUSTOMER_PROFILE"
    FACILITY = "FACILITY"
    EQUIPMENT = "EQUIPMENT"
    TECHNICIAN = "TECHNICIAN"
    INCIDENT = "INCIDENT"
    WORK_ORDER = "WORK_ORDER"
    MAINTENANCE = "MAINTENANCE"
    ALARM = "ALARM"
    SERVICE_REQUEST = "SERVICE_REQUEST"
    COMPLAINT = "COMPLAINT"
    FEEDBACK = "FEEDBACK"
    CRM_UPDATE = "CRM_UPDATE"
    SPARE_PART = "SPARE_PART"
    WEATHER = "WEATHER"
    SLA = "SLA"
    COMPLIANCE = "COMPLIANCE"
    CONTRACT = "CONTRACT"
    BUSINESS_RULE = "BUSINESS_RULE"
    RECOMMENDATION_HISTORY = "RECOMMENDATION_HISTORY"
    KNOWLEDGE_ARTICLE = "KNOWLEDGE_ARTICLE"
    PLAYBOOK = "PLAYBOOK"
    SOP = "SOP"
    BEST_PRACTICE = "BEST_PRACTICE"
    EQUIPMENT_MANUAL = "EQUIPMENT_MANUAL"
    PDF_MANUAL = "PDF_MANUAL"
    SENSOR_AI4I = "SENSOR_AI4I"
    ENERGY_REPORT = "ENERGY_REPORT"
    SCENARIO = "SCENARIO"
    SCENARIO_INCIDENT = "SCENARIO_INCIDENT"
    SCENARIO_EMAIL = "SCENARIO_EMAIL"
    SCENARIO_OUTCOME = "SCENARIO_OUTCOME"
    SCENARIO_RECOMMENDATION = "SCENARIO_RECOMMENDATION"
    BUSINESS_DOCUMENT = "BUSINESS_DOCUMENT"
    MEETING_NOTE = "MEETING_NOTE"
    CALL_TRANSCRIPT = "CALL_TRANSCRIPT"
    TRANSACTION_HISTORY = "TRANSACTION_HISTORY"
    UNKNOWN = "UNKNOWN"


# ===========================================================================
# Target ADIP Module Enum
# ===========================================================================


class TargetModule(StrEnum):
    REFERENCE = "REFERENCE"
    EVIDENCE = "EVIDENCE"
    KNOWLEDGE = "KNOWLEDGE"
    RULES = "RULES"
    RECOMMENDATION = "RECOMMENDATION"
    ENERGY = "ENERGY"
    REASONING = "REASONING"
    MEMORY = "MEMORY"
    PLANNER = "PLANNER"
    WORKFLOW = "WORKFLOW"


# ===========================================================================
# Classification Result Model
# ===========================================================================


class ContentClassResult:
    """Result of classifying a file or record."""

    def __init__(
        self,
        category: ContentCategory,
        confidence: float,
        target_modules: list[TargetModule],
        file_path: str = "",
        source_name: str = "",
        detected_by: str = "",
        details: dict[str, Any] | None = None,
        classification_reason: str = "",
    ) -> None:
        self.category = category
        self.confidence = confidence
        self.target_modules = target_modules
        self.file_path = file_path
        self.source_name = source_name or Path(file_path).name
        self.detected_by = detected_by
        self.details = details or {}
        self.classification_reason = classification_reason

    def __repr__(self) -> str:
        return (
            f"ContentClassResult(category={self.category.value}, "
            f"confidence={self.confidence:.2f}, "
            f"modules={[m.value for m in self.target_modules]}, "
            f"file={self.source_name})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "confidence": self.confidence,
            "target_modules": [m.value for m in self.target_modules],
            "file_path": self.file_path,
            "source_name": self.source_name,
            "detected_by": self.detected_by,
            "details": self.details,
            "classification_reason": self.classification_reason,
        }


# ===========================================================================
# Classification registry — maps signatures to categories
# ===========================================================================


class ClassificationRegistry:
    """Central registry of classification rules: header patterns, path
    patterns, extension patterns, and content signatures."""

    # --- CSV header signatures: key columns that uniquely identify a type ---
    HEADER_SIGNATURES: list[tuple[set[str], ContentCategory, list[TargetModule], float]] = [
        ({"customer_id", "company_name", "industry"}, ContentCategory.CUSTOMER_PROFILE, [TargetModule.REFERENCE], 0.95),
        ({"facility_id", "facility_name", "customer_id"}, ContentCategory.FACILITY, [TargetModule.REFERENCE], 0.95),
        ({"asset_id", "asset_name", "asset_type"}, ContentCategory.EQUIPMENT, [TargetModule.ENERGY, TargetModule.REFERENCE], 0.95),
        ({"technician_id", "name", "specialty"}, ContentCategory.TECHNICIAN, [TargetModule.REFERENCE], 0.95),
        ({"incident_id", "asset_id", "severity", "incident_date"}, ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.90),
        ({"work_order_id", "asset_id", "priority", "issue_description"}, ContentCategory.WORK_ORDER, [TargetModule.EVIDENCE], 0.90),
        ({"maintenance_id", "asset_id", "maintenance_type"}, ContentCategory.MAINTENANCE, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.90),
        ({"alarm_code", "severity", "message", "operator_action"}, ContentCategory.ALARM, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.85),
        ({"complaint_id", "customer_id", "issue"}, ContentCategory.COMPLAINT, [TargetModule.EVIDENCE], 0.90),
        ({"feedback_id", "customer_id", "rating", "feedback_category"}, ContentCategory.FEEDBACK, [TargetModule.EVIDENCE], 0.90),
        ({"request_id", "request_type", "request_date"}, ContentCategory.SERVICE_REQUEST, [TargetModule.EVIDENCE], 0.90),
        ({"crm_id", "update_type", "assigned_team"}, ContentCategory.CRM_UPDATE, [TargetModule.EVIDENCE], 0.85),
        ({"part_id", "part_name", "asset_type", "quantity_in_stock"}, ContentCategory.SPARE_PART, [TargetModule.REFERENCE], 0.90),
        ({"city", "lat", "lon", "temperature"}, ContentCategory.WEATHER, [TargetModule.EVIDENCE], 0.85),
        ({"sla_type", "response_time_hours", "resolution_time_hours"}, ContentCategory.SLA, [TargetModule.RULES], 0.95),
        ({"compliance_id", "standard", "requirement"}, ContentCategory.COMPLIANCE, [TargetModule.RULES], 0.95),
        ({"contract_id", "customer_id", "contract_type"}, ContentCategory.CONTRACT, [TargetModule.RULES, TargetModule.EVIDENCE], 0.90),
        ({"rule_id", "category", "condition", "action"}, ContentCategory.BUSINESS_RULE, [TargetModule.RULES], 0.90),
        ({"recommendation_id", "incident_id", "asset_id", "recommendation"}, ContentCategory.RECOMMENDATION_HISTORY, [TargetModule.RECOMMENDATION], 0.90),
        ({"UDI", "Product ID", "Type", "Air temperature"}, ContentCategory.SENSOR_AI4I, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.95),
        ({"Date", "z1_Light(kW)", "z1_Plug(kW)", "z2_AC1(kW)"}, ContentCategory.ENERGY_REPORT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.95),
    ]

    # --- File path pattern signatures ---
    PATH_SIGNATURES: list[tuple[str, ContentCategory, list[TargetModule], float]] = [
        ("customer_profiles/", ContentCategory.CUSTOMER_PROFILE, [TargetModule.REFERENCE], 0.80),
        ("facility_profiles/", ContentCategory.FACILITY, [TargetModule.REFERENCE], 0.80),
        ("equipment_registry/", ContentCategory.EQUIPMENT, [TargetModule.ENERGY, TargetModule.REFERENCE], 0.80),
        ("technician_profiles/", ContentCategory.TECHNICIAN, [TargetModule.REFERENCE], 0.80),
        ("incidents/", ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.70),
        ("work_orders/", ContentCategory.WORK_ORDER, [TargetModule.EVIDENCE], 0.70),
        ("maintenance/", ContentCategory.MAINTENANCE, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.70),
        ("scada_logs/", ContentCategory.ALARM, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.70),
        ("inventory/", ContentCategory.SPARE_PART, [TargetModule.REFERENCE], 0.70),
        ("weather_data/", ContentCategory.WEATHER, [TargetModule.EVIDENCE], 0.70),
        ("service_requests/", ContentCategory.SERVICE_REQUEST, [TargetModule.EVIDENCE], 0.70),
        ("complaints/", ContentCategory.COMPLAINT, [TargetModule.EVIDENCE], 0.70),
        ("feedback/", ContentCategory.FEEDBACK, [TargetModule.EVIDENCE], 0.70),
        ("crm_updates/", ContentCategory.CRM_UPDATE, [TargetModule.EVIDENCE], 0.70),
        ("sla/", ContentCategory.SLA, [TargetModule.RULES], 0.75),
        ("compliance/", ContentCategory.COMPLIANCE, [TargetModule.RULES], 0.75),
        ("contracts/", ContentCategory.CONTRACT, [TargetModule.RULES, TargetModule.EVIDENCE], 0.75),
        ("business_rules/", ContentCategory.BUSINESS_RULE, [TargetModule.RULES], 0.75),
        ("recommendation_history/", ContentCategory.RECOMMENDATION_HISTORY, [TargetModule.RECOMMENDATION], 0.75),
        ("knowledge_articles/", ContentCategory.KNOWLEDGE_ARTICLE, [TargetModule.KNOWLEDGE], 0.85),
        ("playbooks/", ContentCategory.PLAYBOOK, [TargetModule.KNOWLEDGE], 0.85),
        ("sops/", ContentCategory.SOP, [TargetModule.KNOWLEDGE], 0.85),
        ("best_practices/", ContentCategory.BEST_PRACTICE, [TargetModule.KNOWLEDGE], 0.85),
        ("equipment_manuals/", ContentCategory.EQUIPMENT_MANUAL, [TargetModule.KNOWLEDGE], 0.85),
        ("sensor_data/", ContentCategory.SENSOR_AI4I, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.70),
        ("energy_reports/", ContentCategory.ENERGY_REPORT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.70),
        ("scenarios/SCN", ContentCategory.SCENARIO, [TargetModule.EVIDENCE, TargetModule.REASONING], 0.80),
        ("TRAN", ContentCategory.TRANSACTION_HISTORY, [TargetModule.EVIDENCE], 0.50),
        ("MEET", ContentCategory.MEETING_NOTE, [TargetModule.KNOWLEDGE], 0.50),
        ("CALL", ContentCategory.CALL_TRANSCRIPT, [TargetModule.KNOWLEDGE], 0.50),
    ]

    # --- File extension to category mapping (fallback) ---
    EXTENSION_SIGNATURES: list[tuple[str, ContentCategory, list[TargetModule], float]] = [
        (".pdf", ContentCategory.PDF_MANUAL, [TargetModule.KNOWLEDGE], 0.40),
        (".txt", ContentCategory.BUSINESS_DOCUMENT, [TargetModule.KNOWLEDGE], 0.30),
        (".json", ContentCategory.BUSINESS_RULE, [TargetModule.RULES], 0.35),
        (".csv", ContentCategory.UNKNOWN, [TargetModule.EVIDENCE], 0.20),
    ]

    # --- Content pattern signatures for text/email/chat files ---
    CONTENT_SIGNATURES: list[tuple[list[str], ContentCategory, list[TargetModule], float, str]] = [
        (["Customer:", "customer"], ContentCategory.CUSTOMER_PROFILE, [TargetModule.REFERENCE], 0.85, "Detected customer identifier in content"),
        (["Transformer", "Temperature", "°C"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.90, "Detected transformer temperature reading indicating incident"),
        (["From:", "Subject:", "To:", "Email"], ContentCategory.SCENARIO_EMAIL, [TargetModule.EVIDENCE], 0.85, "Detected email headers indicating customer communication"),
        (["Chat:", "chat message", "user said"], ContentCategory.SERVICE_REQUEST, [TargetModule.EVIDENCE], 0.75, "Detected chat transcript content"),
        (["Call Transcript", "call transcript", "call recording"], ContentCategory.CALL_TRANSCRIPT, [TargetModule.KNOWLEDGE], 0.80, "Detected call transcript"),
        (["CRM Update", "CRM Note", "customer contact"], ContentCategory.CRM_UPDATE, [TargetModule.EVIDENCE], 0.80, "Detected CRM update entry"),
        (["SOP:", "Standard Operating Procedure", "procedure:"], ContentCategory.SOP, [TargetModule.KNOWLEDGE], 0.88, "Detected Standard Operating Procedure document"),
        (["Policy:", "Policy Name"], ContentCategory.KNOWLEDGE_ARTICLE, [TargetModule.KNOWLEDGE], 0.80, "Detected policy document"),
        (["Playbook:", "Playbook Name"], ContentCategory.PLAYBOOK, [TargetModule.KNOWLEDGE], 0.85, "Detected playbook document"),
        (["Complaint", "complaint_id"], ContentCategory.COMPLAINT, [TargetModule.EVIDENCE], 0.80, "Detected complaint record"),
        (["Maintenance Log", "maintenance_type", "maintenance_id"], ContentCategory.MAINTENANCE, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.85, "Detected maintenance log"),
        (["Inspection Report", "inspection_id"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE], 0.80, "Detected inspection report"),
        (["Voltage", "fluctuation", "power"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.75, "Detected voltage/power incident description"),
        (["Battery", "degradation", "capacity"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.75, "Detected battery degradation report"),
        (["Wind turbine", "vibration", "bearing"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.80, "Detected wind turbine vibration incident"),
        (["Solar inverter", "fault", "error"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.80, "Detected solar inverter fault"),
        (["SCADA", "alarm", "alert"], ContentCategory.ALARM, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.85, "Detected SCADA alarm record"),
        (["Best Practice", "best practice"], ContentCategory.BEST_PRACTICE, [TargetModule.KNOWLEDGE], 0.80, "Detected best practice document"),
        (["Equipment Manual", "User Manual", "Operating Manual"], ContentCategory.EQUIPMENT_MANUAL, [TargetModule.KNOWLEDGE], 0.85, "Detected equipment manual"),
        (["Predictive maintenance", "maintenance alert"], ContentCategory.MAINTENANCE, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.80, "Detected predictive maintenance alert"),
        (["Emergency", "outage", "power failure"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.85, "Detected emergency/outage incident"),
        (["Energy spike", "power spike"], ContentCategory.INCIDENT, [TargetModule.EVIDENCE, TargetModule.ENERGY], 0.78, "Detected energy spike incident"),
    ]


# ===========================================================================
# Content Classifier
# ===========================================================================


class ContentClassifier:
    """Automatically identifies and classifies uploaded files/records.

    Uses a multi-strategy approach:
    1. CSV header analysis — match column sets against known signatures
    2. File path pattern matching — match directory structure against known paths
    3. File extension fallback — basic extension-based classification
    4. Content pattern detection — regex patterns within file content
    """

    def __init__(self, registry: ClassificationRegistry | None = None) -> None:
        self.registry = registry or ClassificationRegistry()
        self._header_cache: dict[str, ContentClassResult | None] = {}

    # ── Primary classification API ────────────────────────────────────────

    def classify_file(self, file_path: str | Path) -> ContentClassResult:
        """Classify a single file by its path and content signature."""
        path = Path(file_path)
        fname = path.name.lower()

        log.debug("classifier.classify_file", path=str(path))

        # 1. Try extension + content-based classification
        ext = path.suffix.lower()

        if ext == ".csv":
            return self._classify_csv(path, fname)
        elif ext == ".json":
            return self._classify_json(path, fname)
        elif ext == ".pdf":
            return ContentClassResult(
                category=ContentCategory.PDF_MANUAL,
                confidence=0.40,
                target_modules=[TargetModule.KNOWLEDGE],
                file_path=str(path),
                detected_by="extension",
                details={"extension": "pdf"},
            )
        elif ext == ".txt":
            return self._classify_text(path, fname)

        # 3. Unknown extension
        return ContentClassResult(
            category=ContentCategory.UNKNOWN,
            confidence=0.10,
            target_modules=[TargetModule.EVIDENCE],
            file_path=str(path),
            detected_by="fallback",
            details={"extension": ext},
        )

    def classify_csv_headers(self, headers: list[str], file_path: str = "") -> ContentClassResult:
        """Classify a CSV file by its column headers."""
        header_set = {h.strip().lower() for h in headers}
        cache_key = file_path or str(sorted(header_set))

        if cache_key in self._header_cache:
            cached = self._header_cache[cache_key]
            if cached is not None:
                return cached

        best: ContentClassResult | None = None

        for sig_headers, cat, modules, confidence in self.registry.HEADER_SIGNATURES:
            sig_lower = {s.lower() for s in sig_headers}
            match_count = len(sig_lower & header_set)
            if match_count >= 2:
                ratio = match_count / len(sig_lower)
                adjusted = confidence * ratio
                if best is None or adjusted > best.confidence:
                    details = {
                        "matched_headers": list(sig_lower & header_set),
                        "match_ratio": round(ratio, 2),
                        "matched_type": cat.value,
                    }
                    best = ContentClassResult(
                        category=cat,
                        confidence=adjusted,
                        target_modules=modules,
                        file_path=file_path,
                        detected_by="csv_headers",
                        details=details,
                    )

        result = best or ContentClassResult(
            category=ContentCategory.UNKNOWN,
            confidence=0.15,
            target_modules=[TargetModule.EVIDENCE],
            file_path=file_path,
            detected_by="csv_headers_fallback",
            details={"headers": headers[:10]},
        )

        self._header_cache[cache_key] = result
        return result

    def classify_record(self, row: dict[str, str], file_path: str = "") -> ContentClassResult:
        """Classify a single data record (row dict) by its field names."""
        return self.classify_csv_headers(list(row.keys()), file_path)

    def classify_file_batch(self, files: list[str | Path]) -> list[ContentClassResult]:
        """Classify multiple files at once."""
        return [self.classify_file(f) for f in files]

    def classify_directory(self, directory: str | Path) -> list[ContentClassResult]:
        """Scan and classify all files in a directory."""
        from adip.utils.file_utils import list_files

        dir_path = Path(directory)
        if not dir_path.is_dir():
            log.warning("classifier.directory_not_found", path=str(dir_path))
            return []

        results: list[ContentClassResult] = []
        for ext in ("*.csv", "*.json", "*.txt", "*.pdf"):
            for fpath in list_files(dir_path, ext):
                results.append(self.classify_file(fpath))
        return results

    def get_classification_summary(self, results: list[ContentClassResult]) -> dict[str, Any]:
        """Summarise a batch of classification results."""
        by_category: dict[str, int] = {}
        by_module: dict[str, int] = {}
        high_confidence = 0
        low_confidence = 0
        unknown = 0

        for r in results:
            cat = r.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            for m in r.target_modules:
                by_module[m.value] = by_module.get(m.value, 0) + 1
            if r.confidence >= 0.7:
                high_confidence += 1
            elif r.confidence >= 0.3:
                low_confidence += 1
            else:
                unknown += 1
            if r.category == ContentCategory.UNKNOWN:
                unknown += 1

        return {
            "total": len(results),
            "by_category": by_category,
            "by_module": by_module,
            "high_confidence": high_confidence,
            "low_confidence": low_confidence,
            "unknown": unknown,
        }

    # ── Route classification to ADIP module ──────────────────────────────

    def route_to_module(self, result: ContentClassResult) -> TargetModule:
        """Return the primary target module for a classification result."""
        if result.target_modules:
            return result.target_modules[0]
        return TargetModule.EVIDENCE

    def route_all(self, results: list[ContentClassResult]) -> dict[str, list[ContentClassResult]]:
        """Group classification results by target module."""
        routing: dict[str, list[ContentClassResult]] = {}
        for r in results:
            for m in r.target_modules:
                key = m.value
                if key not in routing:
                    routing[key] = []
                routing[key].append(r)
        return routing

    # ── Internal classification methods ───────────────────────────────────

    def _classify_csv(self, path: Path, fname: str) -> ContentClassResult:
        """Classify a CSV file — first try path, then headers, then LLM."""
        path_result = self._classify_by_path(path)
        if path_result.category != ContentCategory.UNKNOWN and path_result.confidence >= 0.75:
            return path_result

        try:
            from adip.data_import.readers import read_csv_sample

            sample = read_csv_sample(path, n=3)
            if sample and len(sample) > 0:
                header_result = self.classify_csv_headers(list(sample[0].keys()), str(path))
                if header_result.category != ContentCategory.UNKNOWN:
                    return header_result
        except Exception:
            log.debug("classifier.csv_sample_failed", path=str(path))

        llm_result = self._classify_with_llm(path.read_text(encoding="utf-8", errors="ignore")[:2000], fname, ".csv")
        if llm_result is not None and llm_result.confidence >= 0.50:
            llm_result.file_path = str(path)
            return llm_result

        return path_result

    def _classify_json(self, path: Path, fname: str) -> ContentClassResult:
        """Classify a JSON file."""
        path_result = self._classify_by_path(path)

        if "recommendation" in fname or "outcome" in fname:
            return ContentClassResult(
                category=ContentCategory.SCENARIO_OUTCOME,
                confidence=0.65,
                target_modules=[TargetModule.REASONING, TargetModule.RECOMMENDATION],
                file_path=str(path),
                detected_by="filename_match",
                details={"path_pattern": path_result.category.value if path_result.category != ContentCategory.UNKNOWN else None},
            )

        if path_result.category != ContentCategory.UNKNOWN:
            return path_result

        if "rules" in fname or "rule" in fname:
            return ContentClassResult(
                category=ContentCategory.BUSINESS_RULE,
                confidence=0.70,
                target_modules=[TargetModule.RULES],
                file_path=str(path),
                detected_by="filename_match",
                details={"keyword": "rules" if "rules" in fname else "rule"},
            )

        return ContentClassResult(
            category=ContentCategory.BUSINESS_RULE,
            confidence=0.35,
            target_modules=[TargetModule.RULES],
            file_path=str(path),
            detected_by="extension_json",
        )

    def _classify_with_llm(self, content: str, fname: str, ext: str) -> ContentClassResult | None:
        """Classify content using Gemini LLM."""
        try:
            from adip.services.llm import chat as llm_chat

            categories_list = "\n".join(f"- {c.value}" for c in ContentCategory)
            modules_list = "\n".join(f"- {m.value}" for m in TargetModule)
            preview = content[:2000]

            prompt = (
                f"Classify the following file content into exactly one of these categories:\n"
                f"{categories_list}\n\n"
                f"Also recommend the best target ADIP module from:\n"
                f"{modules_list}\n\n"
                f"File name: {fname}\n"
                f"File extension: {ext}\n\n"
                f"Content preview:\n{preview}\n\n"
                f"Respond in JSON only with keys: category, confidence (0.0-1.0), target_modules (array), "
                f"classification_reason (brief explanation)"
            )
            response = llm_chat(prompt, model="gemini-1.5-flash", max_tokens=512)
            import json
            data = json.loads(response.strip().removeprefix("```json").removesuffix("```").strip())
            cat = ContentCategory(data.get("category", "UNKNOWN"))
            modules = [TargetModule(m) for m in data.get("target_modules", ["EVIDENCE"])]
            return ContentClassResult(
                category=cat,
                confidence=min(1.0, max(0.0, float(data.get("confidence", 0.5)))),
                target_modules=modules,
                file_path="",
                detected_by="llm_classifier",
                classification_reason=data.get("classification_reason", ""),
            )
        except Exception:
            return None

    def _classify_text(self, path: Path, fname: str) -> ContentClassResult:
        """Classify a text file — uses filename first, then content analysis."""
        path_result = self._classify_by_path(path)

        if "incident" in fname:
            return ContentClassResult(
                category=ContentCategory.SCENARIO_INCIDENT,
                confidence=0.60,
                target_modules=[TargetModule.EVIDENCE],
                file_path=str(path),
                detected_by="filename_match",
                details={"path_pattern": path_result.category.value if path_result.category != ContentCategory.UNKNOWN else None},
                classification_reason="Filename indicates incident report",
            )
        if "email" in fname:
            return ContentClassResult(
                category=ContentCategory.SCENARIO_EMAIL,
                confidence=0.60,
                target_modules=[TargetModule.EVIDENCE],
                file_path=str(path),
                detected_by="filename_match",
                details={"path_pattern": path_result.category.value if path_result.category != ContentCategory.UNKNOWN else None},
                classification_reason="Filename indicates email communication",
            )

        if path_result.category != ContentCategory.UNKNOWN:
            return path_result

        content_result = self._classify_by_content(path)
        if content_result is not None and content_result.confidence >= 0.50:
            return content_result

        llm_result = self._classify_with_llm(path.read_text(encoding="utf-8", errors="ignore"), fname, ".txt")
        if llm_result is not None and llm_result.confidence >= 0.50:
            llm_result.file_path = str(path)
            return llm_result

        return ContentClassResult(
            category=ContentCategory.BUSINESS_DOCUMENT,
            confidence=0.30,
            target_modules=[TargetModule.KNOWLEDGE],
            file_path=str(path),
            detected_by="extension_txt",
            classification_reason="Generic text file — no specific content patterns detected",
        )

    def _classify_by_content(self, path: Path) -> ContentClassResult | None:
        """Classify a file by scanning its content for known patterns."""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

        content_lower = content.lower()
        best: ContentClassResult | None = None

        for keywords, cat, modules, confidence, reason in self.registry.CONTENT_SIGNATURES:
            match_count = sum(1 for kw in keywords if kw.lower() in content_lower)
            if match_count > 0:
                ratio = match_count / len(keywords)
                adjusted = confidence * ratio
                if best is None or adjusted > best.confidence:
                    matched_keywords = [kw for kw in keywords if kw.lower() in content_lower]
                    best = ContentClassResult(
                        category=cat,
                        confidence=adjusted,
                        target_modules=modules,
                        file_path=str(path),
                        detected_by="content_pattern",
                        details={
                            "matched_keywords": matched_keywords,
                            "match_ratio": round(ratio, 2),
                            "content_preview": content[:200],
                        },
                        classification_reason=reason,
                    )

        return best

    def _classify_by_path(self, path: Path) -> ContentClassResult:
        """Classify using file path directory patterns."""
        path_str = str(path).replace("\\", "/")

        for pattern, cat, modules, confidence in self.registry.PATH_SIGNATURES:
            if pattern in path_str:
                return ContentClassResult(
                    category=cat,
                    confidence=confidence,
                    target_modules=modules,
                    file_path=str(path),
                    detected_by="path_pattern",
                    details={"pattern": pattern},
                )

        return ContentClassResult(
            category=ContentCategory.UNKNOWN,
            confidence=0.10,
            target_modules=[TargetModule.EVIDENCE],
            file_path=str(path),
            detected_by="path_fallback",
        )


# ===========================================================================
# Module-level convenience
# ===========================================================================


classifier = ContentClassifier()
