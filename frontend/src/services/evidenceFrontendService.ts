import type { EvidenceItem, TraceabilityStep } from '@/types/evidence'

const mockEvidence: EvidenceItem[] = [
  { id: 'EV-001', type: 'sensor', status: 'fused', priority: 'critical', severity: 'high', title: 'Solar Panel Array 3 - Voltage Drop', description: 'Voltage drop from 480V to 412V detected on Solar Panel Array 3 at NovaGrid facility. Duration: 14 minutes.', source: 'SCADA System', sourceType: 'sensor', domain: 'energy', confidence: 0.92, qualityScore: 0.88, freshness: 0.95, completeness: 0.85, consistency: 0.91, reliability: 0.89, timestamp: '2026-06-28T14:23:00Z', tags: ['solar', 'voltage', 'scada'], relatedCustomers: ['C-1001'], relatedAssets: ['SP-101', 'SP-102'], relatedKnowledge: ['DOC-001'], relatedRules: ['RUL-001'], relatedRecommendations: ['R-001'] },
  { id: 'EV-002', type: 'incident', status: 'analyzed', priority: 'high', severity: 'critical', title: 'Voltage Fluctuation - PeakVolt Zone 4', description: 'Customer reported voltage fluctuations in Zone 4 over 48 hours. Production equipment tripped 3 times.', source: 'PeakVolt Systems', sourceType: 'customer_report', domain: 'energy', confidence: 0.85, qualityScore: 0.79, freshness: 0.60, completeness: 0.72, consistency: 0.80, reliability: 0.82, timestamp: '2026-06-28T10:15:00Z', tags: ['voltage', 'fluctuation', 'complaint'], relatedCustomers: ['C-1002'], relatedAssets: ['TF-101', 'TF-102', 'SN-105'], relatedKnowledge: ['DOC-003'], relatedRules: ['RUL-002', 'RUL-003'], relatedRecommendations: ['R-002', 'R-003'] },
  { id: 'EV-003', type: 'maintenance', status: 'verified', priority: 'medium', severity: 'medium', title: 'Transformer TF-102 Oil Sample Analysis', description: 'Routine DGA on TF-102 shows elevated hydrogen (85 ppm) and methane (42 ppm). Partial discharge suspected.', source: 'Lab Analysis Report', sourceType: 'laboratory', domain: 'energy', confidence: 0.88, qualityScore: 0.91, freshness: 0.70, completeness: 0.90, consistency: 0.86, reliability: 0.93, timestamp: '2026-06-27T09:00:00Z', tags: ['transformer', 'dga', 'oil-analysis'], relatedCustomers: ['C-1002'], relatedAssets: ['TF-102'], relatedKnowledge: ['DOC-003', 'DOC-007'], relatedRules: ['RUL-004'], relatedRecommendations: ['R-003'] },
  { id: 'EV-004', type: 'compliance', status: 'fused', priority: 'medium', severity: 'info', title: 'ISO 50001 Audit - Q2 2026 Pass', description: 'Quarterly ISO 50001 compliance audit passed with 94% score. Minor observation on documentation timeliness.', source: 'Internal Audit', sourceType: 'compliance', domain: 'energy', confidence: 0.96, qualityScore: 0.93, freshness: 0.85, completeness: 0.95, consistency: 0.94, reliability: 0.97, timestamp: '2026-06-25T16:00:00Z', tags: ['compliance', 'iso-50001', 'audit'], relatedCustomers: ['C-1001', 'C-1003'], relatedAssets: [], relatedKnowledge: ['DOC-004'], relatedRules: ['RUL-005'], relatedRecommendations: [] },
  { id: 'EV-005', type: 'alarm', status: 'collected', priority: 'critical', severity: 'critical', title: 'Transformer TF-201 Unusual Noise Alert', description: 'Acoustic sensor detected unusual noise pattern from TF-201. Frequency analysis suggests possible winding loosening.', source: 'Acoustic Monitoring System', sourceType: 'sensor', domain: 'energy', confidence: 0.78, qualityScore: 0.72, freshness: 0.98, completeness: 0.65, consistency: 0.75, reliability: 0.80, timestamp: '2026-06-29T07:45:00Z', tags: ['transformer', 'acoustic', 'alert', 'tf-201'], relatedCustomers: ['C-1004'], relatedAssets: ['TF-201'], relatedKnowledge: ['DOC-007'], relatedRules: ['RUL-006'], relatedRecommendations: ['R-004'] },
  { id: 'EV-006', type: 'customer', status: 'fused', priority: 'high', severity: 'medium', title: 'Solaris Utilities - QBR Meeting Minutes', description: 'Quarterly Business Review with Solaris Utilities. Positive feedback on SLA performance. New projects discussed.', source: 'Customer Meeting', sourceType: 'meeting', domain: 'general', confidence: 0.90, qualityScore: 0.86, freshness: 0.90, completeness: 0.88, consistency: 0.92, reliability: 0.90, timestamp: '2026-06-28T08:00:00Z', tags: ['customer', 'qbr', 'meeting', 'solaris'], relatedCustomers: ['C-1005'], relatedAssets: ['SP-105', 'WT-101', 'BB-101'], relatedKnowledge: ['DOC-008'], relatedRules: ['RUL-007', 'RUL-008'], relatedRecommendations: ['R-005', 'R-006'] },
  { id: 'EV-007', type: 'knowledge', status: 'analyzed', priority: 'medium', severity: 'info', title: 'Grid Emergency Response Drill Results', description: 'Tabletop exercise based on DOC-005 (Grid Failure Playbook) completed. All teams passed with >85% effectiveness.', source: 'Training Records', sourceType: 'exercise', domain: 'general', confidence: 0.94, qualityScore: 0.90, freshness: 0.80, completeness: 0.92, consistency: 0.93, reliability: 0.95, timestamp: '2026-06-24T15:30:00Z', tags: ['emergency', 'drill', 'grid-failure', 'training'], relatedCustomers: [], relatedAssets: ['TF-101', 'BB-101'], relatedKnowledge: ['DOC-005'], relatedRules: ['RUL-009'], relatedRecommendations: ['R-004'] },
  { id: 'EV-008', type: 'recommendation', status: 'analyzed', priority: 'high', severity: 'high', title: 'Battery Storage Capacity Degradation Warning', description: 'BB-101 shows 18% capacity loss vs baseline. Recommended: full capacity test and BMS firmware update.', source: 'ADIP Recommendation Engine', sourceType: 'system', domain: 'energy', confidence: 0.82, qualityScore: 0.78, freshness: 0.88, completeness: 0.75, consistency: 0.80, reliability: 0.85, timestamp: '2026-06-27T11:00:00Z', tags: ['battery', 'degradation', 'recommendation', 'bb-101'], relatedCustomers: ['C-1005'], relatedAssets: ['BB-101'], relatedKnowledge: ['DOC-006'], relatedRules: ['RUL-010'], relatedRecommendations: ['R-006'] },
  { id: 'EV-009', type: 'sensor', status: 'verified', priority: 'medium', severity: 'medium', title: 'Solar Panel SP-106 Inverter Error E-47', description: 'Inverter on SP-106 reporting error code E-47 (DC arc fault). Remote reset attempted - persistent fault.', source: 'Inverter Monitoring System', sourceType: 'sensor', domain: 'energy', confidence: 0.87, qualityScore: 0.84, freshness: 0.92, completeness: 0.80, consistency: 0.88, reliability: 0.86, timestamp: '2026-06-27T14:00:00Z', tags: ['solar', 'inverter', 'error', 'sp-106'], relatedCustomers: ['C-1001'], relatedAssets: ['SP-106'], relatedKnowledge: ['DOC-001'], relatedRules: ['RUL-011'], relatedRecommendations: [] },
  { id: 'EV-010', type: 'customer', status: 'verified', priority: 'low', severity: 'info', title: 'GridCore Solutions - Enterprise Tier Interest', description: 'CRM Update: GridCore expressed interest in upgrading to Enterprise SLA tier. Revenue opportunity: $120K/yr.', source: 'CRM System', sourceType: 'business', domain: 'general', confidence: 0.79, qualityScore: 0.82, freshness: 0.85, completeness: 0.78, consistency: 0.81, reliability: 0.77, timestamp: '2026-06-26T10:30:00Z', tags: ['crm', 'upsell', 'enterprise', 'opportunity'], relatedCustomers: ['C-1006'], relatedAssets: [], relatedKnowledge: ['DOC-009'], relatedRules: [], relatedRecommendations: ['R-007'] },
  { id: 'EV-011', type: 'incident', status: 'collected', priority: 'high', severity: 'high', title: 'EcoWatt - SLA Breach Incident', description: 'Emergency response time 45 minutes vs 15-minute SLA commitment. Formal complaint filed. Compensation required.', source: 'EcoWatt Partners', sourceType: 'customer_report', domain: 'energy', confidence: 0.91, qualityScore: 0.87, freshness: 0.65, completeness: 0.85, consistency: 0.90, reliability: 0.92, timestamp: '2026-06-25T08:00:00Z', tags: ['sla', 'breach', 'complaint', 'ecowatt'], relatedCustomers: ['C-1008'], relatedAssets: ['TF-202'], relatedKnowledge: ['DOC-009'], relatedRules: ['RUL-012', 'RUL-013'], relatedRecommendations: ['R-008'] },
  { id: 'EV-012', type: 'maintenance', status: 'fused', priority: 'medium', severity: 'medium', title: 'Wind Turbine WT-102 Predictive Maintenance', description: 'Predictive model shows bearing wear on WT-102 at 72% of failure threshold. Recommend inspection within 2 weeks.', source: 'ADIP Predictive Maintenance', sourceType: 'system', domain: 'energy', confidence: 0.83, qualityScore: 0.80, freshness: 0.75, completeness: 0.82, consistency: 0.85, reliability: 0.81, timestamp: '2026-06-24T13:00:00Z', tags: ['wind', 'predictive', 'maintenance', 'wt-102'], relatedCustomers: ['C-1009'], relatedAssets: ['WT-102'], relatedKnowledge: ['DOC-002', 'DOC-010'], relatedRules: ['RUL-014'], relatedRecommendations: ['R-009'] },
  { id: 'EV-013', type: 'sensor', status: 'fused', priority: 'low', severity: 'info', title: 'NovaGrid - Monthly Performance Summary', description: 'June 2026: Total output 4.2 GWh, Efficiency 94.3%, Availability 98.7%, Downtime 9.4 hours.', source: 'Energy Management System', sourceType: 'sensor', domain: 'energy', confidence: 0.97, qualityScore: 0.95, freshness: 0.82, completeness: 0.96, consistency: 0.96, reliability: 0.98, timestamp: '2026-06-23T09:00:00Z', tags: ['solar', 'performance', 'monthly', 'summary'], relatedCustomers: ['C-1001'], relatedAssets: ['SP-101', 'SP-102', 'SP-103'], relatedKnowledge: ['DOC-001', 'DOC-008'], relatedRules: [], relatedRecommendations: ['R-011'] },
  { id: 'EV-014', type: 'report', status: 'verified', priority: 'low', severity: 'info', title: 'Battery Storage Performance Benchmark Q2', description: 'Quarterly benchmark report for all battery storage assets. Average efficiency: 89.2%. Cycle life tracking on track.', source: 'Asset Management', sourceType: 'report', domain: 'energy', confidence: 0.93, qualityScore: 0.91, freshness: 0.78, completeness: 0.93, consistency: 0.92, reliability: 0.94, timestamp: '2026-06-22T16:00:00Z', tags: ['battery', 'benchmark', 'performance', 'quarterly'], relatedCustomers: ['C-1001', 'C-1005'], relatedAssets: ['BB-101', 'BB-102'], relatedKnowledge: ['DOC-006'], relatedRules: ['RUL-015'], relatedRecommendations: [] },
]

