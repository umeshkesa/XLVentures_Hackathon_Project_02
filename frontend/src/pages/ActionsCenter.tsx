import { useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { Drawer } from '@/components/Drawer'
import { useExecutionList, useExecutionSummary } from '@/services/executionApiService'
import type { ExecutionItem } from '@/types/execution'
import {
  CheckCircle2, Clock, ArrowRight, User, Calendar, AlertCircle, Play, Activity, ListChecks
} from 'lucide-react'

const STATUS_BADGE: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
  approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  scheduled: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  in_progress: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  completed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  cancelled: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
}

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500 text-white',
  high: 'bg-orange-500 text-white',
  medium: 'bg-yellow-500 text-slate-900',
  low: 'bg-slate-500 text-white',
}

const STEP_STATUS_ICON: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="h-5 w-5 text-green-500" />,
  in_progress: <Play className="h-5 w-5 text-blue-500" />,
  pending: <Clock className="h-5 w-5 text-muted-foreground/50" />,
}

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'scheduled', label: 'Scheduled' },
]

const SUMMARY_CARDS = [
  { key: 'pending', label: 'Pending', color: 'border-l-slate-500' },
  { key: 'inProgress', label: 'In Progress', color: 'border-l-blue-500' },
  { key: 'completed', label: 'Completed', color: 'border-l-emerald-500' },
  { key: 'cancelled', label: 'Cancelled', color: 'border-l-red-500' },
]

