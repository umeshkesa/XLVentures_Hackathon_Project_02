import type { LLMMessage, Conversation, SuggestedQuestion } from '@/types/llm'

const suggestedQs: SuggestedQuestion[] = [
  { id: 'SQ-1', text: 'Why was recommendation R-001 generated?', category: 'recommendations' },
  { id: 'SQ-2', text: 'Summarize NovaGrid customer interactions', category: 'customers' },
  { id: 'SQ-3', text: 'Summarize uploaded knowledge documents', category: 'knowledge' },
  { id: 'SQ-4', text: 'Explain evidence EV-003', category: 'evidence' },
  { id: 'SQ-5', text: 'What business rules were triggered for TF-102?', category: 'rules' },
  { id: 'SQ-6', text: 'Explain asset health for WT-102', category: 'assets' },
  { id: 'SQ-7', text: 'Why is recommendation R-002 confidence 0.82?', category: 'recommendations' },
  { id: 'SQ-8', text: 'Compare recommendations R-001 and R-003', category: 'recommendations' },
  { id: 'SQ-9', text: 'Summarize imported datasets from last import', category: 'import' },
  { id: 'SQ-10', text: 'What is the overall platform health status?', category: 'platform' },
]

const responses: Record<string, string> = {
  'why was recommendation r-001 generated': `## Recommendation R-001: Schedule TF-102 Internal Inspection

**Why this recommendation was generated:**

TF-102 is a critical transformer serving PeakVolt Zone 4. Evidence analysis revealed:

1. **Voltage fluctuations** (EV-002): Customer reported production equipment tripping 3 times due to unstable voltage
2. **Oil analysis** (EV-003): DGA showed elevated hydrogen (85ppm) and methane (42ppm) — indicators of partial discharge
3. **Knowledge cross-reference**: DOC-003 (Oil Analysis Best Practices) confirms these levels require immediate investigation
4. **Business rules**: Three rules triggered (RUL-002, RUL-003, RUL-004)

**Confidence**: 0.87 (High)
**Risk Level**: High — potential catastrophic failure affecting 25% of PeakVolt capacity
**Timeline**: 7 days from generation`,
  'summarize novagrid customer interactions': `## NovaGrid Energy (C-1001) — Interaction Summary

**Total Interactions**: 3 recorded

| Date | Type | Subject | Status |
|------|------|---------|--------|
| Jun 28 | Email | Q3 Maintenance Schedule | Resolved |
| Jun 27 | Call | Inverter Error Support | Resolved |
| Jun 23 | Email | Monthly Performance Report | Resolved |

**Key Points**:
- Q3 maintenance schedule confirmed — aligns with production downtime
- SP-106 inverter error E-47 identified and being addressed
- Monthly performance: 4.2 GWh output, 94.3% efficiency

**Related Assets**: SP-101, SP-102, SP-103, SP-106
**Open Items**: None`,
  'summarize uploaded knowledge documents': `## Knowledge Base Summary

**Total Documents**: 10 published documents across 7 categories

| Category | Count | Latest |
|----------|-------|--------|
| Manuals | 2 | Siemens Transformer Manual |
| SOPs | 1 | Solar Panel Maintenance SOP v4 |
| Best Practices | 1 | Transformer Oil Analysis |
| Compliance | 1 | ISO 50001 Framework |
| Playbooks | 1 | Grid Failure Playbook v5 |
| Policies | 1 | Battery Safety Guidelines |
| Articles | 2 | ADIP Architecture, ML White Paper |
| Contracts | 1 | SLA Template v2 |

**Most Recent Update**: ADIP Platform Architecture (Jun 15)
**Top Keywords**: safety, transformer, maintenance, solar, compliance`,
  'explain evidence ev-003': `## Evidence EV-003: TF-102 Oil Sample Analysis

**Type**: Maintenance Evidence
**Status**: Verified
**Priority**: Medium

**Description**: Routine DGA on TF-102 shows elevated hydrogen (85ppm) and methane (42ppm), indicating partial discharge activity within the transformer.

**Quality Metrics**:
- Quality Score: 91%
- Freshness: 70% (collected Jun 27)
- Completeness: 90%
- Consistency: 86%
- Reliability: 93%

**Source**: ISO 17025 accredited laboratory analysis
**Source Type**: Laboratory Report

**Related**:
- Knowledge: DOC-003 (Oil Analysis Best Practices), DOC-007 (Siemens Manual)
- Rules: RUL-004 (Transformer maintenance rules)
- Recommendations: R-003 (Oil reclamation)

**Traceability**: Source → Evidence → Knowledge → Rules → Reasoning (RSN-001) → Recommendations (R-001, R-003)`,
  'what business rules were triggered for tf-102': `## Business Rules Triggered for TF-102

During reasoning session RSN-001, three business rules were evaluated for TF-102:

| Rule ID | Description | Status | Impact |
|---------|-------------|--------|--------|
| RUL-002 | Voltage deviation >5% requires investigation | ✅ **TRIGGERED** | Deviation 14.2% — urgent investigation required |
| RUL-003 | DGA H2 >50ppm requires immediate action | ✅ **TRIGGERED** | H2 at 85ppm — partial discharge confirmed |
| RUL-004 | Transformer maintenance due every 6 months | ✅ **TRIGGERED** | Last maintenance: Jan 2026 — 6 months overdue |

**Conclusion**: All three rules triggered, escalating TF-102 to critical priority.

**Related**: R-001 (Inspection), R-003 (Oil Reclamation)`,
  'explain asset health for wt-102': `## WT-102 Asset Health Assessment

**Type**: Wind Turbine (2MW)
**Location**: TerraVolt Corp Wind Farm

**Overall Health Score**: 72% — **Advisory**

| Dimension | Score | Status |
|-----------|-------|--------|
| Mechanical | 68% | ⚠️ Bearing wear at 72% of failure threshold |
| Electrical | 85% | Generator and converter operating normally |
| Structural | 90% | Tower and foundation within spec |
| Performance | 75% | Output 94% of rated capacity |

**Active Issues**:
1. Bearing wear trending upward — 12% increase in vibration MoM
2. Inspection recommended within 14 days (per R-009)

**Maintenance History**:
- Last inspection: Mar 2026 (routine)
- Next scheduled: Sep 2026 (accelerated to Jul based on recommendation)

**Predictive Model**: Bearing failure probability in 60 days without intervention`,
  'why is recommendation r-002 confidence 0.82': `## Recommendation R-002 Confidence Breakdown

**Title**: Deploy Voltage Stabilization Equipment at Zone 4
**Overall Confidence**: 0.82 (High)

| Factor | Score | Weight | Contribution |
|--------|-------|--------|-------------|
| Evidence Quality | 0.88 | 0.30 | 0.26 |
| Knowledge Relevance | 0.85 | 0.25 | 0.21 |
| Rule Consistency | 0.91 | 0.20 | 0.18 |
| Historical Accuracy | 0.78 | 0.15 | 0.12 |
| Feasibility | 0.70 | 0.10 | 0.07 |

**Why not higher (0.82)?**
- Feasibility score of 0.70 reflects the 30-day implementation timeline and $185K cost
- Historical accuracy of 0.78 because DVR installations have mixed results (67% success rate in similar scenarios)

**Why not lower?**
- Strong evidence quality (0.88) from verified voltage fluctuation data
- High rule consistency (0.91) across multiple regulatory frameworks`,
  'compare recommendations r-001 and r-003': `## Comparison: R-001 vs R-003

Both recommendations address the TF-102 transformer issue at PeakVolt Zone 4.

| Aspect | R-001: Internal Inspection | R-003: Oil Reclamation |
|--------|---------------------------|----------------------|
| **Priority** | 🔴 Critical | 🟡 High |
| **Confidence** | 0.87 | 0.85 |
| **Cost** | $45,000 | $28,000 |
| **Savings** | $320,000 | $500,000 |
| **Timeline** | 7 days | 14 days |
| **Risk Level** | High | Low |
| **Status** | Active | Approved |

**Relationship**: These are complementary, not competing:
1. **R-003** (Oil Reclamation) was already approved and is in execution — it addresses the immediate oil quality issue
2. **R-001** (Internal Inspection) is still needed as a critical follow-up to assess the winding insulation condition

**Recommendation**: Execute both in sequence — oil reclamation first (R-003), then internal inspection (R-001) to verify effectiveness.`,
  'summarize imported datasets from last import': `## Last Import Summary

**Status**: Completed ✅
**Job ID**: IMP-20260628-001
**Date**: Jun 28, 2026

| Metric | Value |
|--------|-------|
| Files Imported | 1 (CSV) |
| Records Processed | 1,247 |
| Evidence Generated | 3 |
| Knowledge Created | 0 |
| Rules Triggered | 4 |
| Reasoning Sessions | 1 |
| Recommendations | 2 |

**Classification**: Operations Data → Evidence Module

**Processing Time**: 6.5 seconds`,
  'what is the overall platform health status': `## ADIP Platform Health Status

**Overall**: 🟢 Operational

| Service | Status | Latency | Notes |
|---------|--------|---------|-------|
| API Gateway | 🟢 Healthy | 45ms | All endpoints responding |
| PostgreSQL | 🟢 Healthy | 12ms | Connection pool at 34% |
| Redis Cache | 🟢 Healthy | 3ms | Hit rate 89% |
| Import Pipeline | 🟢 Healthy | — | 7/7 phases operational |
| Reasoning Engine | 🟢 Healthy | — | 5 active sessions |
| Recommendation Engine | 🟢 Healthy | — | 11 recommendations tracked |

**Recent Activity** (Last 24h):
- 1 new reasoning session started (RSN-004)
- 2 recommendations generated (R-004, R-011)
- 1 evidence item collected (EV-005)
- 0 errors reported`,
}

