"""LLM service adapter — deterministic placeholder for AI assistant chat."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.models.base import ApiResponse

_RESPONSES: dict[str, str] = {
    "why was recommendation r-001 generated": "## Recommendation R-001: Schedule TF-102 Internal Inspection\n\n**Why this recommendation was generated:**\n\nTF-102 is a critical transformer serving PeakVolt Zone 4. Evidence analysis revealed:\n\n1. **Voltage fluctuations** (EV-002): Customer reported production equipment tripping 3 times due to unstable voltage\n2. **Oil analysis** (EV-003): DGA showed elevated hydrogen (85ppm) and methane (42ppm) — indicators of partial discharge\n3. **Knowledge cross-reference**: DOC-003 (Oil Analysis Best Practices) confirms these levels require immediate investigation\n4. **Business rules**: Three rules triggered (RUL-002, RUL-003, RUL-004)\n\n**Confidence**: 0.87 (High)\n**Risk Level**: High — potential catastrophic failure affecting 25% of PeakVolt capacity\n**Timeline**: 7 days from generation",
    "summarize novagrid customer interactions": "## NovaGrid Energy (C-1001) — Interaction Summary\n\n**Total Interactions**: 3 recorded\n\n| Date | Type | Subject | Status |\n|------|------|---------|--------|\n| Jun 28 | Email | Q3 Maintenance Schedule | Resolved |\n| Jun 27 | Call | Inverter Error Support | Resolved |\n| Jun 23 | Email | Monthly Performance Report | Resolved |\n\n**Key Points**:\n- Q3 maintenance schedule confirmed — aligns with production downtime\n- SP-106 inverter error E-47 identified and being addressed\n- Monthly performance: 4.2 GWh output, 94.3% efficiency\n\n**Related Assets**: SP-101, SP-102, SP-103, SP-106\n**Open Items**: None",
    "summarize uploaded knowledge documents": "## Knowledge Base Summary\n\n**Total Documents**: 10 published documents across 7 categories\n\n| Category | Count | Latest |\n|----------|-------|--------|\n| Manuals | 2 | Siemens Transformer Manual |\n| SOPs | 1 | Solar Panel Maintenance SOP v4 |\n| Best Practices | 1 | Transformer Oil Analysis |\n| Compliance | 1 | ISO 50001 Framework |\n| Playbooks | 1 | Grid Failure Playbook v5 |\n| Policies | 1 | Battery Safety Guidelines |\n| Articles | 2 | ADIP Architecture, ML White Paper |\n| Contracts | 1 | SLA Template v2 |\n\n**Most Recent Update**: ADIP Platform Architecture (Jun 15)\n**Top Keywords**: safety, transformer, maintenance, solar, compliance",
    "explain evidence ev-003": "## Evidence EV-003: TF-102 Oil Sample Analysis\n\n**Type**: Maintenance Evidence\n**Status**: Verified\n**Priority**: Medium\n\n**Description**: Routine DGA on TF-102 shows elevated hydrogen (85ppm) and methane (42ppm), indicating partial discharge activity within the transformer.\n\n**Quality Metrics**:\n- Quality Score: 91%\n- Freshness: 70% (collected Jun 27)\n- Completeness: 90%\n- Consistency: 86%\n- Reliability: 93%\n\n**Source**: ISO 17025 accredited laboratory analysis\n**Source Type**: Laboratory Report\n\n**Related**:\n- Knowledge: DOC-003 (Oil Analysis Best Practices), DOC-007 (Siemens Manual)\n- Rules: RUL-004 (Transformer maintenance rules)\n- Recommendations: R-003 (Oil reclamation)\n\n**Traceability**: Source → Evidence → Knowledge → Rules → Reasoning (RSN-001) → Recommendations (R-001, R-003)",
    "what business rules were triggered for tf-102": "## Business Rules Triggered for TF-102\n\nDuring reasoning session RSN-001, three business rules were evaluated for TF-102:\n\n| Rule ID | Description | Status | Impact |\n|---------|-------------|--------|--------|\n| RUL-002 | Voltage deviation >5% requires investigation | TRIGGERED | Deviation 14.2% — urgent investigation required |\n| RUL-003 | DGA H2 >50ppm requires immediate action | TRIGGERED | H2 at 85ppm — partial discharge confirmed |\n| RUL-004 | Transformer maintenance due every 6 months | TRIGGERED | Last maintenance: Jan 2026 — 6 months overdue |\n\n**Conclusion**: All three rules triggered, escalating TF-102 to critical priority.\n\n**Related**: R-001 (Inspection), R-003 (Oil Reclamation)",
    "explain asset health for wt-102": "## WT-102 Asset Health Assessment\n\n**Type**: Wind Turbine (2MW)\n**Location**: TerraVolt Corp Wind Farm\n\n**Overall Health Score**: 72% — **Advisory**\n\n| Dimension | Score | Status |\n|-----------|-------|--------|\n| Mechanical | 68% | Bearing wear at 72% of failure threshold |\n| Electrical | 85% | Generator and converter operating normally |\n| Structural | 90% | Tower and foundation within spec |\n| Performance | 75% | Output 94% of rated capacity |\n\n**Active Issues**:\n1. Bearing wear trending upward — 12% increase in vibration MoM\n2. Inspection recommended within 14 days (per R-009)\n\n**Maintenance History**:\n- Last inspection: Mar 2026 (routine)\n- Next scheduled: Sep 2026 (accelerated to Jul based on recommendation)\n\n**Predictive Model**: Bearing failure probability in 60 days without intervention",
    "why is recommendation r-002 confidence 0.82": "## Recommendation R-002 Confidence Breakdown\n\n**Title**: Deploy Voltage Stabilization Equipment at Zone 4\n**Overall Confidence**: 0.82 (High)\n\n| Factor | Score | Weight | Contribution |\n|--------|-------|--------|-------------|\n| Evidence Quality | 0.88 | 0.30 | 0.26 |\n| Knowledge Relevance | 0.85 | 0.25 | 0.21 |\n| Rule Consistency | 0.91 | 0.20 | 0.18 |\n| Historical Accuracy | 0.78 | 0.15 | 0.12 |\n| Feasibility | 0.70 | 0.10 | 0.07 |\n\n**Why not higher (0.82)?**\n- Feasibility score of 0.70 reflects the 30-day implementation timeline and $185K cost\n- Historical accuracy of 0.78 because DVR installations have mixed results (67% success rate in similar scenarios)\n\n**Why not lower?**\n- Strong evidence quality (0.88) from verified voltage fluctuation data\n- High rule consistency (0.91) across multiple regulatory frameworks",
    "compare recommendations r-001 and r-003": "## Comparison: R-001 vs R-003\n\nBoth recommendations address the TF-102 transformer issue at PeakVolt Zone 4.\n\n| Aspect | R-001: Internal Inspection | R-003: Oil Reclamation |\n|--------|---------------------------|----------------------|\n| **Priority** | Critical | High |\n| **Confidence** | 0.87 | 0.85 |\n| **Cost** | $45,000 | $28,000 |\n| **Savings** | $320,000 | $500,000 |\n| **Timeline** | 7 days | 14 days |\n| **Risk Level** | High | Low |\n| **Status** | Active | Approved |\n\n**Relationship**: These are complementary, not competing:\n1. **R-003** (Oil Reclamation) was already approved and is in execution — it addresses the immediate oil quality issue\n2. **R-001** (Internal Inspection) is still needed as a critical follow-up to assess the winding insulation condition\n\n**Recommendation**: Execute both in sequence — oil reclamation first (R-003), then internal inspection (R-001) to verify effectiveness.",
    "summarize imported datasets from last import": "## Last Import Summary\n\n**Status**: Completed\n**Job ID**: IMP-20260628-001\n**Date**: Jun 28, 2026\n\n| Metric | Value |\n|--------|-------|\n| Files Imported | 1 (CSV) |\n| Records Processed | 1,247 |\n| Evidence Generated | 3 |\n| Knowledge Created | 0 |\n| Rules Triggered | 4 |\n| Reasoning Sessions | 1 |\n| Recommendations | 2 |\n\n**Classification**: Operations Data → Evidence Module\n\n**Processing Time**: 6.5 seconds",
    "what is the overall platform health status": "## ADIP Platform Health Status\n\n**Overall**: Operational\n\n| Service | Status | Latency | Notes |\n|---------|--------|---------|-------|\n| API Gateway | Healthy | 45ms | All endpoints responding |\n| PostgreSQL | Healthy | 12ms | Connection pool at 34% |\n| Redis Cache | Healthy | 3ms | Hit rate 89% |\n| Import Pipeline | Healthy | — | 7/7 phases operational |\n| Reasoning Engine | Healthy | — | 5 active sessions |\n| Recommendation Engine | Healthy | — | 11 recommendations tracked |\n\n**Recent Activity** (Last 24h):\n- 1 new reasoning session started (RSN-004)\n- 2 recommendations generated (R-004, R-011)\n- 1 evidence item collected (EV-005)\n- 0 errors reported",
}


def _find_best_response(query: str) -> str:
    q = query.lower().strip()

    for key, response in _RESPONSES.items():
        if q == key or q.startswith(key) or q.endswith(key):
            return response

    if "recommendation" in q and "r-001" in q:
        return _RESPONSES["why was recommendation r-001 generated"]
    if "recommendation" in q and "r-002" in q and "confidence" in q:
        return _RESPONSES["why is recommendation r-002 confidence 0.82"]
    if "r-001" in q and "r-003" in q:
        return _RESPONSES["compare recommendations r-001 and r-003"]
    if "novagrid" in q and "interaction" in q:
        return _RESPONSES["summarize novagrid customer interactions"]
    if "knowledge" in q or "document" in q:
        return _RESPONSES["summarize uploaded knowledge documents"]
    if "evidence" in q and ("ev-003" in q or "oil" in q or "tf-102" in q):
        return _RESPONSES["explain evidence ev-003"]
    if "rule" in q and "tf-102" in q:
        return _RESPONSES["what business rules were triggered for tf-102"]
    if "asset" in q and "wt-102" in q:
        return _RESPONSES["explain asset health for wt-102"]
    if "import" in q or "dataset" in q:
        return _RESPONSES["summarize imported datasets from last import"]
    if "platform" in q or "health" in q:
        return _RESPONSES["what is the overall platform health status"]

    return (
        f"## Response\n\n"
        f"I understand you're asking about \"{query}\".\n\n"
        f"Based on the available ADIP platform data, I can help you with:\n"
        f"- **Recommendations**: Why they were generated, confidence breakdowns, comparisons\n"
        f"- **Evidence**: Explanation of evidence items and their traceability\n"
        f"- **Customers**: Summaries of interactions and engagement history\n"
        f"- **Knowledge**: Overview of documents and their relevance\n"
        f"- **Assets**: Health status and maintenance requirements\n"
        f"- **Rules**: Which business rules apply and were triggered\n"
        f"- **Platform**: Overall system health and recent activity\n\n"
        f"Could you please rephrase your question to be more specific?"
    )


class LLMAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "llm"

    def chat(self, message: str, conversation_id: str | None = None) -> ApiResponse:
        response = _find_best_response(message)
        return self._success_response(data={
            "response": response,
            "conversation_id": conversation_id or f"conv-{hash(message) & 0xFFFFFFFF:08x}",
        })

    def get_suggested_questions(self) -> ApiResponse:
        questions = [
            {"id": "SQ-1", "text": "Why was recommendation R-001 generated?", "category": "recommendations"},
            {"id": "SQ-2", "text": "Summarize NovaGrid customer interactions", "category": "customers"},
            {"id": "SQ-3", "text": "Summarize uploaded knowledge documents", "category": "knowledge"},
            {"id": "SQ-4", "text": "Explain evidence EV-003", "category": "evidence"},
            {"id": "SQ-5", "text": "What business rules were triggered for TF-102?", "category": "rules"},
            {"id": "SQ-6", "text": "Explain asset health for WT-102", "category": "assets"},
            {"id": "SQ-7", "text": "Why is recommendation R-002 confidence 0.82?", "category": "recommendations"},
            {"id": "SQ-8", "text": "Compare recommendations R-001 and R-003", "category": "recommendations"},
            {"id": "SQ-9", "text": "Summarize imported datasets from last import", "category": "import"},
            {"id": "SQ-10", "text": "What is the overall platform health status?", "category": "platform"},
        ]
        return self._success_response(data={"questions": questions})
