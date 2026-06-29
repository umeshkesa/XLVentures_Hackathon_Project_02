import type { Interaction } from '@/types/interactions'

const mockInteractions: Interaction[] = [
  { id: 'INT-001', type: 'email', subject: 'Q3 Maintenance Schedule Confirmation', content: 'Please confirm the maintenance schedule for Q3 as discussed in our last meeting. We need to align with the production downtime window.', date: new Date(Date.now() - 3600000 * 2).toISOString(), agent: 'Sarah Chen', customerId: 'C-1001', customerName: 'NovaGrid Energy', relatedAssets: ['SP-101', 'SP-102'], relatedEvidence: ['EV-001'], relatedRecommendations: ['R-001'], attachments: [{ name: 'maintenance_schedule_q3.pdf', url: '#', size: 245000 }], status: 'resolved' },
  { id: 'INT-002', type: 'complaint', subject: 'Voltage Fluctuation Incident Report', content: 'Customer reports voltage fluctuations in Zone 4 over the past 48 hours. This is causing production equipment to trip.', date: new Date(Date.now() - 3600000 * 5).toISOString(), agent: 'Mike Rivera', customerId: 'C-1002', customerName: 'PeakVolt Systems', relatedAssets: ['TF-101', 'TF-102', 'SN-105'], relatedEvidence: ['EV-002', 'EV-003'], relatedRecommendations: ['R-002', 'R-003'], attachments: [], status: 'escalated' },
  { id: 'INT-003', type: 'feedback', subject: 'New Dashboard Feedback', content: 'The new energy monitoring dashboard is excellent. We appreciate the real-time visibility into our solar farm performance.', date: new Date(Date.now() - 3600000 * 8).toISOString(), agent: 'Emily Park', customerId: 'C-1003', customerName: 'GreenCircuit Inc', relatedAssets: ['SP-103', 'SP-104'], relatedEvidence: ['EV-004'], relatedRecommendations: [], attachments: [{ name: 'dashboard_screenshot.png', url: '#', size: 1800000 }], status: 'resolved' },
  { id: 'INT-004', type: 'service_request', subject: 'Emergency Transformer Inspection Required', content: 'Requesting emergency inspection of Transformer TF-201 after unusual noise reported by site operators.', date: new Date(Date.now() - 3600000 * 12).toISOString(), agent: 'David Kim', customerId: 'C-1004', customerName: 'PowerLine Dynamics', relatedAssets: ['TF-201'], relatedEvidence: ['EV-005'], relatedRecommendations: ['R-004'], attachments: [], status: 'pending' },
  { id: 'INT-005', type: 'meeting', subject: 'Quarterly Business Review - Q2 2026', content: 'Agenda: SLA performance review, new project pipeline, contract renewal discussion, and upcoming technology upgrades.', date: new Date(Date.now() - 86400000).toISOString(), agent: 'Lisa Wang', customerId: 'C-1005', customerName: 'Solaris Utilities', relatedAssets: ['SP-105', 'WT-101', 'BB-101'], relatedEvidence: ['EV-006', 'EV-007', 'EV-008'], relatedRecommendations: ['R-005', 'R-006'], attachments: [{ name: 'Q2_2026_Review.pptx', url: '#', size: 5200000 }, { name: 'SLA_Report_Q2.pdf', url: '#', size: 890000 }], status: 'resolved' },
  { id: 'INT-006', type: 'call_transcript', subject: 'Technical Support Call - Inverter Error', content: 'Call transcript: Customer reporting inverter error code E-47 on Solar Panel Array 3. Remote diagnostics initiated.', date: new Date(Date.now() - 86400000 * 2).toISOString(), agent: 'John Smith', customerId: 'C-1001', customerName: 'NovaGrid Energy', relatedAssets: ['SP-106'], relatedEvidence: ['EV-009'], relatedRecommendations: [], attachments: [{ name: 'call_transcript_20260627.txt', url: '#', size: 12000 }], status: 'resolved' },
  { id: 'INT-007', type: 'crm_update', subject: 'Contract Renewal Opportunity', content: 'CRM Update: Customer expressed interest in upgrading to Enterprise SLA tier. Follow-up scheduled for next week.', date: new Date(Date.now() - 86400000 * 3).toISOString(), agent: 'Sarah Chen', customerId: 'C-1006', customerName: 'GridCore Solutions', relatedAssets: [], relatedEvidence: ['EV-010'], relatedRecommendations: ['R-007'], attachments: [], status: 'resolved' },
  { id: 'INT-008', type: 'chat', subject: 'Quick Query - Billing Discrepancy', content: 'Chat conversation regarding billing discrepancy for May 2026. Customer was overcharged by $2,847. Refund processed.', date: new Date(Date.now() - 86400000 * 4).toISOString(), agent: 'Emily Park', customerId: 'C-1007', customerName: 'VoltAmp Industries', relatedAssets: [], relatedEvidence: [], relatedRecommendations: [], attachments: [], status: 'resolved' },
  { id: 'INT-009', type: 'complaint', subject: 'Service Response Time Exceeded', content: 'Formal complaint: Emergency response took 45 minutes instead of the 15-minute SLA commitment. Customer demands compensation.', date: new Date(Date.now() - 86400000 * 5).toISOString(), agent: 'Mike Rivera', customerId: 'C-1008', customerName: 'EcoWatt Partners', relatedAssets: ['TF-202'], relatedEvidence: ['EV-011'], relatedRecommendations: ['R-008'], attachments: [], status: 'escalated' },
  { id: 'INT-010', type: 'feedback', subject: 'Predictive Maintenance Program', content: 'Excellent experience with the new predictive maintenance program. It helped us identify a potential failure before it occurred.', date: new Date(Date.now() - 86400000 * 7).toISOString(), agent: 'Lisa Wang', customerId: 'C-1009', customerName: 'TerraVolt Corp', relatedAssets: ['WT-102', 'WT-103'], relatedEvidence: ['EV-012'], relatedRecommendations: ['R-009'], attachments: [], status: 'resolved' },
  { id: 'INT-011', type: 'service_request', subject: 'New Sensor Installation Request', content: 'Requesting installation of additional temperature sensors in Server Room B and Cooling Tower 3.', date: new Date(Date.now() - 86400000 * 8).toISOString(), agent: 'David Kim', customerId: 'C-1010', customerName: 'BlueCurrent Ltd', relatedAssets: ['SN-201', 'SN-202'], relatedEvidence: [], relatedRecommendations: ['R-010'], attachments: [{ name: 'sensor_layout_request.pdf', url: '#', size: 340000 }], status: 'pending' },
  { id: 'INT-012', type: 'email', subject: 'Monthly Performance Report - June', content: 'Please find attached the monthly performance report for June 2026. Total energy output: 4.2 GWh. Efficiency: 94.3%.', date: new Date(Date.now() - 86400000 * 10).toISOString(), agent: 'Sarah Chen', customerId: 'C-1001', customerName: 'NovaGrid Energy', relatedAssets: ['SP-101', 'SP-102', 'SP-103'], relatedEvidence: ['EV-013', 'EV-014'], relatedRecommendations: ['R-011'], attachments: [{ name: 'monthly_report_june_2026.pdf', url: '#', size: 1200000 }], status: 'resolved' },
]

