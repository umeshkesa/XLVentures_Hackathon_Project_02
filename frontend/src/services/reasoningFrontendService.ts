import type { ReasoningSession, ReasoningSummary } from '@/types/reasoning'

const mockSessions: ReasoningSession[] = [
  { id: 'RSN-001', query: 'Analyze voltage fluctuations at PeakVolt Zone 4 and determine root cause', status: 'completed', domain: 'energy', strategy: 'causal', confidence: 0.87, riskScore: 0.72, processingTimeMs: 3420, triggeredBy: 'Evidence EV-002', evidenceCount: 3, ruleCount: 4, knowledgeCount: 2, createdAt: '2026-06-28T10:15:00Z', completedAt: '2026-06-28T10:21:00Z', conclusion: 'Voltage fluctuations caused by failing transformer TF-102 insulation degradation. Partial discharge detected via DGA analysis (H2: 85ppm, CH4: 42ppm). Immediate inspection recommended.', steps: [
    { id: 'ST-001', type: 'evidence_analysis', description: 'Analyze evidence for voltage fluctuations', input: 'EV-002: Voltage fluctuation report, EV-003: TF-102 oil analysis, EV-009: Inverter error', output: 'Correlated voltage drops with TF-102 partial discharge indicators', durationMs: 890 },
    { id: 'ST-002', type: 'knowledge_retrieval', description: 'Retrieve relevant knowledge', input: 'Transformer diagnostics knowledge base', output: 'Found DOC-003 (Oil analysis best practices) and DOC-007 (Siemens maintenance manual)', durationMs: 450 },
    { id: 'ST-003', type: 'rule_evaluation', description: 'Evaluate business rules', input: 'RUL-002: Voltage deviation threshold, RUL-003: DGA alert rules, RUL-004: Transformer maintenance rules', output: 'RUL-002 triggered: voltage deviation >5%. RUL-003 triggered: H2 >50ppm. RUL-004 triggered: maintenance due.', durationMs: 620 },
    { id: 'ST-004', type: 'hypothesis_generation', description: 'Generate and test hypotheses', input: 'Evidence + Knowledge + Rules', output: 'Hypothesis 1 (confidence 0.87): TF-102 winding insulation failure. Hypothesis 2 (confidence 0.45): External grid disturbance.', durationMs: 780 },
    { id: 'ST-005', type: 'conclusion', description: 'Final reasoning conclusion', input: 'Selected Hypothesis 1 based on evidence weight', output: 'Recommend TF-102 internal inspection and oil reclamation within 7 days', durationMs: 680 },
  ], relatedRecommendations: ['R-002', 'R-003'] },
  { id: 'RSN-002', query: 'Assess grid failure response readiness at NovaGrid facility', status: 'completed', domain: 'operations', strategy: 'deductive', confidence: 0.92, riskScore: 0.45, processingTimeMs: 2150, triggeredBy: 'Scheduled audit Q2 2026', evidenceCount: 2, ruleCount: 3, knowledgeCount: 2, createdAt: '2026-06-25T09:00:00Z', completedAt: '2026-06-25T09:04:00Z', conclusion: 'Grid failure response readiness is adequate. All playbook procedures verified through tabletop exercise (85% effectiveness). One gap identified: backup generator fuel supply documentation.', steps: [
    { id: 'ST-006', type: 'evidence_analysis', description: 'Review drill results', input: 'EV-007: Grid emergency drill results, EV-004: ISO 50001 audit', output: 'Drill effectiveness 85%, compliance 94%', durationMs: 520 },
    { id: 'ST-007', type: 'knowledge_retrieval', description: 'Check playbook compliance', input: 'DOC-005: Grid failure playbook', output: 'All playbook sections verified against drill results', durationMs: 380 },
    { id: 'ST-008', type: 'rule_evaluation', description: 'Check SLA and compliance rules', input: 'RUL-009: Emergency response rules, RUL-005: ISO compliance rules', output: 'All rules satisfied', durationMs: 450 },
    { id: 'ST-009', type: 'conclusion', description: 'Final readiness assessment', input: 'Evidence + Knowledge + Rules', output: 'Readiness level: 92%. Minor gap in fuel supply documentation.', durationMs: 800 },
  ], relatedRecommendations: ['R-005', 'R-004'] },
  { id: 'RSN-003', query: 'Predictive maintenance analysis for wind turbine WT-102 bearing wear', status: 'completed', domain: 'maintenance', strategy: 'inductive', confidence: 0.83, riskScore: 0.65, processingTimeMs: 4100, triggeredBy: 'Predictive maintenance scheduler', evidenceCount: 3, ruleCount: 2, knowledgeCount: 2, createdAt: '2026-06-24T13:00:00Z', completedAt: '2026-06-24T13:07:00Z', conclusion: 'Bearing wear on WT-102 at 72% of failure threshold. Vibration analysis shows increasing trend in high-frequency band. Inspection recommended within 14 days.', steps: [
    { id: 'ST-010', type: 'evidence_analysis', description: 'Analyze sensor data', input: 'EV-012: WT-102 vibration data, EV-013: Monthly performance data', output: 'Vibration amplitude increasing 12% month-over-month in 2-4 kHz band', durationMs: 1100 },
    { id: 'ST-011', type: 'knowledge_retrieval', description: 'Retrieve maintenance knowledge', input: 'DOC-002: Wind turbine inspection checklist, DOC-010: Predictive maintenance white paper', output: 'Bearing wear pattern matches historical failure cases', durationMs: 520 },
    { id: 'ST-012', type: 'rule_evaluation', description: 'Evaluate maintenance thresholds', input: 'RUL-014: Bearing wear threshold rule', output: '72% threshold - advisory level, not yet critical', durationMs: 480 },
    { id: 'ST-013', type: 'conclusion', description: 'Generate maintenance recommendation', input: 'All analysis results', output: 'Schedule bearing inspection within 14 days. Order replacement bearings.', durationMs: 2000 },
  ], relatedRecommendations: ['R-009'] },
  { id: 'RSN-004', query: 'Evaluate battery storage capacity degradation at Solaris facility', status: 'in_progress', domain: 'energy', strategy: 'analogical', confidence: 0.0, riskScore: 0.0, processingTimeMs: 1800, triggeredBy: 'Capacity alarm EV-008', evidenceCount: 2, ruleCount: 2, knowledgeCount: 1, createdAt: '2026-06-29T08:30:00Z', steps: [
    { id: 'ST-014', type: 'evidence_analysis', description: 'Analyze capacity degradation evidence', input: 'EV-008: BB-101 capacity loss report, EV-014: Battery benchmark Q2', output: 'Analysis in progress...', durationMs: 900 },
    { id: 'ST-015', type: 'knowledge_retrieval', description: 'Retrieve battery knowledge', input: 'DOC-006: Battery safety guidelines', output: 'Found relevant capacity testing procedures', durationMs: 400 },
  ], relatedRecommendations: ['R-006'] },
  { id: 'RSN-005', query: 'EcoWatt SLA breach analysis and compensation calculation', status: 'failed', domain: 'compliance', strategy: 'deductive', confidence: 0.0, riskScore: 0.0, processingTimeMs: 3500, triggeredBy: 'Complaint EV-011', evidenceCount: 1, ruleCount: 2, knowledgeCount: 1, createdAt: '2026-06-25T08:00:00Z', failedAt: '2026-06-25T08:06:00Z', conclusion: 'Reasoning failed: Insufficient evidence to determine SLA breach root cause. Manual review required.', steps: [
    { id: 'ST-016', type: 'evidence_analysis', description: 'Analyze SLA breach report', input: 'EV-011: EcoWatt SLA breach report', output: 'Response time 45 min vs 15 min SLA. Root cause unclear.', durationMs: 800 },
    { id: 'ST-017', type: 'rule_evaluation', description: 'Evaluate SLA rules', input: 'RUL-012: SLA response time rules, RUL-013: Compensation rules', output: 'SLA breach confirmed. Compensation formula applies. Missing dispatch logs.', durationMs: 900 },
  ], relatedRecommendations: ['R-008'] },
  { id: 'RSN-006', query: 'Analyze solar panel SP-106 inverter fault pattern', status: 'completed', domain: 'energy', strategy: 'inductive', confidence: 0.79, riskScore: 0.55, processingTimeMs: 2800, triggeredBy: 'Inverter error EV-009', evidenceCount: 2, ruleCount: 2, knowledgeCount: 1, createdAt: '2026-06-27T14:00:00Z', completedAt: '2026-06-27T14:05:00Z', conclusion: 'Inverter error E-47 (DC arc fault) on SP-106. Pattern suggests intermittent connection issue in DC combiner box. Remote reset unsuccessful - physical inspection required.', steps: [
    { id: 'ST-018', type: 'evidence_analysis', description: 'Analyze inverter error', input: 'EV-009: Inverter error E-47', output: 'DC arc fault detected. 3 occurrences in 48 hours. Pattern suggests loose connection.', durationMs: 650 },
    { id: 'ST-019', type: 'knowledge_retrieval', description: 'Retrieve inverter knowledge', input: 'DOC-001: Solar panel maintenance SOP', output: 'Found DC combiner box inspection procedure', durationMs: 350 },
    { id: 'ST-020', type: 'rule_evaluation', description: 'Evaluate safety rules', input: 'RUL-011: Inverter fault response rules', output: 'Rule triggered: physical inspection required for DC arc faults', durationMs: 400 },
    { id: 'ST-021', type: 'conclusion', description: 'Generate fault conclusion', input: 'All data analyzed', output: 'DC combiner box inspection needed. Likely loose termination.', durationMs: 1400 },
  ], relatedRecommendations: [] },
  { id: 'RSN-007', query: 'Quarterly SLA performance review for NovaGrid', status: 'completed', domain: 'operations', strategy: 'deductive', confidence: 0.94, riskScore: 0.25, processingTimeMs: 1950, triggeredBy: 'Scheduled quarterly review', evidenceCount: 2, ruleCount: 2, knowledgeCount: 1, createdAt: '2026-06-23T08:00:00Z', completedAt: '2026-06-23T08:03:00Z', conclusion: 'NovaGrid SLA performance: 99.3% uptime (target 99.5%). One breach in Q2: response time 22 min (target 15 min). Overall performance satisfactory with minor improvement areas.', steps: [
    { id: 'ST-022', type: 'evidence_analysis', description: 'Review SLA metrics', input: 'EV-013: Monthly performance summary, EV-014: Q2 benchmark', output: 'Uptime 99.3%, 1 breach in Q2', durationMs: 500 },
    { id: 'ST-023', type: 'knowledge_retrieval', description: 'Review SLA terms', input: 'DOC-009: SLA template', output: 'NovaGrid on Premium tier. 99.9% target.', durationMs: 300 },
    { id: 'ST-024', type: 'rule_evaluation', description: 'Check SLA compliance rules', input: 'RUL-007: SLA performance rules', output: 'Minor breach - service credit of 5% may apply', durationMs: 350 },
    { id: 'ST-025', type: 'conclusion', description: 'Generate SLA review summary', input: 'All data', output: 'Satisfactory with recommendations for improvement', durationMs: 800 },
  ], relatedRecommendations: ['R-011'] },
].map((s) => ({ ...s, completedAt: (s as any).completedAt || (s as any).failedAt || undefined })) as ReasoningSession[]

