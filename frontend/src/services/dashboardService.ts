import type {
  KPI,
  ActivityItem,
  PlatformHealth,
  RecommendationOverview,
  EvidenceAnalytics,
  AssetOverview,
  CustomerSummary,
  AlertItem,
  PlannerRun,
  AgentStat,
  KnowledgeUsage,
} from '@/types/dashboard'
import { COLORS } from '@/types/dashboard'

const DAY = 86_400_000

function hoursAgo(n: number): string {
  return new Date(Date.now() - n * 3_600_000).toISOString()
}

function daysAgo(n: number): string {
  return new Date(Date.now() - n * DAY).toISOString()
}

// ── Mock data ───────────────────────────────────────────────────────────────

const mockKPIs: KPI[] = [
  { label: 'Total Customers', value: 2847, formatted: '2,847', change: 12, changeLabel: 'from last month', trend: 'up', icon: 'Users' },
  { label: 'Total Assets', value: 14203, formatted: '14,203', change: 5, changeLabel: 'from last month', trend: 'up', icon: 'HardDrive' },
  { label: 'Active Recommendations', value: 847, formatted: '847', change: 23, changeLabel: 'from last month', trend: 'up', icon: 'ThumbsUp' },
  { label: 'Pending Reviews', value: 34, formatted: '34', change: -15, changeLabel: 'from last week', trend: 'down', icon: 'ClipboardCheck' },
  { label: 'Open Incidents', value: 128, formatted: '128', change: -8, changeLabel: 'from last month', trend: 'down', icon: 'AlertTriangle' },
  { label: 'Imported Documents', value: 15632, formatted: '15,632', change: 34, changeLabel: 'from last month', trend: 'up', icon: 'Upload' },
  { label: 'Knowledge Base', value: 4218, formatted: '4,218', change: 18, changeLabel: 'articles added', trend: 'up', icon: 'BookOpen' },
  { label: 'System Health', value: 98, formatted: '98%', change: 2, changeLabel: 'uptime this month', trend: 'up', icon: 'Activity' },
]

const mockActivity: ActivityItem[] = [
  { id: 'a1', type: 'import', title: 'Dataset Imported', description: 'Monthly sensor data batch — 12,483 records', timestamp: hoursAgo(1), status: 'completed' },
  { id: 'a2', type: 'evidence', title: 'Evidence Generated', description: '3 new evidence packages from sensor anomalies', timestamp: hoursAgo(2), status: 'completed' },
  { id: 'a3', type: 'recommendation', title: 'Recommendation Created', description: 'Transformer PM schedule updated for Zone 4', timestamp: hoursAgo(3), status: 'completed' },
  { id: 'a4', type: 'planner', title: 'Planner Run Completed', description: 'PLN-001: Transformer T102 overheating incident handled', timestamp: hoursAgo(3), status: 'completed' },
  { id: 'a5', type: 'review', title: 'Review Completed', description: 'Maintenance plan approved for Solar Farm B', timestamp: hoursAgo(5), status: 'completed' },
  { id: 'a6', type: 'action', title: 'Action Executed', description: 'Work order #WO-2847 dispatched to crew Alpha', timestamp: hoursAgo(6), status: 'completed' },
  { id: 'a7', type: 'import', title: 'Dataset Failed', description: 'CU-BEMS energy data — connection timeout', timestamp: hoursAgo(8), status: 'failed' },
  { id: 'a8', type: 'recommendation', title: 'Recommendation Updated', description: 'Wind Turbine #WT-12 efficiency plan revised', timestamp: hoursAgo(10), status: 'completed' },
  { id: 'a9', type: 'planner', title: 'Planner Run Started', description: 'PLN-003: WT-102 bearing wear analysis initiated', timestamp: hoursAgo(11), status: 'pending' },
  { id: 'a10', type: 'evidence', title: 'Evidence Conflict Detected', description: 'Duplicate readings in Zone 4 vibration data', timestamp: hoursAgo(12), status: 'pending' },
  { id: 'a11', type: 'review', title: 'Review Started', description: 'Emergency shutdown protocol for Grid Node 7', timestamp: hoursAgo(18), status: 'pending' },
  { id: 'a12', type: 'action', title: 'Action Scheduled', description: 'Solar inverter calibration — start 2026-07-01', timestamp: daysAgo(1), status: 'pending' },
]

