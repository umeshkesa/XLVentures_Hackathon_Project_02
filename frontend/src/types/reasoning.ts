export type ReasoningStatus = 'in_progress' | 'completed' | 'failed'
export type ReasoningDomain = 'energy' | 'maintenance' | 'safety' | 'compliance' | 'operations' | 'customer' | 'general'
export type ReasoningStrategy = 'deductive' | 'inductive' | 'abductive' | 'analogical' | 'causal'

export interface ReasoningSession {
  id: string
  query: string
  status: ReasoningStatus
  domain: ReasoningDomain
  strategy: ReasoningStrategy
  confidence: number
  riskScore: number
  processingTimeMs: number
  triggeredBy: string
  evidenceCount: number
  ruleCount: number
  knowledgeCount: number
  createdAt: string
  completedAt?: string
  conclusion: string
  steps: ReasoningStep[]
  relatedRecommendations: string[]
}

export interface ReasoningStep {
  id: string
  type: string
  description: string
  input: string
  output: string
  durationMs: number
}

export interface ReasoningSummary {
  activeCount: number
  completedCount: number
  failedCount: number
  averageConfidence: number
  averageRiskScore: number
}