export interface ReasoningService {
  list(params: { status?: string; domain?: string; search?: string; page: number; limit: number }): Promise<{ items: ReasoningSession[]; total: number }>
  getById(id: string): Promise<ReasoningSession | undefined>
  getSummary(): Promise<ReasoningSummary>
}

export function useReasoningService(): ReasoningService {
  return {
    async list({ status, domain, search, page, limit }) {
      let filtered = [...mockSessions]
      if (status) filtered = filtered.filter((s) => s.status === status)
      if (domain) filtered = filtered.filter((s) => s.domain === domain)
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter((s) => s.query.toLowerCase().includes(q) || s.triggeredBy.toLowerCase().includes(q))
      }
      filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      const total = filtered.length
      const start = (page - 1) * limit
      return { items: filtered.slice(start, start + limit), total }
    },
    async getById(id) { return mockSessions.find((s) => s.id === id) },
    async getSummary() {
      return {
        activeCount: mockSessions.filter((s) => s.status === 'in_progress').length,
        completedCount: mockSessions.filter((s) => s.status === 'completed').length,
        failedCount: mockSessions.filter((s) => s.status === 'failed').length,
        averageConfidence: parseFloat((mockSessions.filter((s) => s.confidence > 0).reduce((a, s) => a + s.confidence, 0) / Math.max(1, mockSessions.filter((s) => s.confidence > 0).length)).toFixed(3)),
        averageRiskScore: parseFloat((mockSessions.filter((s) => s.riskScore > 0).reduce((a, s) => a + s.riskScore, 0) / Math.max(1, mockSessions.filter((s) => s.riskScore > 0).length)).toFixed(3)),
      }
    },
  }
}