let conversationCounter = 0

export interface LLMService {
  sendMessage(conversationId: string | null, message: string): Promise<{ message: LLMMessage; conversationId: string; conversationTitle: string }>
  getConversation(conversationId: string): Promise<Conversation | undefined>
  listConversations(): Promise<Conversation[]>
  clearConversation(conversationId: string): Promise<void>
  getSuggestedQuestions(): Promise<SuggestedQuestion[]>
}

// In-memory conversations store
const conversations = new Map<string, Conversation>()

function findBestResponse(query: string): string {
  const q = query.toLowerCase().trim()

  // Direct match on known questions
  for (const [key, response] of Object.entries(responses)) {
    if (q.includes(key)) return response
  }

  // Partial matches
  if (q.includes('recommendation') && q.includes('r-001')) return responses['why was recommendation r-001 generated']
  if (q.includes('recommendation') && q.includes('r-002') && q.includes('confidence')) return responses['why is recommendation r-002 confidence 0.82']
  if (q.includes('r-001') && q.includes('r-003')) return responses['compare recommendations r-001 and r-003']
  if (q.includes('novagrid') && q.includes('interaction')) return responses['summarize novagrid customer interactions']
  if (q.includes('knowledge') || q.includes('document')) return responses['summarize uploaded knowledge documents']
  if (q.includes('evidence') && (q.includes('ev-003') || q.includes('oil') || q.includes('tf-102'))) return responses['explain evidence ev-003']
  if (q.includes('rule') && q.includes('tf-102')) return responses['what business rules were triggered for tf-102']
  if (q.includes('asset') && q.includes('wt-102')) return responses['explain asset health for wt-102']
  if (q.includes('import') || q.includes('dataset')) return responses['summarize imported datasets from last import']
  if (q.includes('platform') || q.includes('health')) return responses['what is the overall platform health status']

  // Fallback: generate a contextual response
  return `## Response

I understand you're asking about "${query}". 

Based on the available ADIP platform data, I can help you with:
- **Recommendations**: Why they were generated, confidence breakdowns, comparisons
- **Evidence**: Explanation of evidence items and their traceability
- **Customers**: Summaries of interactions and engagement history
- **Knowledge**: Overview of documents and their relevance
- **Assets**: Health status and maintenance requirements
- **Rules**: Which business rules apply and were triggered
- **Platform**: Overall system health and recent activity

Could you please rephrase your question to be more specific? For example:
- "Why was recommendation R-001 generated?"
- "Explain evidence EV-003"
- "Summarize NovaGrid interactions"
- "What is the platform health status?"`
}

