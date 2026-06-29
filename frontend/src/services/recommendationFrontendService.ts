import type { RecommendationItem, RecommendationSummary } from '@/types/recommendations'

const mockRecs: RecommendationItem[] = [
  { id: 'R-001', title: 'Schedule TF-102 Internal Inspection', description: 'Based on DGA analysis showing elevated hydrogen (85ppm) and methane (42ppm), schedule an internal inspection of TF-102 within 7 days to assess winding insulation condition.', priority: 'critical', confidence: 0.87, businessImpact: 'Prevents catastrophic transformer failure affecting 25% of PeakVolt production capacity', riskLevel: 'high', estimatedCost: 45000, estimatedSavings: 320000, timeline: '7 days', source: 'reasoning_engine', status: 'active', reasoningId: 'RSN-001', evidenceIds: ['EV-002', 'EV-003'], ruleIds: ['RUL-002', 'RUL-003', 'RUL-004'], knowledgeIds: ['DOC-003', 'DOC-007'], assetIds: ['TF-102'], customerIds: ['C-1002'], actions: [
    { id: 'A-001', description: 'Contact Siemens service team for TF-102 inspection', assignedTo: 'Maintenance Manager', deadline: '2026-07-05', status: 'in_progress' },
    { id: 'A-002', description: 'Order replacement gaskets and seals', assignedTo: 'Procurement', deadline: '2026-07-03', status: 'pending' },
  ], createdAt: '2026-06-28T11:00:00Z', updatedAt: '2026-06-28T11:00:00Z' },
  { id: 'R-002', title: 'Deploy Voltage Stabilization Equipment at Zone 4', description: 'Install dynamic voltage restorer (DVR) at PeakVolt Zone 4 to mitigate voltage fluctuations and protect production equipment from further damage.', priority: 'high', confidence: 0.82, businessImpact: 'Eliminates production downtime caused by voltage fluctuations, saving ~$50K per incident', riskLevel: 'medium', estimatedCost: 185000, estimatedSavings: 600000, timeline: '30 days', source: 'reasoning_engine', status: 'pending_approval', reasoningId: 'RSN-001', evidenceIds: ['EV-002'], ruleIds: ['RUL-002'], knowledgeIds: ['DOC-003'], assetIds: ['TF-101', 'TF-102', 'SN-105'], customerIds: ['C-1002'], actions: [
    { id: 'A-003', description: 'Submit engineering change request for DVR installation', assignedTo: 'Engineering Lead', deadline: '2026-07-14', status: 'pending' },
  ], createdAt: '2026-06-28T11:30:00Z', updatedAt: '2026-06-28T11:30:00Z' },
  { id: 'R-003', title: 'Oil Reclamation for Transformer TF-102', description: 'Perform oil reclamation/filtration on TF-102 to reduce moisture content and acidity levels. Improves dielectric strength and extends transformer life.', priority: 'high', confidence: 0.85, businessImpact: 'Extends TF-102 life by 3-5 years. Avoids $500K replacement cost.', riskLevel: 'low', estimatedCost: 28000, estimatedSavings: 500000, timeline: '14 days', source: 'reasoning_engine', status: 'approved', reasoningId: 'RSN-001', evidenceIds: ['EV-003'], ruleIds: ['RUL-004'], knowledgeIds: ['DOC-003', 'DOC-007'], assetIds: ['TF-102'], customerIds: ['C-1002'], actions: [
    { id: 'A-004', description: 'Schedule oil reclamation with lab services', assignedTo: 'Maintenance Lead', deadline: '2026-07-07', status: 'completed', completedAt: '2026-06-29T09:00:00Z' },
    { id: 'A-005', description: 'Post-reclamation DGA analysis', assignedTo: 'Lab Services', deadline: '2026-07-14', status: 'pending' },
  ], createdAt: '2026-06-28T12:00:00Z', updatedAt: '2026-06-29T09:00:00Z' },
  { id: 'R-004', title: 'Deploy Transformer TF-201 Acoustic Monitoring', description: 'Install permanent acoustic monitoring system on TF-201 following unusual noise detection. Enables early warning of winding loosening.', priority: 'critical', confidence: 0.78, businessImpact: 'Prevents catastrophic failure of TF-201. Early warning allows planned maintenance vs emergency replacement.', riskLevel: 'medium', estimatedCost: 35000, estimatedSavings: 450000, timeline: '14 days', source: 'reasoning_engine', status: 'active', reasoningId: 'RSN-002', evidenceIds: ['EV-005'], ruleIds: ['RUL-006'], knowledgeIds: ['DOC-007'], assetIds: ['TF-201'], customerIds: ['C-1004'], actions: [
    { id: 'A-006', description: 'Procure acoustic monitoring system', assignedTo: 'Procurement', deadline: '2026-07-08', status: 'in_progress' },
    { id: 'A-007', description: 'Schedule installation with electrical team', assignedTo: 'Engineering Lead', deadline: '2026-07-12', status: 'pending' },
  ], createdAt: '2026-06-29T08:00:00Z', updatedAt: '2026-06-29T08:00:00Z' },
  { id: 'R-005', title: 'Install Backup Generator Fuel Monitoring System', description: 'Implement automated fuel level monitoring for backup generators at Solaris facility. Addresses gap identified in grid failure readiness assessment.', priority: 'medium', confidence: 0.92, businessImpact: 'Ensures backup power availability during grid failures. Regulatory compliance requirement.', riskLevel: 'low', estimatedCost: 12000, estimatedSavings: 0, timeline: '21 days', source: 'reasoning_engine', status: 'active', reasoningId: 'RSN-002', evidenceIds: ['EV-007'], ruleIds: ['RUL-009'], knowledgeIds: ['DOC-005'], assetIds: ['BB-101'], customerIds: ['C-1005'], actions: [
    { id: 'A-008', description: 'Specify fuel monitoring system requirements', assignedTo: 'Engineering Lead', deadline: '2026-07-10', status: 'pending' },
  ], createdAt: '2026-06-25T10:00:00Z', updatedAt: '2026-06-25T10:00:00Z' },
  { id: 'R-006', title: 'Perform Full Capacity Test on BB-101', description: 'Execute full charge/discharge capacity test on battery storage BB-101 to quantify 18% capacity loss and determine if BMS firmware update or cell replacement is needed.', priority: 'high', confidence: 0.82, businessImpact: 'Restores BB-101 to rated capacity. Extends useful life. Avoids $200K early replacement cost.', riskLevel: 'medium', estimatedCost: 15000, estimatedSavings: 200000, timeline: '7 days', source: 'reasoning_engine', status: 'executed', reasoningId: 'RSN-004', evidenceIds: ['EV-008', 'EV-014'], ruleIds: ['RUL-010'], knowledgeIds: ['DOC-006'], assetIds: ['BB-101'], customerIds: ['C-1005'], actions: [
    { id: 'A-009', description: 'Schedule capacity test with battery team', assignedTo: 'Maintenance Lead', deadline: '2026-07-01', status: 'completed', completedAt: '2026-06-30T10:00:00Z' },
  ], createdAt: '2026-06-27T12:00:00Z', updatedAt: '2026-06-30T10:00:00Z' },
  { id: 'R-007', title: 'Prepare Enterprise SLA Proposal for GridCore', description: 'Develop enterprise SLA tier proposal for GridCore Solutions. Revenue opportunity: $120K/yr. Include premium response times and dedicated support.', priority: 'low', confidence: 0.79, businessImpact: 'New revenue stream: $120K annual. Strengthens customer relationship.', riskLevel: 'low', estimatedCost: 5000, estimatedSavings: 120000, timeline: '45 days', source: 'customer_feedback', status: 'draft', evidenceIds: ['EV-010'], ruleIds: [], knowledgeIds: ['DOC-009'], assetIds: [], customerIds: ['C-1006'], actions: [], createdAt: '2026-06-26T11:00:00Z', updatedAt: '2026-06-26T11:00:00Z' },
  { id: 'R-008', title: 'Process EcoWatt SLA Breach Compensation', description: 'Process compensation claim for EcoWatt following 45-minute emergency response (exceeded 15-min SLA). Calculate service credit per SLA terms and implement corrective actions.', priority: 'high', confidence: 0.91, businessImpact: 'Retains customer relationship. SLA compliance improvement needed.', riskLevel: 'medium', estimatedCost: 25000, estimatedSavings: 150000, timeline: '14 days', source: 'compliance', status: 'pending_approval', evidenceIds: ['EV-011'], ruleIds: ['RUL-012', 'RUL-013'], knowledgeIds: ['DOC-009'], assetIds: ['TF-202'], customerIds: ['C-1008'], actions: [
    { id: 'A-010', description: 'Calculate service credit amount', assignedTo: 'Customer Success', deadline: '2026-07-05', status: 'pending' },
    { id: 'A-011', description: 'Implement dispatch process improvements', assignedTo: 'Operations Manager', deadline: '2026-07-14', status: 'pending' },
  ], createdAt: '2026-06-25T09:00:00Z', updatedAt: '2026-06-25T09:00:00Z' },
  { id: 'R-009', title: 'Schedule WT-102 Bearing Inspection', description: 'Schedule bearing inspection for wind turbine WT-102 within 14 days. Bearing wear at 72% of failure threshold. Order replacement bearings proactively.', priority: 'medium', confidence: 0.83, businessImpact: 'Prevents unplanned WT-102 downtime. Scheduled replacement costs 60% less than emergency repair.', riskLevel: 'medium', estimatedCost: 18500, estimatedSavings: 95000, timeline: '14 days', source: 'reasoning_engine', status: 'active', reasoningId: 'RSN-003', evidenceIds: ['EV-012'], ruleIds: ['RUL-014'], knowledgeIds: ['DOC-002', 'DOC-010'], assetIds: ['WT-102'], customerIds: ['C-1009'], actions: [
    { id: 'A-012', description: 'Schedule bearing inspection', assignedTo: 'Maintenance Lead', deadline: '2026-07-08', status: 'pending' },
    { id: 'A-013', description: 'Order replacement bearings', assignedTo: 'Procurement', deadline: '2026-07-05', status: 'in_progress' },
  ], createdAt: '2026-06-24T14:00:00Z', updatedAt: '2026-06-24T14:00:00Z' },
  { id: 'R-010', title: 'Install Additional Temperature Sensors at BlueCurrent', description: 'Install temperature sensors in Server Room B and Cooling Tower 3 as requested. Enables better thermal monitoring and predictive maintenance.', priority: 'low', confidence: 0.72, businessImpact: 'Improved monitoring reduces risk of overheating incidents.', riskLevel: 'low', estimatedCost: 8500, estimatedSavings: 30000, timeline: '30 days', source: 'customer_feedback', status: 'draft', evidenceIds: [], ruleIds: [], knowledgeIds: [], assetIds: ['SN-201', 'SN-202'], customerIds: ['C-1010'], actions: [
    { id: 'A-014', description: 'Create sensor installation work order', assignedTo: 'Engineering Lead', deadline: '2026-07-20', status: 'pending' },
  ], createdAt: '2026-06-23T10:00:00Z', updatedAt: '2026-06-23T10:00:00Z' },
  { id: 'R-011', title: 'Implement NovaGrid SLA Improvement Plan', description: 'Develop and implement plan to improve NovaGrid SLA performance from 99.3% to 99.9% target. Focus areas: response time reduction and proactive monitoring.', priority: 'medium', confidence: 0.94, businessImpact: 'Retains NovaGrid Premium SLA ($200K/yr). Avoids service credit penalties.', riskLevel: 'low', estimatedCost: 35000, estimatedSavings: 200000, timeline: '60 days', source: 'reasoning_engine', status: 'approved', reasoningId: 'RSN-007', evidenceIds: ['EV-013', 'EV-014'], ruleIds: ['RUL-007'], knowledgeIds: ['DOC-001', 'DOC-008'], assetIds: ['SP-101', 'SP-102', 'SP-103'], customerIds: ['C-1001'], actions: [
    { id: 'A-015', description: 'Create SLA improvement roadmap', assignedTo: 'Operations Manager', deadline: '2026-07-15', status: 'in_progress' },
    { id: 'A-016', description: 'Implement proactive monitoring alerts', assignedTo: 'Engineering Lead', deadline: '2026-08-01', status: 'pending' },
  ], createdAt: '2026-06-23T09:00:00Z', updatedAt: '2026-06-23T09:00:00Z' },
]