export default function ActionsCenter() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedAction, setSelectedAction] = useState<ExecutionItem | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const search = searchParams.get('search') || ''
  const statusFilter = searchParams.get('status') || ''
  const priority = searchParams.get('priority') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const { data: listData, isLoading: listLoading, error: listError } = useExecutionList({
    status: statusFilter || undefined,
    priority: priority || undefined,
    search: search || undefined,
    page,
    limit: 12,
  })
  const { data: summary } = useExecutionSummary()

  const items = (listData?.items ?? []).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  const total = listData?.total ?? 0
  const loading = listLoading
  const error = listError ? (listError as Error).message : null

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => {
      if (v) next.set(k, v)
      else next.delete(k)
    })
    if (updates.status !== undefined || updates.priority !== undefined || updates.search !== undefined) {
      next.delete('page')
    }
    setSearchParams(next)
  }

  const handleCardClick = (a: ExecutionItem) => {
    setSelectedAction(a)
    setIsDrawerOpen(true)
  }

  const completedSteps = (steps: ExecutionItem['steps']) => steps.filter((s) => s.status === 'completed').length

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Action Execution</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Track and manage the execution of approved recommendations.
          </p>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SUMMARY_CARDS.map((cfg) => (
            <div key={cfg.key} className={`bg-card rounded-xl border shadow-xs border-l-4 ${cfg.color} px-4 py-3 transition-all`}>
              <div className="text-2xl font-bold text-foreground">{(summary as any)[cfg.key] ?? 0}</div>
              <div className="text-xs font-medium text-muted-foreground mt-0.5">{cfg.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3 bg-card p-4 rounded-xl border">
        <div className="flex-1 min-w-[280px]">
          <input type="text" placeholder="Search actions by title or ID..." value={search} onChange={(e) => updateParams({ search: e.target.value })} className="w-full px-3 py-2 border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" />
        </div>
        <div className="flex flex-wrap gap-2">
          <select value={statusFilter} onChange={(e) => updateParams({ status: e.target.value })} className="px-3 py-2 border rounded-lg bg-background text-sm">
            {STATUS_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <select value={priority} onChange={(e) => updateParams({ priority: e.target.value })} className="px-3 py-2 border rounded-lg bg-background text-sm">
            <option value="">All Priorities</option>
            {['critical', 'high', 'medium', 'low'].map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
          </select>
        </div>
      </div>

      {error && <ErrorState message={error} onRetry={() => window.location.reload()} />}
      {loading && <div className="flex justify-center py-12"><LoadingSpinner size="lg" label="Loading actions..." /></div>}

      {!loading && !error && (
        <>
          {items.length === 0 ? (
            <EmptyState title="No actions found" description="Approved recommendations will appear here." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((a) => (
                <div key={a.action_id} onClick={() => handleCardClick(a)} className="bg-card rounded-xl border shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col overflow-hidden">
                  <div className="p-4 space-y-3 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono text-muted-foreground">{a.action_id}</span>
                      <div className="flex gap-1.5">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${PRIORITY_COLORS[a.priority] || ''}`}>{a.priority}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium capitalize ${STATUS_BADGE[a.status] || ''}`}>{a.status.replace(/_/g, ' ')}</span>
                      </div>
                    </div>
                    <h3 className="font-semibold text-sm leading-snug line-clamp-2">{a.title}</h3>
                    <p className="text-xs text-muted-foreground line-clamp-2">{a.description}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <ListChecks className="h-3 w-3" />
                      <span>{completedSteps(a.steps)}/{a.steps.length} steps</span>
                    </div>
                    {a.steps.length > 0 && (
                      <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${(completedSteps(a.steps) / a.steps.length) * 100}%` }} />
                      </div>
                    )}
                  </div>
                  <div className="bg-muted/30 px-4 py-2.5 border-t flex items-center justify-between text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><User className="h-3 w-3" />{a.assigned_to || 'Unassigned'}</span>
                    <span className="flex items-center gap-1"><ArrowRight className="h-3 w-3" /> Details</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-6">
              <button disabled={page <= 1} onClick={() => updateParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 bg-card hover:bg-muted">Previous</button>
              <span className="text-sm text-muted-foreground">Page {page} of {Math.ceil(total / 12)}</span>
              <button disabled={page >= Math.ceil(total / 12)} onClick={() => updateParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 bg-card hover:bg-muted">Next</button>
            </div>
          )}
        </>
      )}

      <Drawer open={isDrawerOpen} onOpenChange={(o) => { setIsDrawerOpen(o); if (!o) setSelectedAction(null) }} title={selectedAction?.title || ''} description={selectedAction ? `Action ${selectedAction.action_id}` : ''}>
        {selectedAction && (
          <div className="space-y-6 pb-8">
            {/* Status & Assignee */}
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Status</span><span className={`inline-block text-xs px-2 py-0.5 rounded font-medium mt-1 capitalize ${STATUS_BADGE[selectedAction.status] || ''}`}>{selectedAction.status.replace(/_/g, ' ')}</span></div>
              <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Priority</span><span className={`inline-block text-xs px-2 py-0.5 rounded font-bold uppercase mt-1 ${PRIORITY_COLORS[selectedAction.priority] || ''}`}>{selectedAction.priority}</span></div>
              <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Assigned To</span><span className="font-medium text-foreground block mt-1 flex items-center gap-1"><User className="h-3 w-3 text-muted-foreground" />{selectedAction.assigned_to || <span className="text-muted-foreground italic">Unassigned</span>}</span></div>
              <div className="bg-card p-3 rounded-lg border"><span className="text-xs text-muted-foreground block">Scheduled</span><span className="font-medium text-foreground block mt-1 flex items-center gap-1"><Calendar className="h-3 w-3 text-muted-foreground" />{selectedAction.scheduled_date || <span className="text-muted-foreground italic">Not set</span>}</span></div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1">Description</h4>
              <p className="text-sm text-muted-foreground">{selectedAction.description}</p>
            </div>

            {/* Linked Recommendation & Review */}
            <div className="flex gap-2 flex-wrap">
              {selectedAction.recommendation_id && (
                <Link to={`/recommendations?id=${selectedAction.recommendation_id}`} className="flex items-center gap-1.5 px-3 py-2 bg-card border rounded-lg text-xs hover:border-primary/40 transition-all">
                  <Activity className="h-3.5 w-3.5 text-blue-500" />
                  Recommendation {selectedAction.recommendation_id}
                </Link>
              )}
              {selectedAction.review_id && (
                <Link to={`/review?id=${selectedAction.review_id}`} className="flex items-center gap-1.5 px-3 py-2 bg-card border rounded-lg text-xs hover:border-primary/40 transition-all">
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                  Review {selectedAction.review_id}
                </Link>
              )}
            </div>

            {/* Execution Timeline */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1">Execution Timeline</h4>
              {selectedAction.steps.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No steps defined.</p>
              ) : (
                <div className="space-y-0">
                  {selectedAction.steps.map((step, idx) => (
                    <div key={step.step} className="flex gap-3 text-sm">
                      <div className="flex flex-col items-center">
                        <div className="mt-0.5">{STEP_STATUS_ICON[step.status]}</div>
                        {idx < selectedAction.steps.length - 1 && <div className="w-px flex-1 bg-border" />}
                      </div>
                      <div className="pb-5 flex-1">
                        <p className={`font-medium ${step.status === 'completed' ? 'text-muted-foreground line-through' : step.status === 'in_progress' ? 'text-foreground' : 'text-muted-foreground/70'}`}>
                          {step.label}
                        </p>
                        {step.completed_at && (
                          <p className="text-[11px] text-muted-foreground mt-0.5 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(step.completed_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Audit History */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1">Audit Trail</h4>
              {selectedAction.audit_history.map((entry, idx) => (
                <div key={idx} className="flex gap-2 text-xs text-muted-foreground">
                  <AlertCircle className="h-3 w-3 mt-0.5 shrink-0" />
                  <div>
                    <span className="font-medium text-foreground capitalize">{entry.action.replace(/_/g, ' ')}</span> by {entry.by}
                    <span className="block">{entry.detail}</span>
                    <span className="block text-[10px]">{new Date(entry.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  )
}
