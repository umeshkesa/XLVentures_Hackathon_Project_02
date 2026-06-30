import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { KPICard, KPICardSkeleton } from '@/components/KPICard'
import { RecentActivity } from '@/components/RecentActivity'
import { PlatformHealthWidget } from '@/components/PlatformHealth'
import { RecommendationCharts } from '@/components/RecommendationCharts'
import { EvidenceCharts } from '@/components/EvidenceCharts'
import { AssetOverviewWidget } from '@/components/AssetOverview'
import { CustomerSummaryWidget } from '@/components/CustomerSummary'
import { AlertsWidget } from '@/components/AlertsWidget'
import { useDashboardService } from '@/services/dashboardService'
import type { DashboardData, PlannerRun, AgentStat, KnowledgeUsage } from '@/types/dashboard'
import {
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  TrendingUp,
  BrainCircuit,
  BookOpen,
  Activity,
  ArrowRight,
  ClipboardList,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'

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
  plannerRuns: [],
  agentStats: [],
  knowledgeUsage: [],
  criticalRecommendations: 0,
  pendingReviews: 0,
  plannerSuccessRate: 0,
  loading: true,
  error: null,
}

function PlannerRunsWidget({ runs, loading }: { runs: PlannerRun[]; loading: boolean }) {
  if (loading || runs.length === 0) return null
  return (
    <div className="bg-card rounded-xl border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <ClipboardList className="h-4 w-4 text-indigo-500" />
          Recent Planner Runs
        </h3>
        <Link to="/planner" className="text-xs text-primary hover:underline flex items-center gap-1">
          View All <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="space-y-3">
        {runs.map((run) => (
          <Link
            key={run.id}
            to={`/planner?id=${run.id}`}
            className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
          >
            <div className={cn(
              'h-8 w-8 rounded-full flex items-center justify-center shrink-0',
              run.status === 'completed' ? 'bg-emerald-100 dark:bg-emerald-900/30' :
              run.status === 'active' ? 'bg-blue-100 dark:bg-blue-900/30' :
              'bg-red-100 dark:bg-red-900/30',
            )}>
              {run.status === 'completed' && <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />}
              {run.status === 'active' && <Loader2 className="h-4 w-4 text-blue-600 dark:text-blue-400 animate-spin" />}
              {run.status === 'failed' && <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{run.title}</p>
              <p className="text-xs text-muted-foreground truncate">{run.goal}</p>
            </div>
            <div className="text-right text-xs text-muted-foreground shrink-0">
              <div className="font-mono">{(run.confidence * 100).toFixed(0)}%</div>
              <div>{run.agentCount} agents</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

function AgentStatsWidget({ stats, loading }: { stats: AgentStat[]; loading: boolean }) {
  if (loading || stats.length === 0) return null
  return (
    <div className="bg-card rounded-xl border p-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="h-4 w-4 text-cyan-500" />
        <h3 className="font-semibold">Agent Execution Statistics</h3>
      </div>
      <div className="space-y-3">
        {stats.map((agent) => (
          <div key={agent.name} className="flex items-center gap-3">
            <div className={cn(
              'h-2 w-2 rounded-full shrink-0',
              agent.status === 'idle' ? 'bg-slate-400' :
              agent.status === 'active' ? 'bg-blue-500' :
              agent.status === 'busy' ? 'bg-amber-500' :
              'bg-red-500',
            )} />
            <div className="flex-1 min-w-0">
              <div className="flex justify-between text-sm">
                <span className="font-medium text-foreground truncate">{agent.name}</span>
                <span className="text-muted-foreground font-mono">{agent.avgDurationMs}ms</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                <span>Success: {agent.successRate}%</span>
                <span>{agent.executionsToday} today</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function KnowledgeUsageWidget({ usage, loading }: { usage: KnowledgeUsage[]; loading: boolean }) {
  if (loading || usage.length === 0) return null
  return (
    <div className="bg-card rounded-xl border p-6">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="h-4 w-4 text-yellow-500" />
        <h3 className="font-semibold">Knowledge Usage</h3>
      </div>
      <div className="space-y-2">
        {usage.map((doc) => (
          <div key={doc.documentId} className="flex items-center gap-3 p-2.5 rounded-lg border text-sm">
            <BookOpen className="h-4 w-4 text-yellow-500 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-foreground truncate">{doc.title}</p>
              <p className="text-xs text-muted-foreground">{doc.documentId} · Used {doc.usageCount} times</p>
            </div>
            <div className="flex items-center gap-1 text-xs">
              <TrendingUp className="h-3 w-3 text-emerald-500" />
              <span className="font-mono text-muted-foreground">{(doc.confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SummaryCards({ criticalRecs, pendingReviews, plannerSuccessRate, loading }: {
  criticalRecs: number; pendingReviews: number; plannerSuccessRate: number; loading: boolean
}) {
  if (loading) return null
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <Link to="/recommendations?priority=critical" className="bg-card rounded-xl border p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Critical Recommendations</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{criticalRecs}</p>
          </div>
          <Zap className="h-8 w-8 text-red-500/30" />
        </div>
      </Link>
      <Link to="/review?status=pending" className="bg-card rounded-xl border p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Pending Human Reviews</p>
            <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">{pendingReviews}</p>
          </div>
          <Clock className="h-8 w-8 text-amber-500/30" />
        </div>
      </Link>
      <Link to="/planner" className="bg-card rounded-xl border p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Planner Success Rate</p>
            <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{plannerSuccessRate.toFixed(0)}%</p>
          </div>
          <BrainCircuit className="h-8 w-8 text-indigo-500/30" />
        </div>
      </Link>
    </div>
  )
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
          Enterprise overview of platform activity, agent orchestration, health, and analytics.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {data.loading
          ? Array.from({ length: 8 }).map((_, i) => <KPICardSkeleton key={i} />)
          : data.kpis.map((kpi) => <KPICard key={kpi.label} kpi={kpi} />)
        }
      </div>

      {/* Summary Cards */}
      <SummaryCards
        criticalRecs={data.criticalRecommendations}
        pendingReviews={data.pendingReviews}
        plannerSuccessRate={data.plannerSuccessRate}
        loading={data.loading}
      />

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

      {/* Row 4: Planner + Agents + Knowledge */}
      <div className="grid gap-6 lg:grid-cols-3">
        <PlannerRunsWidget runs={data.plannerRuns} loading={data.loading} />
        <AgentStatsWidget stats={data.agentStats} loading={data.loading} />
        <KnowledgeUsageWidget usage={data.knowledgeUsage} loading={data.loading} />
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
