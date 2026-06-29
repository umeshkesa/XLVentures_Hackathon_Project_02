export interface Customer {
  id: string
  companyName: string
  industry: string
  location: string
  contactPerson: string
  contactEmail: string
  phone: string
  status: 'Active' | 'Inactive' | 'Suspended'
  contractStart: string
  contractEnd: string
  slaType: string
  totalCases: number
  openCases: number
  createdAt: string
}

export interface CustomerContract {
  id: string
  type: string
  startDate: string
  endDate: string
  value: number
  status: 'Active' | 'Expired' | 'Pending'
}

export interface SLAEntry {
  metric: string
  target: number
  actual: number
  status: 'compliant' | 'breached' | 'at_risk'
}

export interface CustomerInteraction {
  id: string
  type: 'email' | 'phone' | 'meeting' | 'support_ticket'
  subject: string
  date: string
  agent: string
  status: 'resolved' | 'pending' | 'escalated'
}

export interface CustomerDetail {
  customer: Customer
  contracts: CustomerContract[]
  sla: SLAEntry[]
  interactions: CustomerInteraction[]
}
