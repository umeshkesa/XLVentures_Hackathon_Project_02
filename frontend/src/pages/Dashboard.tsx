import { useEffect, useState } from 'react'
import { KPICard, KPICardSkeleton } from '@/components/KPICard'
import { RecentActivity } from '@/components/RecentActivity'
import { PlatformHealthWidget } from '@/components/PlatformHealth'
import { RecommendationCharts } from '@/components/RecommendationCharts'
import { EvidenceCharts } from '@/components/EvidenceCharts'
import { AssetOverviewWidget } from '@/components/AssetOverview'
import { CustomerSummaryWidget } from '@/components/CustomerSummary'
import { AlertsWidget } from '@/components/AlertsWidget'
import { useDashboardService } from '@/services/dashboardService'
import type { DashboardData } from '@/types/dashboard'

const emptyData: DashboardData = {
  kpis: [],
  recentActivity: [],
  platformHealth: {
    api: { label: 'API Gateway', status: 'unknown' },
    postgresql: { label: 'PostgreSQL', status: 'unknown' },
    redis: { label: 'Redis Cache', status: 'unknown' },
    chromadb: { label: 'Vector Store', status: 'unknown' },
    importPipeline: { label: 'Import Pipeline', status: 'unknown' },
    llm: { label: 'LLM Service', status: 'unknown' },
  },
  recommendationOverview: { byPriority: [], byStatus: [], confidenceDistribution: [] },
  evidenceAnalytics: { byType: [], bySource: [], confidence: [] },
  assetOverview: { categories: [], total: 0 },
  customerSummary: { totalCustomers: 0, activeCases: 0, contracts: 0, slaCompliant: 0, slaTotal: 0 },
  alerts: [],
  loading: true,
  error: null,
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData>(emptyData)
  const svc = useDashboardService()

  const load = () => {
    setData((prev) => ({ ...prev, loading: true, error: null }))
    svc.getAll().then((result) => {
      setData({ ...result, loading: false, error: null })
    }).catch((err: unknown) => {
      setData((prev) => ({ ...prev, loading: false, error: err instanceof Error ? err.message : 'Failed to load dashboard data' }))
    })
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 30000)
    const onRefresh = () => load()
    window.addEventListener('dashboard-refresh', onRefresh)
    return () => { clearInterval(interval); window.removeEventListener('dashboard-refresh', onRefresh) }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Executive Dashboard</h1>
        <p className="text-muted-foreground">
          Enterprise overview of platform activity, health, and analytics.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {data.loading
          ? Array.from({ length: 8 }).map((_, i) => <KPICardSkeleton key={i} />)
          : data.kpis.map((kpi) => <KPICard key={kpi.label} kpi={kpi} />)
        }
      </div>

      {/* Row 2: Activity + Health */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentActivity
            items={data.recentActivity}
            loading={data.loading}
            error={data.error}
            onRetry={load}
          />
        </div>
        <div>
          <PlatformHealthWidget
            health={data.platformHealth}
            loading={data.loading}
            error={data.error}
            onRetry={load}
          />
        </div>
      </div>

      {/* Recommendation Charts */}
      <RecommendationCharts
        data={data.recommendationOverview}
        loading={data.loading}
        error={data.error}
        onRetry={load}
      />

      {/* Evidence Charts */}
      <EvidenceCharts
        data={data.evidenceAnalytics}
        loading={data.loading}
        error={data.error}
        onRetry={load}
      />

      {/* Row 3: Assets + Customers */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AssetOverviewWidget
            data={data.assetOverview}
            loading={data.loading}
            error={data.error}
            onRetry={load}
          />
        </div>
        <div>
          <CustomerSummaryWidget
            data={data.customerSummary}
            loading={data.loading}
            error={data.error}
            onRetry={load}
          />
        </div>
      </div>

      {/* Alerts */}
      <AlertsWidget
        items={data.alerts}
        loading={data.loading}
        error={data.error}
        onRetry={load}
      />
    </div>
  )
}
