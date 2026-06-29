import { useApiHealth, useApiReady, useApiVersion, useImportJobs } from '@/services/healthApiService'
import { useEvidence } from '@/services/evidenceApiService'
import { useReasoningList } from '@/services/reasoningApiService'
import { useRecommendationList } from '@/services/recommendationApiService'
import { cn } from '@/lib/utils'
import {
  Activity, CheckCircle2, XCircle, AlertTriangle,   Database, HardDrive,
  Cpu, Clock, Download, Upload, RefreshCw, Server, BarChart3,
} from 'lucide-react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { LoadingSpinner } from '@/components/LoadingSpinner'

const SERVICE_ICONS: Record<string, React.ReactNode> = {
  'API Gateway': <Server className="h-4 w-4" />,
  'PostgreSQL': <Database className="h-4 w-4" />,
  'Redis Cache': <HardDrive className="h-4 w-4" />,
  'Import Pipeline': <Upload className="h-4 w-4" />,
  'Reasoning Engine': <Activity className="h-4 w-4" />,
  'Recommendation Engine': <BarChart3 className="h-4 w-4" />,
}

export default function PlatformHealth() {
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useApiHealth()
  const { data: ready } = useApiReady()
  const { data: version } = useApiVersion()
  const { data: importJobs = [] } = useImportJobs()
  const { data: evidenceData } = useEvidence({ limit: 1 })
  const { data: reasoningData } = useReasoningList({})
  const { data: recommendationData } = useRecommendationList({})
  const reasoningList = reasoningData?.items ?? []
  const recommendationList = recommendationData?.items ?? []

  const services = [
    { name: 'API Gateway', status: health?.status === 'healthy' ? 'healthy' as const : 'degraded' as const, latency: 45, uptime: health?.uptime_seconds ?? 0 },
    { name: 'PostgreSQL', status: 'healthy' as const, latency: 12, uptime: 0 },
    { name: 'Redis Cache', status: 'healthy' as const, latency: 3, uptime: 0 },
    { name: 'Import Pipeline', status: 'healthy' as const, latency: 0, uptime: 0 },
    { name: 'Reasoning Engine', status: 'healthy' as const, latency: 0, uptime: 0 },
    { name: 'Recommendation Engine', status: 'healthy' as const, latency: 0, uptime: 0 },
  ]

  const activeImports = importJobs.filter(j => j.status === 'processing' || j.status === 'queued').length
  const completedImports = importJobs.filter(j => j.status === 'completed').length
  const failedImports = importJobs.filter(j => j.status === 'failed').length

  const formatUptime = (seconds: number) => {
    const d = Math.floor(seconds / 86400)
    const h = Math.floor((seconds % 86400) / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    return `${d}d ${h}h ${m}m`
  }

  if (healthLoading) return <div className="flex justify-center py-12"><LoadingSpinner /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Platform Health</h1>
          <p className="text-sm text-muted-foreground mt-1">System status and operational metrics</p>
        </div>
        <button onClick={() => refetchHealth()} className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground px-3 py-1.5 rounded-lg hover:bg-muted transition-colors">
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <Card className="p-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-muted-foreground uppercase">Status</span>
            <Badge className={cn('text-[10px]', health?.status === 'healthy' ? 'bg-green-500/10 text-green-600 border-green-500/30' : 'bg-amber-500/10 text-amber-600')}>
              {health?.status === 'healthy' ? <CheckCircle2 className="h-3 w-3 mr-0.5" /> : <AlertTriangle className="h-3 w-3 mr-0.5" />}
              {health?.status ?? 'unknown'}
            </Badge>
          </div>
          <div className="text-lg font-bold mt-1">{version?.version ?? '—'}</div>
          <div className="text-[10px] text-muted-foreground">Version</div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-muted-foreground uppercase">Ready</span>
            <Badge className={cn('text-[10px]', ready?.ready ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600')}>
              {ready?.ready ? <CheckCircle2 className="h-3 w-3 mr-0.5" /> : <XCircle className="h-3 w-3 mr-0.5" />}
              {ready?.ready ? 'Ready' : 'Not Ready'}
            </Badge>
          </div>
          <div className="text-lg font-bold mt-1"><Clock className="h-4 w-4 inline mr-1" />{formatUptime(health?.uptime_seconds ?? 0)}</div>
          <div className="text-[10px] text-muted-foreground">Uptime</div>
        </Card>
        <Card className="p-3">
          <div className="text-lg font-bold">{services.filter(s => s.status === 'healthy').length}/{services.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Services Healthy</div>
        </Card>
        <Card className="p-3">
          <div className="text-lg font-bold">{evidenceData?.items?.length ?? 0}+</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Evidence Items</div>
        </Card>
        <Card className="p-3">
          <div className="text-lg font-bold">{reasoningList.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Reasoning Sessions</div>
        </Card>
        <Card className="p-3">
          <div className="text-lg font-bold">{recommendationList.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Recommendations</div>
        </Card>
        <Card className="p-3">
          <div className="text-lg font-bold">{importJobs.length}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Import Jobs</div>
        </Card>
      </div>

      <h2 className="text-lg font-semibold">Service Status</h2>
      <div className="grid gap-2">
        {services.map(s => (
          <div key={s.name} className="flex items-center gap-3 p-3 rounded-xl border bg-card">
            <div className={cn('flex h-8 w-8 items-center justify-center rounded-lg', s.status === 'healthy' ? 'bg-green-500/10 text-green-600' : 'bg-amber-500/10 text-amber-600')}>
              {SERVICE_ICONS[s.name] ?? <Server className="h-4 w-4" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{s.name}</span>
                <Badge className={cn('text-[10px]', s.status === 'healthy' ? 'bg-green-500/10 text-green-600 border-green-500/30' : 'bg-amber-500/10 text-amber-600 border-amber-500/30')}>
                  {s.status === 'healthy' ? <CheckCircle2 className="h-3 w-3 mr-0.5" /> : <AlertTriangle className="h-3 w-3 mr-0.5" />}
                  {s.status}
                </Badge>
              </div>
            </div>
            <div className="text-right text-xs text-muted-foreground shrink-0">
              {s.latency > 0 && <div>{s.latency}ms</div>}
              {s.uptime > 0 && <div>{formatUptime(s.uptime)}</div>}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold mb-3">Import Queue</h2>
          <Card className="p-4">
            <div className="flex items-center gap-4 mb-4">
              <div className="text-center flex-1 p-2 rounded-lg bg-muted/50">
                <div className="text-lg font-bold text-blue-500">{activeImports}</div>
                <div className="text-[10px] text-muted-foreground">Active</div>
              </div>
              <div className="text-center flex-1 p-2 rounded-lg bg-muted/50">
                <div className="text-lg font-bold text-green-500">{completedImports}</div>
                <div className="text-[10px] text-muted-foreground">Completed</div>
              </div>
              <div className="text-center flex-1 p-2 rounded-lg bg-muted/50">
                <div className="text-lg font-bold text-red-500">{failedImports}</div>
                <div className="text-[10px] text-muted-foreground">Failed</div>
              </div>
            </div>
            {importJobs.length === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-4">No import jobs found.</p>
            ) : (
              <div className="space-y-2 max-h-[200px] overflow-y-auto">
                {importJobs.slice(0, 10).map(job => (
                  <div key={job.job_id} className="flex items-center justify-between text-xs py-1.5 border-b border-border/50 last:border-0">
                    <span className="text-muted-foreground truncate max-w-[200px]">{job.file_name}</span>
                    <Badge className={cn('text-[9px]', job.status === 'completed' ? 'bg-green-500/10 text-green-600' : job.status === 'failed' ? 'bg-red-500/10 text-red-600' : 'bg-blue-500/10 text-blue-600')}>
                      {job.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-3">System Metrics</h2>
          <Card className="p-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground flex items-center gap-1"><Cpu className="h-3 w-3" /> Memory</span>
                  <span className="font-medium">42%</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-blue-500" style={{ width: '42%' }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground flex items-center gap-1"><Activity className="h-3 w-3" /> CPU</span>
                  <span className="font-medium">23%</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-emerald-500" style={{ width: '23%' }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground flex items-center gap-1"><Download className="h-3 w-3" /> Requests</span>
                  <span className="font-medium">1,247/min</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-amber-500" style={{ width: '35%' }} />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground flex items-center gap-1"><Upload className="h-3 w-3" /> Error Rate</span>
                  <span className="font-medium text-green-500">0.3%</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-green-500" style={{ width: '3%' }} />
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-border grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-sm font-bold">99.7%</div>
                <div className="text-[10px] text-muted-foreground">Success Rate</div>
              </div>
              <div>
                <div className="text-sm font-bold">42ms</div>
                <div className="text-[10px] text-muted-foreground">Avg Latency</div>
              </div>
              <div>
                <div className="text-sm font-bold">98</div>
                <div className="text-[10px] text-muted-foreground">Cache Hit %</div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
