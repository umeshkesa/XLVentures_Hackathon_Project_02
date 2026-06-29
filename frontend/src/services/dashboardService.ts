import type {
  KPI,
  ActivityItem,
  PlatformHealth,
  RecommendationOverview,
  EvidenceAnalytics,
  AssetOverview,
  CustomerSummary,
  AlertItem,
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
  { id: 'a4', type: 'review', title: 'Review Completed', description: 'Maintenance plan approved for Solar Farm B', timestamp: hoursAgo(5), status: 'completed' },
  { id: 'a5', type: 'action', title: 'Action Executed', description: 'Work order #WO-2847 dispatched to crew Alpha', timestamp: hoursAgo(6), status: 'completed' },
  { id: 'a6', type: 'import', title: 'Dataset Failed', description: 'CU-BEMS energy data — connection timeout', timestamp: hoursAgo(8), status: 'failed' },
  { id: 'a7', type: 'recommendation', title: 'Recommendation Updated', description: 'Wind Turbine #WT-12 efficiency plan revised', timestamp: hoursAgo(10), status: 'completed' },
  { id: 'a8', type: 'evidence', title: 'Evidence Conflict Detected', description: 'Duplicate readings in Zone 4 vibration data', timestamp: hoursAgo(12), status: 'pending' },
  { id: 'a9', type: 'review', title: 'Review Started', description: 'Emergency shutdown protocol for Grid Node 7', timestamp: hoursAgo(18), status: 'pending' },
  { id: 'a10', type: 'action', title: 'Action Scheduled', description: 'Solar inverter calibration — start 2026-07-01', timestamp: daysAgo(1), status: 'pending' },
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
  { id: 'al3', type: 'warning', title: 'High Risk Asset Detected', description: 'Wind Turbine #WT-07 vibration exceeds threshold', timestamp: hoursAgo(5), source: 'asset' },
  { id: 'al4', type: 'critical', title: 'Compliance Violation', description: 'ISO 55001 audit — 3 maintenance records missing signatures', timestamp: hoursAgo(8), source: 'compliance' },
  { id: 'al5', type: 'info', title: 'SLA Breach Warning', description: 'Customer #C-1042 response time approaching limit', timestamp: hoursAgo(10), source: 'compliance' },
  { id: 'al6', type: 'warning', title: 'Battery Degradation Alert', description: 'Battery Bank #BB-04 capacity dropped to 72%', timestamp: hoursAgo(12), source: 'asset' },
  { id: 'al7', type: 'info', title: 'New Recommendations Available', description: '7 energy optimisation recommendations generated', timestamp: hoursAgo(16), source: 'recommendation' },
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
  getAll(): Promise<{
    kpis: KPI[]
    recentActivity: ActivityItem[]
    platformHealth: PlatformHealth
    recommendationOverview: RecommendationOverview
    evidenceAnalytics: EvidenceAnalytics
    assetOverview: AssetOverview
    customerSummary: CustomerSummary
    alerts: AlertItem[]
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
    getAll: async () => ({
      kpis: mockKPIs,
      recentActivity: mockActivity,
      platformHealth: mockPlatformHealth,
      recommendationOverview: mockRecommendationOverview,
      evidenceAnalytics: mockEvidenceAnalytics,
      assetOverview: mockAssetOverview,
      customerSummary: mockCustomerSummary,
      alerts: mockAlerts,
    }),
  }
}

let instance: DashboardService | undefined

export function useDashboardService(): DashboardService {
  if (!instance) {
    instance = createDashboardService()
  }
  return instance
}