const mockPlatformHealth: PlatformHealth = {
  api: { label: 'API Gateway', status: 'healthy', latency: 24 },
  postgresql: { label: 'PostgreSQL', status: 'healthy', latency: 3 },
  redis: { label: 'Redis Cache', status: 'healthy', latency: 1 },
  chromadb: { label: 'Vector Store', status: 'healthy', latency: 45 },
  importPipeline: { label: 'Import Pipeline', status: 'healthy', latency: 120 },
  llm: { label: 'LLM Service', status: 'unknown' },
}

const mockRecommendationOverview: RecommendationOverview = {
  byPriority: [
    { name: 'Critical', value: 42, color: COLORS.red },
    { name: 'High', value: 156, color: COLORS.amber },
    { name: 'Medium', value: 389, color: COLORS.blue },
    { name: 'Low', value: 260, color: COLORS.emerald },
  ],
  byStatus: [
    { name: 'Active', value: 512, color: COLORS.blue },
    { name: 'Under Review', value: 128, color: COLORS.amber },
    { name: 'Approved', value: 96, color: COLORS.emerald },
    { name: 'Rejected', value: 48, color: COLORS.red },
    { name: 'Draft', value: 63, color: COLORS.slate },
  ],
  confidenceDistribution: [
    { name: '90-100%', value: 187, color: COLORS.emerald },
    { name: '70-89%', value: 312, color: COLORS.blue },
    { name: '50-69%', value: 198, color: COLORS.amber },
    { name: '<50%', value: 150, color: COLORS.red },
  ],
}

const mockEvidenceAnalytics: EvidenceAnalytics = {
  byType: [
    { name: 'Sensor Readings', value: 8421, color: COLORS.blue },
    { name: 'Incident Reports', value: 1256, color: COLORS.red },
    { name: 'Maintenance Logs', value: 3420, color: COLORS.emerald },
    { name: 'Compliance Docs', value: 892, color: COLORS.violet },
    { name: 'Customer Feedback', value: 2147, color: COLORS.amber },
    { name: 'Alarm Records', value: 4103, color: COLORS.cyan },
  ],
  bySource: [
    { name: 'IoT Sensors', value: 7230, color: COLORS.blue },
    { name: 'CRM System', value: 2840, color: COLORS.emerald },
    { name: 'SCADA', value: 4510, color: COLORS.amber },
    { name: 'Manual Entry', value: 1230, color: COLORS.violet },
    { name: 'External API', value: 3870, color: COLORS.cyan },
  ],
  confidence: [
    { name: 'High (>90%)', value: 8920, color: COLORS.emerald },
    { name: 'Medium (70-89%)', value: 5140, color: COLORS.blue },
    { name: 'Low (<70%)', value: 2380, color: COLORS.red },
  ],
}

const mockAssetOverview: AssetOverview = {
  categories: [
    { label: 'Solar Plants', count: 34, icon: 'Sun', status: 'online', change: 2 },
    { label: 'Wind Farms', count: 18, icon: 'Wind', status: 'online', change: 1 },
    { label: 'Transformers', count: 142, icon: 'Zap', status: 'online', change: 0 },
    { label: 'Batteries', count: 89, icon: 'BatteryCharging', status: 'warning', change: 3 },
    { label: 'Sensors', count: 12406, icon: 'Radio', status: 'online', change: 412 },
  ],
  total: 12689,
}

const mockCustomerSummary: CustomerSummary = {
  totalCustomers: 2847,
  activeCases: 156,
  contracts: 421,
  slaCompliant: 392,
  slaTotal: 421,
}

