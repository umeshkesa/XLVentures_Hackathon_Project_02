export type RecommendationPriority = 'critical' | 'high' | 'medium' | 'low'
export type RecommendationStatus = 'active' | 'pending_approval' | 'approved' | 'rejected' | 'executed' | 'draft'
export type RecommendationSource = 'reasoning_engine' | 'rule_engine' | 'maintenance_schedule' | 'compliance' | 'customer_feedback' | 'manual'

export interface RecommendationItem {
  id: string
  title: string
  description: string
  priority: RecommendationPriority
  confidence: number
  businessImpact: string
  riskLevel: string
  estimatedCost: number
  estimatedSavings: number
  timeline: string
  source: RecommendationSource
  status: RecommendationStatus
  reasoningId?: string
  evidenceIds: string[]
  ruleIds: string[]
  knowledgeIds: string[]
  assetIds: string[]
  customerIds: string[]
  actions: RecommendationAction[]
  createdAt: string
  updatedAt: string
}

export interface RecommendationAction {
  id: string
  description: string
  assignedTo: string
  deadline: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  completedAt?: string
}

export interface RecommendationSummary {
  active: number
  pendingApproval: number
  approved: number
  rejected: number
  executed: number
  draft: number
  totalCost: number
  totalSavings: number
}
