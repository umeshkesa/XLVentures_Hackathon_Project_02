import { useState } from 'react'
import { usePlans, useWorkflows } from '@/services/plannerApiService'
import { ORCHESTRATION_PIPELINE } from '@/types/planner'
import { cn } from '@/lib/utils'
import {
  ClipboardList, Search, GitBranch, BookOpen, FileSearch, Scale, Zap,
  BrainCircuit, ThumbsUp, ClipboardCheck, User, ChevronDown, ChevronRight,
  CheckCircle2, XCircle, Play, Clock, AlertCircle, ArrowRight,
} from 'lucide-react'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'

const STAGE_ICONS: Record<string, React.ReactNode> = {
  'user-request': <User className="h-4 w-4" />,
  'planner-agent': <ClipboardList className="h-4 w-4" />,
  'capability-discovery': <Search className="h-4 w-4" />,
  'workflow-engine': <GitBranch className="h-4 w-4" />,
  'knowledge-agent': <BookOpen className="h-4 w-4" />,
  'evidence-agent': <FileSearch className="h-4 w-4" />,
  'rules-agent': <Scale className="h-4 w-4" />,
  'energy-agent': <Zap className="h-4 w-4" />,
  'reasoning-engine': <BrainCircuit className="h-4 w-4" />,
  'recommendation-engine': <ThumbsUp className="h-4 w-4" />,
  'human-review': <ClipboardCheck className="h-4 w-4" />,
  'action-execution': <Zap className="h-4 w-4" />,
}

const STAGE_COLORS: Record<string, string> = {
  'user-request': 'bg-slate-500/10 border-slate-500/30 text-slate-500',
  'planner-agent': 'bg-blue-500/10 border-blue-500/30 text-blue-500',
  'capability-discovery': 'bg-cyan-500/10 border-cyan-500/30 text-cyan-500',
  'workflow-engine': 'bg-indigo-500/10 border-indigo-500/30 text-indigo-500',
  'knowledge-agent': 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500',
  'evidence-agent': 'bg-amber-500/10 border-amber-500/30 text-amber-500',
  'rules-agent': 'bg-rose-500/10 border-rose-500/30 text-rose-500',
  'energy-agent': 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500',
  'reasoning-engine': 'bg-violet-500/10 border-violet-500/30 text-violet-500',
  'recommendation-engine': 'bg-orange-500/10 border-orange-500/30 text-orange-500',
  'human-review': 'bg-pink-500/10 border-pink-500/30 text-pink-500',
  'action-execution': 'bg-green-500/10 border-green-500/30 text-green-500',
}

const STATUS_ICON: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  in_progress: <Play className="h-4 w-4 text-blue-500" />,
  failed: <XCircle className="h-4 w-4 text-red-500" />,
  pending: <Clock className="h-4 w-4 text-muted-foreground/50" />,
  skipped: <AlertCircle className="h-4 w-4 text-muted-foreground/50" />,
}

