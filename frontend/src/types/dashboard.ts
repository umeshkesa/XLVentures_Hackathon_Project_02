export interface KPI {
  label: string
  value: number
  formatted: string
  change: number
  changeLabel: string
  trend: 'up' | 'down' | 'neutral'
  icon: string
}

export interface ActivityItem {
  id: string
  type: 'import' | 'evidence' | 'recommendation' | 'review' | 'action'
  title: string
  description: string
  timestamp: string
  status: 'completed' | 'pending' | 'failed'
}

export interface HealthStatus {
  label: string
  status: 'healthy' | 'degraded' | 'down' | 'unknown'
  latency?: number
}

export interface PlatformHealth {
  api: HealthStatus
  postgresql: HealthStatus
  redis: HealthStatus
  chromadb: HealthStatus
  importPipeline: HealthStatus
  llm: HealthStatus
}

export interface ChartSlice {
  name: string
  value: number
  color: string
}

export interface RecommendationOverview {
  byPriority: ChartSlice[]
  byStatus: ChartSlice[]
  confidenceDistribution: ChartSlice[]
}

export interface EvidenceAnalytics {
  byType: ChartSlice[]
  bySource: ChartSlice[]
  confidence: ChartSlice[]
}

export interface AssetCategory {
  label: string
  count: number
  icon: string
  status: 'online' | 'offline' | 'warning'
  change: number
}

export interface AssetOverview {
  categories: AssetCategory[]
  total: number
}

export interface CustomerSummary {
  totalCustomers: number
  activeCases: number
  contracts: number
  slaCompliant: number
  slaTotal: number
}

export interface AlertItem {
  id: string
  type: 'critical' | 'warning' | 'info'
  title: string
  description: string
  timestamp: string
  source: 'recommendation' | 'import' | 'asset' | 'compliance'
}

export interface DashboardData {
  kpis: KPI[]
  recentActivity: ActivityItem[]
  platformHealth: PlatformHealth
  recommendationOverview: RecommendationOverview
  evidenceAnalytics: EvidenceAnalytics
  assetOverview: AssetOverview
  customerSummary: CustomerSummary
  alerts: AlertItem[]
  loading: boolean
  error: string | null
}

export const COLORS = {
  blue: '#3b82f6',
  indigo: '#6366f1',
  violet: '#8b5cf6',
  emerald: '#10b981',
  amber: '#f59e0b',
  red: '#ef4444',
  cyan: '#06b6d4',
  pink: '#ec4899',
  slate: '#64748b',
  orange: '#f97316',
  teal: '#14b8a6',
} as const

export const CHART_COLORS = [
  COLORS.blue,
  COLORS.emerald,
  COLORS.amber,
  COLORS.violet,
  COLORS.cyan,
  COLORS.red,
  COLORS.pink,
  COLORS.indigo,
  COLORS.orange,
  COLORS.teal,
]
