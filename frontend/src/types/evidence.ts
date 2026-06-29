export type EvidenceType = 'sensor' | 'incident' | 'maintenance' | 'compliance' | 'customer' | 'alarm' | 'knowledge' | 'recommendation' | 'email' | 'report'
export type EvidenceStatus = 'collected' | 'verified' | 'analyzed' | 'fused' | 'rejected'
export type EvidencePriority = 'critical' | 'high' | 'medium' | 'low'
export type EvidenceSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info'

export interface EvidenceItem {
  id: string
  type: EvidenceType
  status: EvidenceStatus
  priority: EvidencePriority
  severity: EvidenceSeverity
  title: string
  description: string
  source: string
  sourceType: string
  domain: string
  confidence: number
  qualityScore: number
  freshness: number
  completeness: number
  consistency: number
  reliability: number
  timestamp: string
  tags: string[]
  relatedCustomers: string[]
  relatedAssets: string[]
  relatedKnowledge: string[]
  relatedRules: string[]
  relatedRecommendations: string[]
}

export interface TraceabilityStep {
  stage: 'source' | 'evidence' | 'knowledge' | 'rules' | 'reasoning' | 'recommendation'
  label: string
  description: string
  timestamp: string
  status: 'completed' | 'in_progress' | 'pending'
  targetId?: string
  targetRoute?: string
}
