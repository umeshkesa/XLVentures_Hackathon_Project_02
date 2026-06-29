export type ExecutionStatus = 'pending' | 'approved' | 'rejected' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
export type ExecutionPriority = 'critical' | 'high' | 'medium' | 'low'

export interface ExecutionStep {
  step: number
  label: string
  status: 'pending' | 'completed' | 'in_progress'
  completed_at: string | null
}

export interface AuditEntry {
  action: string
  by: string
  timestamp: string
  detail: string
}

export interface ExecutionItem {
  action_id: string
  recommendation_id: string
  review_id: string | null
  title: string
  status: ExecutionStatus
  priority: ExecutionPriority
  assigned_to: string
  description: string
  created_at: string
  scheduled_date: string
  completed_at: string | null
  steps: ExecutionStep[]
  audit_history: AuditEntry[]
}

export interface ExecutionSummary {
  pending: number
  inProgress: number
  completed: number
  cancelled: number
  total: number
}
