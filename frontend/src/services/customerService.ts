import type { Customer, CustomerDetail, CustomerContract, SLAEntry, CustomerInteraction } from '@/types/customers'

const mockCustomers: Customer[] = Array.from({ length: 48 }, (_, i) => ({
  id: `C-${(1000 + i).toString()}`,
  companyName: [
    'NovaGrid Energy', 'PeakVolt Systems', 'GreenCircuit Inc', 'PowerLine Dynamics',
    'Solaris Utilities', 'WindStream Energy', 'GridCore Solutions', 'VoltAmp Industries',
    'EcoWatt Partners', 'TerraVolt Corp', 'BlueCurrent Ltd', 'ApexEnergy Group',
    'PrimeGrid Holdings', 'FusionWatt LLC', 'CircuitPro Services', 'Element Power',
    'Genesis Energy', 'Horizon Grid', 'InfraVolt Systems', 'JouleWorks Inc',
    'Kinetic Power Co', 'Lumen Energy', 'MagnaGrid Corp', 'NexGen Utilities',
    'OmniPower Group', 'PulseGrid Ltd', 'Quantum Energy', 'Resonance Power',
    'SustainaVolt', 'Triton Energy', 'Unity Grid', 'Vertex Power Systems',
    'WattSync Corp', 'Xenon Grid', 'Yield Energy', 'Zenith Power Holdings',
    'AetherGrid', 'BrightSpark Energy', 'CoreVolt Systems', 'DeltaGrid Corp',
    'Eclipse Power', 'FluxGrid Ltd', 'Gaia Energy', 'Helios Power Group',
    'IonGrid Systems', 'Jupiter Power', 'Kraken Energy', 'Lunar Grid Corp',
  ][i],
  industry: ['Energy', 'Utilities', 'Manufacturing', 'Technology', 'Infrastructure'][i % 5],
  location: ['Austin, TX', 'Denver, CO', 'Portland, OR', 'Phoenix, AZ', 'Atlanta, GA',
             'Chicago, IL', 'Seattle, WA', 'Boston, MA', 'Dallas, TX', 'San Jose, CA'][i % 10],
  contactPerson: `Contact ${i + 1}`,
  contactEmail: `contact${i + 1}@company${i + 1}.com`,
  phone: `+1-555-${String(1000 + i).slice(0, 4)}`,
  status: (['Active', 'Active', 'Active', 'Inactive', 'Suspended'] as const)[i % 5],
  contractStart: new Date(2022, i % 12, 1).toISOString(),
  contractEnd: new Date(2025 + (i % 3), i % 12, 1).toISOString(),
  slaType: ['Premium', 'Standard', 'Basic', 'Enterprise'][i % 4],
  totalCases: [12, 45, 8, 23, 67, 34, 19, 52][i % 8],
  openCases: [3, 12, 1, 5, 18, 7, 2, 14][i % 8],
  createdAt: new Date(2021, i % 12, i + 1).toISOString(),
}))



const mockSla: SLAEntry[] = [
  { metric: 'Response Time', target: 4, actual: 3.2, status: 'compliant' },
  { metric: 'Resolution Time (hrs)', target: 24, actual: 18.5, status: 'compliant' },
  { metric: 'Uptime %', target: 99.9, actual: 99.95, status: 'compliant' },
  { metric: 'First Response (min)', target: 15, actual: 22, status: 'at_risk' },
  { metric: 'Incident Resolution Rate', target: 95, actual: 97, status: 'compliant' },
]

export interface CustomerService {
  list(params: { search?: string; industry?: string; status?: string; page: number; limit: number }): Promise<{ customers: Customer[]; total: number }>
  getById(id: string): Promise<CustomerDetail | null>
}

export function useCustomerService(): CustomerService {
  return {
    async list({ search, industry, status, page, limit }) {
      let filtered = [...mockCustomers]
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter((c) =>
          c.companyName.toLowerCase().includes(q) ||
          c.location.toLowerCase().includes(q) ||
          c.id.toLowerCase().includes(q),
        )
      }
      if (industry) filtered = filtered.filter((c) => c.industry === industry)
      if (status) filtered = filtered.filter((c) => c.status === status)
      const total = filtered.length
      const start = (page - 1) * limit
      const customers = filtered.slice(start, start + limit)
      return { customers, total }
    },
    async getById(id: string) {
      const customer = mockCustomers.find((c) => c.id === id)
      if (!customer) return null
      const contracts: CustomerContract[] = [
        { id: 'CT-001', type: 'Service Agreement', startDate: '2023-01-01', endDate: '2025-12-31', value: 250000, status: 'Active' },
        { id: 'CT-002', type: 'Maintenance Contract', startDate: '2023-06-01', endDate: '2024-06-01', value: 85000, status: 'Expired' },
        { id: 'CT-003', type: 'SLA Premium', startDate: '2024-01-01', endDate: '2025-01-01', value: 120000, status: 'Active' },
      ]
      const sla = mockSla
      const interactions: CustomerInteraction[] = [
        { id: 'IN-001', type: 'support_ticket', subject: 'Voltage fluctuation in Zone 4', date: new Date(Date.now() - 86400000 * 2).toISOString(), agent: 'Sarah Chen', status: 'resolved' },
        { id: 'IN-002', type: 'email', subject: 'Q2 maintenance schedule review', date: new Date(Date.now() - 86400000 * 5).toISOString(), agent: 'Mike Rivera', status: 'resolved' },
        { id: 'IN-003', type: 'phone', subject: 'Emergency outage report', date: new Date(Date.now() - 86400000 * 8).toISOString(), agent: 'Emily Park', status: 'escalated' },
        { id: 'IN-004', type: 'meeting', subject: 'Quarterly business review', date: new Date(Date.now() - 86400000 * 14).toISOString(), agent: 'David Kim', status: 'resolved' },
        { id: 'IN-005', type: 'support_ticket', subject: 'New sensor configuration request', date: new Date(Date.now() - 86400000 * 21).toISOString(), agent: 'Sarah Chen', status: 'pending' },
      ]
      return { customer, contracts, sla, interactions }
    },
  }
}
