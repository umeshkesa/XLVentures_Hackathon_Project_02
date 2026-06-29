export interface ExplainerStage {
  name: string
  description: string
  details: string[]
  evidence: { id: string; title: string; confidence: number }[]
  rules: { id: string; description: string; triggered: boolean }[]
  knowledge: { id: string; title: string }[]
  expanded: boolean
}

export interface Explanation {
  id: string
  recommendationId: string
  recommendationTitle: string
  narrative: string
  stages: ExplainerStage[]
  confidence: number
  confidenceBreakdown: { label: string; value: number }[]
  alternatives: { title: string; confidence: number; reason: string }[]
  createdAt: string
}