export default function PlannerVisualization() {
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set(['planner-agent', 'reasoning-engine', 'recommendation-engine']))
  const [activeTab, setActiveTab] = useState<'pipeline' | 'plans' | 'workflows'>('pipeline')
  const { data: plans = [], isLoading: plansLoading } = usePlans()
  const { data: workflows = [], isLoading: workflowsLoading } = useWorkflows()

  const toggleStage = (id: string) => {
    setExpandedStages(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Planner Visualization</h1>
        <p className="text-sm text-muted-foreground mt-1">End-to-end orchestration pipeline</p>
      </div>

      <div className="flex gap-1 border-b">
        {(['pipeline', 'plans', 'workflows'] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={cn('px-4 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize', activeTab === tab ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground')}>
            {tab === 'pipeline' ? 'Pipeline Flow' : tab}
          </button>
        ))}
      </div>

      {activeTab === 'pipeline' && (
        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500/50 via-violet-500/50 to-green-500/50 hidden lg:block" />
          <div className="space-y-3">
            {ORCHESTRATION_PIPELINE.map((stage, idx) => {
              const isExpanded = expandedStages.has(stage.id)
              return (
                <div key={stage.id} className="relative">
                  <div className="flex items-stretch gap-3">
                    <div className="hidden lg:flex flex-col items-center pt-2 w-16 shrink-0">
                      <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border-2', STAGE_COLORS[stage.id])}>
                        {STAGE_ICONS[stage.id]}
                      </div>
                      {idx < ORCHESTRATION_PIPELINE.length - 1 && (
                        <div className="flex-1 w-0.5 bg-gradient-to-b from-border to-transparent min-h-[20px]" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <button onClick={() => toggleStage(stage.id)}
                        className="w-full flex items-center gap-3 p-4 rounded-xl border bg-card hover:bg-muted/30 transition-all text-left group"
                      >
                        <div className={cn('lg:hidden flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border', STAGE_COLORS[stage.id])}>
                          {STAGE_ICONS[stage.id]}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-sm font-semibold">{stage.label}</span>
                            <Badge variant="outline" className="text-[10px]">{STATUS_ICON[stage.status]}{stage.status.replace('_', ' ')}</Badge>
                            {stage.confidence > 0 && (
                              <Badge variant="outline" className="text-[10px]">{Math.round(stage.confidence * 100)}% confidence</Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5">{stage.description}</p>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground shrink-0">
                          {stage.duration > 0 && <span>{stage.duration.toFixed(1)}s</span>}
                          {stage.agents.length > 0 && <span className="hidden sm:inline">{stage.agents.join(', ')}</span>}
                          {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                        </div>
                      </button>
                      {isExpanded && (
                        <div className="mt-2 ml-4 lg:ml-0 p-4 rounded-xl border bg-muted/20 space-y-3">
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                              <span className="text-[10px] font-semibold text-muted-foreground uppercase">Input</span>
                              <p className="text-xs text-muted-foreground mt-0.5">{stage.input}</p>
                            </div>
                            <div>
                              <span className="text-[10px] font-semibold text-muted-foreground uppercase">Output</span>
                              <p className="text-xs text-muted-foreground mt-0.5">{stage.output}</p>
                            </div>
                          </div>
                          {stage.agents.length > 0 && (
                            <div>
                              <span className="text-[10px] font-semibold text-muted-foreground uppercase">Agent(s)</span>
                              <div className="flex gap-2 mt-1">
                                {stage.agents.map(a => (
                                  <Badge key={a} variant="outline" className="text-[10px]">{a}</Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          {stage.status !== 'pending' && stage.duration > 0 && (
                            <div>
                              <span className="text-[10px] font-semibold text-muted-foreground uppercase">Performance</span>
                              <div className="flex items-center gap-4 mt-1">
                                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                                  <Clock className="h-3 w-3" /> {stage.duration.toFixed(1)}s
                                </div>
                                <div className="flex-1 max-w-[200px] h-1.5 rounded-full bg-muted overflow-hidden">
                                  <div className={cn('h-full rounded-full transition-all', stage.confidence > 0.8 ? 'bg-green-500' : stage.confidence > 0.6 ? 'bg-amber-500' : 'bg-red-500')}
                                    style={{ width: `${Math.round(stage.confidence * 100)}%` }} />
                                </div>
                                <span className="text-xs text-muted-foreground">{Math.round(stage.confidence * 100)}%</span>
                              </div>
                            </div>
                          )}
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <ArrowRight className="h-3 w-3" />
                            <span>Next: {idx < ORCHESTRATION_PIPELINE.length - 1 ? ORCHESTRATION_PIPELINE[idx + 1].label : 'Complete'}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {activeTab === 'plans' && (
        <div>
          {plansLoading ? (
            <div className="flex justify-center py-12"><LoadingSpinner /></div>
          ) : plans.length === 0 ? (
            <EmptyState title="No Plans Yet" description="Plans will appear here once the Planner Agent processes requests." icon={<ClipboardList className="h-12 w-12" />} />
          ) : (
            <div className="grid gap-3">{plans.map(p => (
              <Card key={p.plan_id} className="p-4"><div className="flex items-center justify-between"><div><h3 className="text-sm font-semibold">{p.title}</h3><p className="text-xs text-muted-foreground">{p.description}</p></div><Badge>{p.status}</Badge></div></Card>
            ))}</div>
          )}
        </div>
      )}

      {activeTab === 'workflows' && (
        <div>
          {workflowsLoading ? (
            <div className="flex justify-center py-12"><LoadingSpinner /></div>
          ) : workflows.length === 0 ? (
            <EmptyState title="No Workflows Yet" description="Workflows will appear here once the Workflow Engine executes plans." icon={<GitBranch className="h-12 w-12" />} />
          ) : (
            <div className="grid gap-3">{workflows.map(w => (
              <Card key={w.workflow_id} className="p-4"><div className="flex items-center justify-between"><div><h3 className="text-sm font-semibold">{w.name}</h3></div><Badge>{w.status}</Badge></div></Card>
            ))}</div>
          )}
        </div>
      )}
    </div>
  )
}