export interface RecommendationService {
  list(params: { status?: string; priority?: string; source?: string; search?: string; page: number; limit: number }): Promise<{ items: RecommendationItem[]; total: number }>
  getById(id: string): Promise<RecommendationItem | undefined>
  getSummary(): Promise<RecommendationSummary>
}

export function useRecommendationService(): RecommendationService {
  return {
    async list({ status, priority, source, search, page, limit }) {
      let filtered = [...mockRecs]
      if (status) filtered = filtered.filter((r) => r.status === status)
      if (priority) filtered = filtered.filter((r) => r.priority === priority)
      if (source) filtered = filtered.filter((r) => r.source === source)
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter((r) => r.title.toLowerCase().includes(q) || r.description.toLowerCase().includes(q))
      }
      const total = filtered.length
      const start = (page - 1) * limit
      return { items: filtered.slice(start, start + limit), total }
    },
    async getById(id) { return mockRecs.find((r) => r.id === id) },
    async getSummary() {
      return {
        active: mockRecs.filter((r) => r.status === 'active').length,
        pendingApproval: mockRecs.filter((r) => r.status === 'pending_approval').length,
        approved: mockRecs.filter((r) => r.status === 'approved').length,
        rejected: mockRecs.filter((r) => r.status === 'rejected').length,
        executed: mockRecs.filter((r) => r.status === 'executed').length,
        draft: mockRecs.filter((r) => r.status === 'draft').length,
        totalCost: mockRecs.reduce((a, r) => a + r.estimatedCost, 0),
        totalSavings: mockRecs.reduce((a, r) => a + r.estimatedSavings, 0),
      }
    },
  }
}
