import type { Explanation } from '@/types/explainability'


const mockExplanations: Explanation[] = [
  {
    id: 'EXP-001', recommendationId: 'R-001', recommendationTitle: 'Schedule TF-102 Internal Inspection',
    narrative: `This recommendation was generated based on evidence from multiple sources:

1. **Evidence Analysis**: Voltage fluctuation reports from PeakVolt Zone 4 (EV-002) showed a pattern consistent with transformer degradation. Concurrent DGA analysis of TF-102 (EV-003) revealed elevated hydrogen (85ppm) and methane (42ppm), indicating partial discharge activity.

2. **Knowledge Integration**: The analysis was cross-referenced with transformer oil analysis best practices (DOC-003) which confirmed that H2 >50ppm and CH4 >25ppm warrant immediate investigation. The Siemens maintenance manual (DOC-007) provided specific inspection procedures.

3. **Rule Evaluation**: Three rules were triggered - voltage deviation threshold exceeded (RUL-002), DGA alert levels reached (RUL-003), and scheduled maintenance window open (RUL-004).

4. **Confidence**: High confidence (0.87) based on strong evidence correlation and multiple confirming indicators.`,
    stages: [
      { name: 'Customer Data Collection', description: 'Gathered evidence from PeakVolt Zone 4 voltage fluctuation reports and transformer DGA analysis results', details: ['EV-002: Voltage fluctuation report from PeakVolt Systems', 'EV-003: TF-102 oil sample analysis from laboratory', 'Customer complaint: Production equipment tripped 3 times'], evidence: [{ id: 'EV-002', title: 'Voltage Fluctuation Report', confidence: 0.85 }, { id: 'EV-003', title: 'TF-102 Oil Analysis', confidence: 0.88 }], rules: [], knowledge: [], expanded: false },
      { name: 'Evidence Generation', description: 'Generated evidence from SCADA and laboratory data through the Evidence Fusion Engine', details: ['SCADA voltage readings collected over 48-hour period', 'Oil sample analyzed at ISO 17025 accredited lab', 'Data validated and normalized across all sources'], evidence: [], rules: [], knowledge: [], expanded: false },
      { name: 'Knowledge Retrieved', description: 'Retrieved relevant documentation from Knowledge Base', details: ['DOC-003: Transformer Oil Analysis Best Practices v2', 'DOC-007: Siemens Transformer Maintenance Manual 2025'], evidence: [], rules: [], knowledge: [{ id: 'DOC-003', title: 'Transformer Oil Analysis Best Practices' }, { id: 'DOC-007', title: 'Siemens Transformer Maintenance Manual 2025' }], expanded: false },
      { name: 'Business Rules Applied', description: 'Three business rules were triggered during evaluation', details: ['RUL-002: Voltage deviation >5% threshold â†’ TRIGGERED', 'RUL-003: DGA H2 >50ppm â†’ TRIGGERED', 'RUL-004: Maintenance interval exceeded â†’ TRIGGERED'], evidence: [], rules: [{ id: 'RUL-002', description: 'Voltage deviation >5% requires investigation', triggered: true }, { id: 'RUL-003', description: 'DGA levels above threshold require action', triggered: true }, { id: 'RUL-004', description: 'Transformer maintenance due every 6 months', triggered: true }], knowledge: [], expanded: false },
      { name: 'Reasoning Process', description: 'Causal reasoning chain from evidence to conclusion', details: ['Hypothesis 1: TF-102 winding insulation failure (confidence: 0.87)', 'Hypothesis 2: External grid disturbance (confidence: 0.45)', 'Selected Hypothesis 1 based on evidence weight and rule consistency'], evidence: [], rules: [], knowledge: [], expanded: false },
      { name: 'Confidence Calculation', description: 'Multi-factor confidence calculation', details: ['Evidence quality score: 0.88 (high)', 'Knowledge relevance score: 0.85 (high)', 'Rule consistency score: 0.91 (very high)', 'Final confidence: 0.87'], evidence: [], rules: [], knowledge: [], expanded: false },
    ],
    confidence: 0.87,
    confidenceBreakdown: [
      { label: 'Evidence Quality', value: 0.88 }, { label: 'Knowledge Relevance', value: 0.85 },
      { label: 'Rule Consistency', value: 0.91 }, { label: 'Historical Accuracy', value: 0.84 },
    ],
    alternatives: [
      { title: 'Replace TF-102 immediately', confidence: 0.55, reason: 'Overly conservative - evidence suggests degradation is still in early stages' },
      { title: 'Continue monitoring without action', confidence: 0.30, reason: 'Too risky - DGA levels indicate active degradation that requires intervention' },
    ],
    createdAt: '2026-06-28T11:00:00Z',
  },
  {
    id: 'EXP-002', recommendationId: 'R-006', recommendationTitle: 'Perform Full Capacity Test on BB-101',
    narrative: `This recommendation was triggered by a capacity degradation alarm on BB-101.

The evidence showed an 18% capacity loss compared to baseline, confirmed by Q2 benchmark data. Battery safety guidelines (DOC-006) recommend full capacity testing when degradation exceeds 15%. The BMS firmware update may resolve the issue.`,
    stages: [
      { name: 'Customer Data Collection', description: 'Battery monitoring system detected capacity degradation', details: ['EV-008: BB-101 capacity loss report showing 18% degradation', 'EV-014: Q2 battery benchmark data'], evidence: [{ id: 'EV-008', title: 'BB-101 Capacity Loss', confidence: 0.82 }, { id: 'EV-014', title: 'Battery Benchmark Q2', confidence: 0.93 }], rules: [], knowledge: [], expanded: false },
      { name: 'Evidence Generation', description: 'Anomaly detection identified capacity degradation trend', details: ['Capacity declining 2-3% per month over last 6 months', 'Cell voltage imbalance detected in Module 4'], evidence: [], rules: [], knowledge: [], expanded: false },
      { name: 'Knowledge Retrieved', description: 'Battery maintenance documentation retrieved', details: ['DOC-006: Battery Storage Safety Guidelines v2'], evidence: [], rules: [], knowledge: [{ id: 'DOC-006', title: 'Battery Storage Safety Guidelines' }], expanded: false },
      { name: 'Business Rules Applied', description: 'Capacity loss threshold rules evaluated', details: ['RUL-010: Capacity loss >15% requires full test â†’ TRIGGERED'], evidence: [], rules: [{ id: 'RUL-010', description: 'Capacity loss >15% requires full test', triggered: true }], knowledge: [], expanded: false },
      { name: 'Reasoning Process', description: 'Analogical reasoning based on historical battery degradation patterns', details: ['Compared degradation curve with 3 historical cases', 'Pattern matches BMS calibration issue (60% probability)', 'Pattern matches cell degradation (30% probability)'], evidence: [], rules: [], knowledge: [], expanded: false },
      { name: 'Confidence Calculation', description: 'Confidence based on pattern match quality', details: ['Pattern match confidence: 0.78', 'Evidence quality: 0.88', 'Rule clarity: 0.95', 'Final confidence: 0.82'], evidence: [], rules: [], knowledge: [], expanded: false },
    ],
    confidence: 0.82,
    confidenceBreakdown: [
      { label: 'Evidence Quality', value: 0.88 }, { label: 'Pattern Match', value: 0.78 },
      { label: 'Rule Clarity', value: 0.95 }, { label: 'Historical Accuracy', value: 0.72 },
    ],
    alternatives: [
      { title: 'Replace BB-101 battery cells', confidence: 0.50, reason: 'Premature - capacity test needed first to determine root cause' },
      { title: 'Defer action for 3 months', confidence: 0.35, reason: 'Unacceptable risk - degradation accelerating month-over-month' },
    ],
    createdAt: '2026-06-27T12:00:00Z',
  },
]

export interface ExplainabilityService {
  getByRecommendationId(recId: string): Promise<Explanation | undefined>
  list(params: { page: number; limit: number }): Promise<{ items: Explanation[]; total: number }>
}

export function useExplainabilityService(): ExplainabilityService {
  return {
    async getByRecommendationId(recId) {
      return mockExplanations.find((e) => e.recommendationId === recId)
    },
    async list({ page, limit }) {
      const total = mockExplanations.length
      const start = (page - 1) * limit
      return { items: mockExplanations.slice(start, start + limit), total }
    },
  }
}

