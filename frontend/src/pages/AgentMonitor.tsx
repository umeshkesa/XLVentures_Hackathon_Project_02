import { useState, useMemo } from 'react'
import { DEFAULT_AGENTS } from '@/types/agents'
import type { Agent, AgentStatus } from '@/types/agents'
import { cn } from '@/lib/utils'
import {
  BrainCircuit, BookOpen, FileSearch, Scale, ThumbsUp, Zap, ClipboardList,
  Activity, CheckCircle2, XCircle, AlertTriangle, Clock, Search,
} from 'lucide-react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { LoadingSpinner } from '@/components/LoadingSpinner'

const AGENT_TYPE_CONFIG: Record<string, { icon: React.ReactNode; color: string }> = {
  planner: { icon: <ClipboardList className="h-5 w-5" />, color: 'text-blue-500 bg-blue-500/10 border-blue-500/30' },
  knowledge: { icon: <BookOpen className="h-5 w-5" />, color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30' },
  evidence: { icon: <FileSearch className="h-5 w-5" />, color: 'text-amber-500 bg-amber-500/10 border-amber-500/30' },
  rules: { icon: <Scale className="h-5 w-5" />, color: 'text-rose-500 bg-rose-500/10 border-rose-500/30' },
  reasoning: { icon: <BrainCircuit className="h-5 w-5" />, color: 'text-violet-500 bg-violet-500/10 border-violet-500/30' },
  recommendation: { icon: <ThumbsUp className="h-5 w-5" />, color: 'text-orange-500 bg-orange-500/10 border-orange-500/30' },
  execution: { icon: <Zap className="h-5 w-5" />, color: 'text-green-500 bg-green-500/10 border-green-500/30' },
}

const STATUS_CONFIG: Record<AgentStatus, { icon: React.ReactNode; label: string; color: string }> = {
  active: { icon: <CheckCircle2 className="h-3 w-3" />, label: 'Active', color: 'bg-green-500/10 text-green-600 border-green-500/30' },
  idle: { icon: <Clock className="h-3 w-3" />, label: 'Idle', color: 'bg-blue-500/10 text-blue-600 border-blue-500/30' },
  busy: { icon: <Activity className="h-3 w-3" />, label: 'Busy', color: 'bg-amber-500/10 text-amber-600 border-amber-500/30' },
  error: { icon: <XCircle className="h-3 w-3" />, label: 'Error', color: 'bg-red-500/10 text-red-600 border-red-500/30' },
  disabled: { icon: <AlertTriangle className="h-3 w-3" />, label: 'Disabled', color: 'bg-slate-500/10 text-slate-600 border-slate-500/30' },
}

export default function AgentMonitor() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<AgentStatus | 'all'>('all')
  const agents = DEFAULT_AGENTS as Agent[]

  const filtered = useMemo(() => {
    return agents.filter(a => {
      if (statusFilter !== 'all' && a.status !== statusFilter) return false
      if (search && !a.name.toLowerCase().includes(search.toLowerCase()) && !a.type.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [agents, search, statusFilter])

  const summary = useMemo(() => {
    const total = agents.length
    const active = agents.filter(a => a.status === 'active').length
    const busy = agents.filter(a => a.status === 'busy').length
    const error = agents.filter(a => a.status === 'error').length
    const avgHealth = Math.round(agents.reduce((s, a) => s + a.health, 0) / total)
    const avgSuccess = Math.round(agents.reduce((s, a) => s + a.successRate, 0) / total)
    const totalExecs = agents.reduce((s, a) => s + a.totalExecutions, 0)
    return { total, active, busy, error, avgHealth, avgSuccess, totalExecs }
  }, [agents])

  if (!agents.length) return <div className="flex justify-center py-12"><LoadingSpinner /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Agent Monitor</h1>
        <p className="text-sm text-muted-foreground mt-1">Monitor all registered ADIP agents and their performance</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{summary.total}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Total Agents</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold text-green-500">{summary.active}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Active</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold text-amber-500">{summary.busy}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Busy</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold text-red-500">{summary.error}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Errors</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{summary.avgHealth}%</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Avg Health</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{summary.avgSuccess}%</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Success Rate</div>
        </Card>
        <Card className="p-3 text-center">
          <div className="text-2xl font-bold">{summary.totalExecs.toLocaleString()}</div>
          <div className="text-[10px] text-muted-foreground uppercase mt-0.5">Executions</div>
        </Card>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search agents..." value={search} onChange={e => setSearch(e.target.value)}
            className="w-full bg-background border rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" />
        </div>
        <div className="flex gap-1">
          {(['all', 'active', 'idle', 'busy', 'error'] as const).map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={cn('px-3 py-1.5 text-xs rounded-lg border transition-colors capitalize', statusFilter === s ? 'bg-primary text-primary-foreground border-primary' : 'bg-card text-muted-foreground hover:text-foreground')}>
              {s === 'all' ? 'All' : s}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map(agent => {
          const typeCfg = AGENT_TYPE_CONFIG[agent.type] ?? { icon: <BrainCircuit className="h-5 w-5" />, color: 'text-slate-500 bg-slate-500/10 border-slate-500/30' }
          const statusCfg = STATUS_CONFIG[agent.status]
          return (
            <Card key={agent.id} className="p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border', typeCfg.color)}>
                  {typeCfg.icon}
                </div>
                <Badge className={cn('text-[10px] border', statusCfg.color)}>
                  {statusCfg.icon}{statusCfg.label}
                </Badge>
              </div>
              <h3 className="text-sm font-semibold">{agent.name}</h3>
              <p className="text-[10px] text-muted-foreground capitalize mt-0.5">{agent.domain} · v{agent.version}</p>
              <div className="mt-3 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Health</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className={cn('h-full rounded-full', agent.health >= 90 ? 'bg-green-500' : agent.health >= 70 ? 'bg-amber-500' : 'bg-red-500')}
                        style={{ width: `${agent.health}%` }} />
                    </div>
                    <span className={cn('font-medium', agent.health >= 90 ? 'text-green-500' : agent.health >= 70 ? 'text-amber-500' : 'text-red-500')}>{agent.health}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Active Tasks</span>
                  <span className="font-medium">{agent.activeTasks}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Success Rate</span>
                  <span className="font-medium">{agent.successRate}%</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Avg Runtime</span>
                  <span className="font-medium">{agent.averageRuntime.toFixed(1)}s</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Total Executions</span>
                  <span className="font-medium">{agent.totalExecutions.toLocaleString()}</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-border">
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.map(c => (
                    <Badge key={c} variant="outline" className="text-[9px]">{c}</Badge>
                  ))}
                </div>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