export interface InteractionService {
  list(params: { type?: string; status?: string; search?: string; customerId?: string; page: number; limit: number }): Promise<{ items: Interaction[]; total: number }>
  getById(id: string): Promise<Interaction | undefined>
  getTimeline(params: { customerId?: string; type?: string }): Promise<{ groups: { date: string; interactions: Interaction[] }[] }>
}

export function useInteractionService(): InteractionService {
  return {
    async list({ type, status, search, customerId, page, limit }) {
      let filtered = [...mockInteractions]
      if (type) filtered = filtered.filter((i) => i.type === type)
      if (status) filtered = filtered.filter((i) => i.status === status)
      if (customerId) filtered = filtered.filter((i) => i.customerId === customerId)
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter((i) =>
          i.subject.toLowerCase().includes(q) || i.content.toLowerCase().includes(q) || i.customerName.toLowerCase().includes(q),
        )
      }
      filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      const total = filtered.length
      const start = (page - 1) * limit
      return { items: filtered.slice(start, start + limit), total }
    },
    async getById(id) {
      return mockInteractions.find((i) => i.id === id)
    },
    async getTimeline({ customerId, type }) {
      let filtered = [...mockInteractions]
      if (customerId) filtered = filtered.filter((i) => i.customerId === customerId)
      if (type) filtered = filtered.filter((i) => i.type === type)
      filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      const groups: Record<string, Interaction[]> = {}
      for (const item of filtered) {
        const day = new Date(item.date).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })
        if (!groups[day]) groups[day] = []
        groups[day].push(item)
      }
      return { groups: Object.entries(groups).map(([date, interactions]) => ({ date, interactions })) }
    },
  }
}