const mockAlerts: AlertItem[] = [
  { id: 'al1', type: 'critical', title: 'Critical Recommendation Overdue', description: 'Transformer #TF-089 PM exceeds deadline by 72h', timestamp: hoursAgo(1), source: 'recommendation' },
  { id: 'al2', type: 'warning', title: 'Import Pipeline Degraded', description: 'CSV import for sensor_data/ai4i2020.csv partial failure', timestamp: hoursAgo(3), source: 'import' },
  { id: 'al3', type: 'warning', title: 'Planner Run Failed', description: 'PLN-005: Solar farm analysis — insufficient evidence', timestamp: hoursAgo(4), source: 'planner' },
  { id: 'al4', type: 'warning', title: 'High Risk Asset Detected', description: 'Wind Turbine #WT-07 vibration exceeds threshold', timestamp: hoursAgo(5), source: 'asset' },
  { id: 'al5', type: 'critical', title: 'Compliance Violation', description: 'ISO 55001 audit — 3 maintenance records missing signatures', timestamp: hoursAgo(8), source: 'compliance' },
  { id: 'al6', type: 'info', title: 'SLA Breach Warning', description: 'Customer #C-1042 response time approaching limit', timestamp: hoursAgo(10), source: 'compliance' },
  { id: 'al7', type: 'warning', title: 'Battery Degradation Alert', description: 'Battery Bank #BB-04 capacity dropped to 72%', timestamp: hoursAgo(12), source: 'asset' },
  { id: 'al8', type: 'info', title: 'New Recommendations Available', description: '7 energy optimisation recommendations generated', timestamp: hoursAgo(16), source: 'recommendation' },
]

const mockPlannerRuns: PlannerRun[] = [
  { id: 'PLN-001', title: 'Transformer T102 Overheating', goal: 'Respond to critical transformer overheating incident at PeakVolt substation', status: 'completed', confidence: 0.94, agentCount: 7, totalDurationMs: 3350, createdAt: hoursAgo(3) },
  { id: 'PLN-002', title: 'Emergency Power Outage Response', goal: 'Respond to emergency power outage at PowerLine Dynamics', status: 'completed', confidence: 0.91, agentCount: 7, totalDurationMs: 2990, createdAt: hoursAgo(48) },
  { id: 'PLN-003', title: 'WT-102 Predictive Maintenance', goal: 'Address wind turbine WT-102 bearing wear at 72% threshold', status: 'active', confidence: 0.83, agentCount: 7, totalDurationMs: 2430, createdAt: hoursAgo(96) },
  { id: 'PLN-004', title: 'Battery BB-101 Degradation', goal: 'Investigate 28% capacity loss in battery bank', status: 'completed', confidence: 0.87, agentCount: 7, totalDurationMs: 3120, createdAt: hoursAgo(24) },
]

const mockAgentStats: AgentStat[] = [
  { name: 'Classification Agent', status: 'idle', successRate: 98.5, avgDurationMs: 290, executionsToday: 47 },
  { name: 'Evidence Agent', status: 'active', successRate: 96.2, avgDurationMs: 530, executionsToday: 38 },
  { name: 'Knowledge Agent', status: 'idle', successRate: 97.1, avgDurationMs: 400, executionsToday: 35 },
  { name: 'Business Rule Agent', status: 'idle', successRate: 99.0, avgDurationMs: 280, executionsToday: 42 },
  { name: 'Reasoning Agent', status: 'busy', successRate: 94.5, avgDurationMs: 790, executionsToday: 28 },
  { name: 'Recommendation Agent', status: 'idle', successRate: 95.8, avgDurationMs: 410, executionsToday: 31 },
  { name: 'Explainability Agent', status: 'idle', successRate: 97.3, avgDurationMs: 370, executionsToday: 30 },
]