export interface EvidenceFrontendService {
  list(params: { type?: string; status?: string; priority?: string; search?: string; page: number; limit: number }): Promise<{ items: EvidenceItem[]; total: number }>
  getById(id: string): Promise<EvidenceItem | undefined>
  getTraceability(evidenceId: string): Promise<TraceabilityStep[]>
}

export function useEvidenceFrontendService(): EvidenceFrontendService {
  return {
    async list({ type, status, priority, search, page, limit }) {
      let filtered = [...mockEvidence]
      if (type) filtered = filtered.filter((e) => e.type === type)
      if (status) filtered = filtered.filter((e) => e.status === status)
      if (priority) filtered = filtered.filter((e) => e.priority === priority)
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter((e) =>
          e.title.toLowerCase().includes(q) || e.description.toLowerCase().includes(q) || e.tags.some((t) => t.includes(q)),
        )
      }
      filtered.sort((a, b) => b.confidence - a.confidence)
      const total = filtered.length
      const start = (page - 1) * limit
      return { items: filtered.slice(start, start + limit), total }
    },
    async getById(id) {
      return mockEvidence.find((e) => e.id === id)
    },
    async getTraceability(evidenceId) {
      const evidence = mockEvidence.find((e) => e.id === evidenceId)
      if (!evidence) return []

      const steps: TraceabilityStep[] = [
        {
          stage: 'source',
          label: evidence.source,
          description: `Source type: ${evidence.sourceType}. Captured from ${evidence.domain} domain.`,
          timestamp: evidence.timestamp,
          status: 'completed',
        },
        {
          stage: 'evidence',
          label: evidence.title,
          description: `Evidence collected, ${evidence.status}. Quality score: ${(evidence.qualityScore * 100).toFixed(0)}%. Confidence: ${(evidence.confidence * 100).toFixed(0)}%.`,
          timestamp: evidence.timestamp,
          status: 'completed',
        },
      ]

      if (evidence.relatedKnowledge.length > 0) {
        steps.push({
          stage: 'knowledge',
          label: `${evidence.relatedKnowledge.length} related knowledge documents`,
          description: 'Knowledge documents linked to this evidence for context and analysis.',
          timestamp: evidence.timestamp,
          status: 'completed',
        })
      }

      if (evidence.relatedRules.length > 0) {
        steps.push({
          stage: 'rules',
          label: `${evidence.relatedRules.length} applicable rules`,
          description: 'Rules and policies applied during evidence evaluation.',
          timestamp: evidence.timestamp,
          status: 'completed',
        })
      }

      steps.push({
        stage: 'reasoning',
        label: 'Multi-strategy reasoning completed',
        description: `Reasoning engine evaluated evidence across ${evidence.relatedKnowledge.length + 1} knowledge sources and ${evidence.relatedRules.length} rules.`,
        timestamp: new Date(new Date(evidence.timestamp).getTime() + 3600000).toISOString(),
        status: 'completed',
      })

      if (evidence.relatedRecommendations.length > 0) {
        steps.push({
          stage: 'recommendation',
          label: `${evidence.relatedRecommendations.length} recommendations generated`,
          description: `Based on evidence analysis, ${evidence.relatedRecommendations.length} recommendations were generated and prioritized.`,
          timestamp: new Date(new Date(evidence.timestamp).getTime() + 7200000).toISOString(),
          status: evidence.relatedRecommendations.length > 0 ? 'completed' : 'pending',
        })
      }

      return steps
    },
  }
}
