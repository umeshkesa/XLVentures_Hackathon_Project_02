export interface AnalyticsSummary {
  totalRecommendations: number
  totalEvidence: number
  totalKnowledge: number
  totalImports: number
  totalReasoning: number
  totalReviews: number
  totalActions: number
  approvalRate: number
  averageConfidence: number
}

export interface ChartDataPoint {
  label: string
  value: number
  color?: string
}

export interface TimeSeriesPoint {
  date: string
  value: number
  category?: string
}

export interface AnalyticsDistribution {
  name: string
  data: ChartDataPoint[]
}

export const ANALYTICS_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#6366f1',
  '#84cc16', '#d946ef', '#0ea5e9', '#22c55e', '#eab308',
]