const mockKnowledgeUsage: KnowledgeUsage[] = [
  { documentId: 'DOC-003', title: 'Oil Analysis Best Practices', usageCount: 24, confidence: 0.92 },
  { documentId: 'DOC-007', title: 'Siemens Transformer Manual', usageCount: 18, confidence: 0.88 },
  { documentId: 'DOC-001', title: 'Energy Optimization Playbook', usageCount: 15, confidence: 0.85 },
  { documentId: 'DOC-002', title: 'Wind Turbine Inspection Checklist', usageCount: 12, confidence: 0.90 },
  { documentId: 'DOC-005', title: 'Grid Failure Playbook v5', usageCount: 10, confidence: 0.87 },
  { documentId: 'DOC-006', title: 'Battery Maintenance Guide', usageCount: 8, confidence: 0.84 },
]

// ── Service facade ──────────────────────────────────────────────────────────

export interface DashboardService {
  getKPIs(): Promise<KPI[]>
  getRecentActivity(): Promise<ActivityItem[]>
  getPlatformHealth(): Promise<PlatformHealth>
  getRecommendationOverview(): Promise<RecommendationOverview>
  getEvidenceAnalytics(): Promise<EvidenceAnalytics>
  getAssetOverview(): Promise<AssetOverview>
  getCustomerSummary(): Promise<CustomerSummary>
  getAlerts(): Promise<AlertItem[]>
  getPlannerRuns(): Promise<PlannerRun[]>
  getAgentStats(): Promise<AgentStat[]>
  getKnowledgeUsage(): Promise<KnowledgeUsage[]>
  getAll(): Promise<{
    kpis: KPI[]
    recentActivity: ActivityItem[]
    platformHealth: PlatformHealth
    recommendationOverview: RecommendationOverview
    evidenceAnalytics: EvidenceAnalytics
    assetOverview: AssetOverview
    customerSummary: CustomerSummary
    alerts: AlertItem[]
    plannerRuns: PlannerRun[]
    agentStats: AgentStat[]
    knowledgeUsage: KnowledgeUsage[]
    criticalRecommendations: number
    pendingReviews: number
    plannerSuccessRate: number
  }>
}

function createDashboardService(): DashboardService {
  return {
    getKPIs: async () => mockKPIs,
    getRecentActivity: async () => mockActivity,
    getPlatformHealth: async () => mockPlatformHealth,
    getRecommendationOverview: async () => mockRecommendationOverview,
    getEvidenceAnalytics: async () => mockEvidenceAnalytics,
    getAssetOverview: async () => mockAssetOverview,
    getCustomerSummary: async () => mockCustomerSummary,
    getAlerts: async () => mockAlerts,
    getPlannerRuns: async () => mockPlannerRuns,
    getAgentStats: async () => mockAgentStats,
    getKnowledgeUsage: async () => mockKnowledgeUsage,
    getAll: async () => {
      const completedRuns = mockPlannerRuns.filter((r) => r.status === 'completed').length
      const totalRuns = mockPlannerRuns.length
      return {
        kpis: mockKPIs,
        recentActivity: mockActivity,
        platformHealth: mockPlatformHealth,
        recommendationOverview: mockRecommendationOverview,
        evidenceAnalytics: mockEvidenceAnalytics,
        assetOverview: mockAssetOverview,
        customerSummary: mockCustomerSummary,
        alerts: mockAlerts,
        plannerRuns: mockPlannerRuns,
        agentStats: mockAgentStats,
        knowledgeUsage: mockKnowledgeUsage,
        criticalRecommendations: mockRecommendationOverview.byPriority.find((p) => p.name === 'Critical')?.value ?? 0,
        pendingReviews: mockKPIs.find((k) => k.label === 'Pending Reviews')?.value ?? 0,
        plannerSuccessRate: totalRuns > 0 ? (completedRuns / totalRuns) * 100 : 0,
      }
    },
  }
}

let instance: DashboardService | undefined

export function useDashboardService(): DashboardService {
  if (!instance) {
    instance = createDashboardService()
  }
  return instance
}