export function useLLMService(): LLMService {
  return {
    async sendMessage(conversationId, message) {
      // Simulate processing delay
      await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200))

      const userMsg: LLMMessage = {
        id: `msg-${Date.now()}-user`,
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      }
      const assistantMsg: LLMMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant',
        content: findBestResponse(message),
        timestamp: new Date().toISOString(),
      }

      if (conversationId && conversations.has(conversationId)) {
        const conv = conversations.get(conversationId)!
        conv.messages.push(userMsg, assistantMsg)
        conv.updatedAt = new Date().toISOString()
        return { message: assistantMsg, conversationId, conversationTitle: conv.title }
      }

      conversationCounter++
      const title = message.length > 50 ? message.substring(0, 50) + '...' : message
      const newConv: Conversation = {
        id: `conv-${Date.now()}`,
        title,
        messages: [userMsg, assistantMsg],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      conversations.set(newConv.id, newConv)
      return { message: assistantMsg, conversationId: newConv.id, conversationTitle: title }
    },
    async getConversation(conversationId) {
      return conversations.get(conversationId)
    },
    async listConversations() {
      return Array.from(conversations.values()).sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    },
    async clearConversation(conversationId) {
      conversations.delete(conversationId)
    },
    async getSuggestedQuestions() {
      return suggestedQs
    },
  }
}
