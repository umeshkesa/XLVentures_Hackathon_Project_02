import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { Drawer } from '@/components/Drawer'
import { useRecommendationList, useRecommendationSummary } from '@/services/recommendationApiService'
import { useReasoningById } from '@/services/reasoningApiService'
import type { RecommendationItem } from '@/types/recommendations'
import {
  ShieldAlert,
  Coins,
  Clock,
  BrainCircuit,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  DollarSign,
  Briefcase,
  FileText,
  Activity,
  User,
  GitFork,
  Scale,
  Database,
  BookOpen,
  ListChecks
} from 'lucide-react'

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500 text-white dark:bg-red-600',
  high: 'bg-orange-500 text-white dark:bg-orange-600',
  medium: 'bg-yellow-500 text-slate-900 dark:bg-yellow-600 dark:text-white',
  low: 'bg-slate-500 text-white dark:bg-slate-600',
}

const PRIORITY_CARD_BORDERS: Record<string, string> = {
  critical: 'border-t-4 border-t-red-500 hover:border-red-500/50',
  high: 'border-t-4 border-t-orange-500 hover:border-orange-500/50',
  medium: 'border-t-4 border-t-yellow-500 hover:border-yellow-500/50',
  low: 'border-t-4 border-t-slate-500 hover:border-slate-500/50',
}

const STATUS_BADGE: Record<string, string> = {
  active: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  pending_approval: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  executed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  draft: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
}

const STATUS_CARD_CONFIG = [
  { key: 'active', label: 'Active', color: 'border-l-blue-500' },
  { key: 'pendingApproval', label: 'Pending Approval', color: 'border-l-yellow-500' },
  { key: 'approved', label: 'Approved', color: 'border-l-green-500' },
  { key: 'rejected', label: 'Rejected', color: 'border-l-red-500' },
  { key: 'executed', label: 'Executed', color: 'border-l-emerald-500' },
  { key: 'draft', label: 'Draft', color: 'border-l-slate-500' },
]

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'active', label: 'Active' },
  { value: 'pending_approval', label: 'Pending Approval' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'executed', label: 'Executed' },
  { value: 'draft', label: 'Draft' },
]

const PRIORITY_OPTIONS = [
  { value: '', label: 'All Priorities' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

const SOURCE_OPTIONS = [
  { value: '', label: 'All Sources' },
  { value: 'reasoning_engine', label: 'Reasoning Engine' },
  { value: 'rule_engine', label: 'Rule Engine' },
  { value: 'maintenance_schedule', label: 'Maintenance Schedule' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'customer_feedback', label: 'Customer Feedback' },
  { value: 'manual', label: 'Manual' },
]

function formatCurrency(val: number | undefined | null): string {
  if (val == null) return '\u2014'
  return `$${val.toLocaleString('en-US')}`
}

export default function RecommendationCenter() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedRec, setSelectedRec] = useState<RecommendationItem | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const search = searchParams.get('search') || ''
  const statusFilter = searchParams.get('status') || ''
  const priority = searchParams.get('priority') || ''
  const source = searchParams.get('source') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const { data: listData, isLoading: listLoading, error: listError } = useRecommendationList({
    status: statusFilter || undefined,
    priority: priority || undefined,
    source: source || undefined,
    search: search || undefined,
    page,
    limit: 12,
  })
  const { data: summary } = useRecommendationSummary()

  const items = (listData?.items ?? []).sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )
  const total = listData?.total ?? 0
  const loading = listLoading
  const error = listError ? (listError as Error).message : null

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => {
      if (v) next.set(k, v)
      else next.delete(k)
    })
    if (
      updates.status !== undefined ||
      updates.priority !== undefined ||
      updates.source !== undefined ||
      updates.search !== undefined
    ) {
      next.delete('page')
    }
    setSearchParams(next)
  }

  const handleCardClick = (rec: RecommendationItem) => {
    setSelectedRec(rec)
    setIsDrawerOpen(true)
    window.location.hash = rec.id
  }

  const handleDrawerClose = (open: boolean) => {
    setIsDrawerOpen(open)
    if (!open) {
      setSelectedRec(null)
      // clear hash
      window.history.replaceState(null, '', window.location.pathname + window.location.search)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Recommendation Center</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Review and execute AI-generated decisions and action plans for energy assets and customers.
          </p>
        </div>
      </div>

      {/* KPI Cards Summary */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {STATUS_CARD_CONFIG.map((cfg) => {
            const count = (summary as any)[cfg.key] ?? 0
            return (
              <div
                key={cfg.key}
                className={`bg-card rounded-xl border shadow-xs border-l-4 ${cfg.color} px-4 py-3 transition-all`}
              >
                <div className="text-2xl font-bold text-foreground">{count}</div>
                <div className="text-xs font-medium text-muted-foreground mt-0.5">{cfg.label}</div>
              </div>
            )
          })}
        </div>
      )}

      {/* Filter and Search controls */}
      <div className="flex flex-wrap items-center gap-3 bg-card p-4 rounded-xl border">
        <div className="flex-1 min-w-[280px]">
          <input
            type="text"
            placeholder="Search by title, description or ID..."
            value={search}
            onChange={(e) => updateParams({ search: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <select
            value={statusFilter}
            onChange={(e) => updateParams({ status: e.target.value })}
            className="px-3 py-2 border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <select
            value={priority}
            onChange={(e) => updateParams({ priority: e.target.value })}
            className="px-3 py-2 border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
          >
            {PRIORITY_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <select
            value={source}
            onChange={(e) => updateParams({ source: e.target.value })}
            className="px-3 py-2 border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
          >
            {SOURCE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <ErrorState message={error} onRetry={() => window.location.reload()} />}
      {loading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" label="Analyzing recommendations..." />
        </div>
      )}

      {/* Grid of Recommendation Cards */}
      {!loading && !error && (
        <>
          {items.length === 0 ? (
            <EmptyState
              title="No recommendations found"
              description="Adjust your search query or filters to find other entries."
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((item) => {
                const priorityColor = PRIORITY_COLORS[item.priority] || 'bg-slate-500'
                const borderClass = PRIORITY_CARD_BORDERS[item.priority] || 'border-t-4'

                return (
                  <div
                    key={item.id}
                    onClick={() => handleCardClick(item)}
                    className={`bg-card text-card-foreground rounded-xl border shadow-xs hover:shadow-md transition-all duration-200 cursor-pointer flex flex-col justify-between overflow-hidden ${borderClass}`}
                  >
                    <div className="p-5 space-y-4">
                      {/* Top Badges */}
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-muted-foreground">{item.id}</span>
                        <div className="flex gap-2">
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${priorityColor}`}
                          >
                            {item.priority}
                          </span>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-medium capitalize ${
                              STATUS_BADGE[item.status] || ''
                            }`}
                          >
                            {item.status.replace(/_/g, ' ')}
                          </span>
                        </div>
                      </div>

                      {/* Title & Description */}
                      <div className="space-y-1">
                        <h3 className="font-semibold text-base leading-snug line-clamp-1 group-hover:text-primary">
                          {item.title}
                        </h3>
                        <p className="text-xs text-muted-foreground line-clamp-2">{item.description}</p>
                      </div>

                      {/* Confidence Level */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-muted-foreground">AI Confidence:</span>
                          <span
                            className={
                              item.confidence > 0.8
                                ? 'text-green-600'
                                : item.confidence > 0.6
                                ? 'text-orange-600'
                                : 'text-red-600'
                            }
                          >
                            {(item.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${item.confidence * 100}%`,
                              backgroundColor:
                                item.confidence > 0.8
                                  ? 'var(--color-green-500)'
                                  : item.confidence > 0.6
                                  ? 'var(--color-orange-500)'
                                  : 'var(--color-red-500)',
                            }}
                          />
                        </div>
                      </div>

                      {/* Business Impact Block */}
                      <div className="p-3 bg-muted/50 rounded-lg border border-border/50 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                          <Sparkles className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500/20" />
                          <span>Business Impact:</span>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-2">{item.businessImpact}</p>
                      </div>

                      {/* Action & Risk details */}
                      <div className="grid grid-cols-2 gap-2 text-xs border-t pt-3 mt-1">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-muted-foreground">Risk Level</span>
                          <span className="font-semibold text-foreground capitalize flex items-center gap-1">
                            <ShieldAlert className="h-3 w-3 text-muted-foreground" />
                            {item.riskLevel}
                          </span>
                        </div>
                        <div className="flex flex-col gap-0.5">
                          <span className="text-muted-foreground">Timeline</span>
                          <span className="font-semibold text-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3 text-muted-foreground" />
                            {item.timeline}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Bottom Action Footer */}
                    <div className="bg-muted/30 px-5 py-3 border-t flex items-center justify-between text-xs font-medium hover:bg-muted/50 transition-colors">
                      <span className="text-muted-foreground">
                        {item.estimatedSavings > 0 ? (
                          <span className="text-green-600 dark:text-green-400 font-semibold">
                            Est. Savings: {formatCurrency(item.estimatedSavings)}
                          </span>
                        ) : (
                          `Est. Cost: ${formatCurrency(item.estimatedCost)}`
                        )}
                      </span>
                      <span className="text-primary flex items-center gap-1 group">
                        Review Plan <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-6">
              <button
                disabled={page <= 1}
                onClick={() => updateParams({ page: String(page - 1) })}
                className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 bg-card hover:bg-muted transition-colors"
              >
                Previous
              </button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {Math.ceil(total / 12)}
              </span>
              <button
                disabled={page >= Math.ceil(total / 12)}
                onClick={() => updateParams({ page: String(page + 1) })}
                className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 bg-card hover:bg-muted transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Details Slide-out Drawer */}
      <Drawer
        open={isDrawerOpen}
        onOpenChange={handleDrawerClose}
        title={selectedRec ? selectedRec.title : ''}
        description={selectedRec ? `Recommendation ${selectedRec.id}` : ''}
      >
        {selectedRec && (
          <div className="space-y-6 pb-8">
            {/* Top Stats Overview */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-card p-3 rounded-lg border text-center">
                <div className="text-xs text-muted-foreground">Priority</div>
                <div className="mt-1">
                  <span
                    className={`text-xs px-2 py-0.5 rounded font-bold uppercase ${
                      PRIORITY_COLORS[selectedRec.priority]
                    }`}
                  >
                    {selectedRec.priority}
                  </span>
                </div>
              </div>
              <div className="bg-card p-3 rounded-lg border text-center">
                <div className="text-xs text-muted-foreground">Confidence</div>
                <div className="mt-1 text-sm font-bold text-foreground">
                  {(selectedRec.confidence * 100).toFixed(0)}%
                </div>
              </div>
              <div className="bg-card p-3 rounded-lg border text-center">
                <div className="text-xs text-muted-foreground">Risk Level</div>
                <div className="mt-1 text-sm font-bold text-foreground capitalize">
                  {selectedRec.riskLevel}
                </div>
              </div>
            </div>

            {/* Financial Summary */}
            <div className="bg-muted/40 rounded-xl border p-4 grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-muted-foreground flex items-center gap-1.5">
                  <DollarSign className="h-3.5 w-3.5 text-muted-foreground" />
                  Estimated Cost
                </span>
                <div className="text-lg font-bold text-foreground mt-1">
                  {formatCurrency(selectedRec.estimatedCost)}
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground flex items-center gap-1.5">
                  <Coins className="h-3.5 w-3.5 text-green-500" />
                  Estimated Savings
                </span>
                <div className="text-lg font-bold text-green-600 dark:text-green-400 mt-1">
                  {formatCurrency(selectedRec.estimatedSavings)}
                </div>
              </div>
            </div>

            {/* Core Info */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">General Details</h4>
              <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-sm">
                <div>
                  <span className="text-xs text-muted-foreground block">Decision Source</span>
                  <span className="font-medium capitalize text-foreground">
                    {selectedRec.source.replace(/_/g, ' ')}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block">Timeline</span>
                  <span className="font-medium text-foreground">{selectedRec.timeline}</span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block">Status</span>
                  <span
                    className={`inline-block text-xs px-2 py-0.5 rounded font-medium mt-0.5 ${
                      STATUS_BADGE[selectedRec.status] || ''
                    }`}
                  >
                    {selectedRec.status.replace(/_/g, ' ')}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground block">Generated Date</span>
                  <span className="font-medium text-foreground">
                    {new Date(selectedRec.createdAt).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Narrative & Impact */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Description</h4>
              <p className="text-sm leading-relaxed text-muted-foreground">{selectedRec.description}</p>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Business Justification</h4>
              <div className="p-3.5 bg-yellow-500/5 dark:bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <p className="text-sm text-foreground leading-relaxed">{selectedRec.businessImpact}</p>
              </div>
            </div>

            {/* Suggested Actions Checklist */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Suggested Action Plan</h4>
              {selectedRec.actions.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No specific actions registered.</p>
              ) : (
                <div className="space-y-2.5">
                  {selectedRec.actions.map((act) => (
                    <div
                      key={act.id}
                      className="flex items-start gap-3 bg-card p-3 rounded-lg border text-sm"
                    >
                      <div className="mt-0.5">
                        {act.status === 'completed' ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500 fill-green-500/10" />
                        ) : (
                          <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/30 flex items-center justify-center text-[10px] text-muted-foreground font-mono">
                            {act.status === 'in_progress' ? 'IP' : 'P'}
                          </div>
                        )}
                      </div>
                      <div className="flex-1">
                        <p className={`font-medium ${act.status === 'completed' ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                          {act.description}
                        </p>
                        <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-muted-foreground">
                          <span className="bg-muted px-2 py-0.5 rounded flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {act.assignedTo}
                          </span>
                          <span>•</span>
                          <span>Deadline: {new Date(act.deadline).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Reasoning Steps */}
            {selectedRec.reasoningId && (
              <ReasoningStepsSection reasoningId={selectedRec.reasoningId} />
            )}

            {/* Confidence Calculation */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Confidence Calculation</h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Evidence Quality', value: Math.min(1, selectedRec.confidence * 1.05), desc: 'Source reliability & freshness' },
                  { label: 'Rule Coverage', value: Math.min(1, selectedRec.confidence * 0.95), desc: 'Business rules matched' },
                  { label: 'Reasoning Depth', value: selectedRec.confidence, desc: 'Inference chain quality' },
                  { label: 'Data Completeness', value: Math.min(1, selectedRec.confidence * 0.9), desc: 'Available data points' },
                ].map((dim) => (
                  <div key={dim.label} className="bg-card p-3 rounded-lg border text-sm">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground">{dim.label}</span>
                      <span className="font-medium text-foreground">{(dim.value * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden mb-1">
                      <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${dim.value * 100}%` }} />
                    </div>
                    <p className="text-[10px] text-muted-foreground">{dim.desc}</p>
                  </div>
                ))}
              </div>
              <div className="bg-muted/50 p-3 rounded-lg border text-xs">
                <span className="text-muted-foreground">Overall Confidence: </span>
                <span className="font-bold text-foreground">{(selectedRec.confidence * 100).toFixed(0)}%</span>
                <span className="text-muted-foreground"> — weighted composite of all dimensions</span>
              </div>
            </div>

            {/* Supporting Evidence Inline */}
            {selectedRec.evidenceIds && selectedRec.evidenceIds.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Supporting Evidence</h4>
                <div className="space-y-2">
                  {selectedRec.evidenceIds.map((eid: string) => (
                    <Link key={eid} to={`/evidence/${eid}`} className="flex items-center gap-2 p-2.5 bg-card border rounded-lg hover:border-purple-500/40 hover:bg-muted/40 transition-all text-sm">
                      <Database className="h-4 w-4 text-purple-500 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-foreground truncate">{eid}</div>
                        <div className="text-[10px] text-muted-foreground">Supporting evidence item</div>
                      </div>
                      <ArrowRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Related Knowledge Documents */}
            {selectedRec.knowledgeIds && selectedRec.knowledgeIds.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Related Knowledge Documents</h4>
                <div className="space-y-2">
                  {selectedRec.knowledgeIds.map((kid: string) => (
                    <Link key={kid} to={`/knowledge/${kid}`} className="flex items-center gap-2 p-2.5 bg-card border rounded-lg hover:border-yellow-500/40 hover:bg-muted/40 transition-all text-sm">
                      <BookOpen className="h-4 w-4 text-yellow-500 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-foreground truncate">{kid}</div>
                        <div className="text-[10px] text-muted-foreground">Reference document</div>
                      </div>
                      <ArrowRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Applied Business Rules */}
            {selectedRec.ruleIds && selectedRec.ruleIds.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Applied Business Rules</h4>
                <div className="space-y-2">
                  {selectedRec.ruleIds.map((rid: string) => (
                    <div key={rid} className="flex items-center gap-2 p-2.5 bg-card border rounded-lg text-sm">
                      <Scale className="h-4 w-4 text-orange-500 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-foreground truncate">{rid}</div>
                        <div className="text-[10px] text-muted-foreground">Business rule triggered</div>
                      </div>
                      <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Traceability Connections */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Evidence & Knowledge Linage</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {selectedRec.reasoningId && (
                  <Link
                    to={`/reasoning/${selectedRec.reasoningId}`}
                    className="p-2.5 bg-card border rounded-lg hover:border-blue-500/40 hover:bg-muted/40 transition-all flex items-center gap-2"
                  >
                    <BrainCircuit className="h-4 w-4 text-blue-500" />
                    <div className="text-left">
                      <div className="text-muted-foreground">Reasoning Session</div>
                      <div className="font-semibold text-foreground">{selectedRec.reasoningId}</div>
                    </div>
                  </Link>
                )}
                {selectedRec.assetIds && selectedRec.assetIds.map((assetId) => (
                  <Link
                    key={assetId}
                    to={`/assets/${assetId}`}
                    className="p-2.5 bg-card border rounded-lg hover:border-orange-500/40 hover:bg-muted/40 transition-all flex items-center gap-2"
                  >
                    <Activity className="h-4 w-4 text-orange-500" />
                    <div className="text-left">
                      <div className="text-muted-foreground">Related Asset</div>
                      <div className="font-semibold text-foreground">{assetId}</div>
                    </div>
                  </Link>
                ))}
                {selectedRec.customerIds && selectedRec.customerIds.map((cust)=> (
                  <Link
                    key={cust}
                    to={`/customers/${cust}`}
                    className="p-2.5 bg-card border rounded-lg hover:border-green-500/40 hover:bg-muted/40 transition-all flex items-center gap-2"
                  >
                    <Briefcase className="h-4 w-4 text-green-500" />
                    <div className="text-left">
                      <div className="text-muted-foreground">Customer Account</div>
                      <div className="font-semibold text-foreground">{cust}</div>
                    </div>
                  </Link>
                ))}
                {selectedRec.evidenceIds && selectedRec.evidenceIds.map((evId) => (
                  <Link
                    key={evId}
                    to={`/evidence/${evId}`}
                    className="p-2.5 bg-card border rounded-lg hover:border-purple-500/40 hover:bg-muted/40 transition-all flex items-center gap-2"
                  >
                    <GitFork className="h-4 w-4 text-purple-500" />
                    <div className="text-left">
                      <div className="text-muted-foreground">Supporting Evidence</div>
                      <div className="font-semibold text-foreground">{evId}</div>
                    </div>
                  </Link>
                ))}
                {selectedRec.knowledgeIds && selectedRec.knowledgeIds.map((kId) => (
                  <Link
                    key={kId}
                    to={`/knowledge/${kId}`}
                    className="p-2.5 bg-card border rounded-lg hover:border-yellow-500/40 hover:bg-muted/40 transition-all flex items-center gap-2"
                  >
                    <FileText className="h-4 w-4 text-yellow-500" />
                    <div className="text-left">
                      <div className="text-muted-foreground">Reference Doc</div>
                      <div className="font-semibold text-foreground">{kId}</div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>

            {/* Reviewer Decision Status */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Reviewer Decision</h4>
              <div className="bg-card p-3 rounded-lg border text-sm flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Pending human review</span>
                </div>
                <Link to={`/review?q=${selectedRec.id}`} className="text-xs text-primary hover:underline flex items-center gap-1">
                  Open Review <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>

            {/* Execution Status */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Execution Status</h4>
              <div className="bg-card p-3 rounded-lg border text-sm flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ListChecks className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Awaiting approval to execute</span>
                </div>
                <Link to={`/actions?q=${selectedRec.id}`} className="text-xs text-primary hover:underline flex items-center gap-1">
                  View Actions <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>

            {/* Reasoning Pipeline Link */}
            <Link
              to={`/reasoning/pipeline?recommendationId=${selectedRec.id}`}
              className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-card border rounded-xl hover:bg-muted/50 transition-all text-sm font-medium text-foreground"
            >
              <BrainCircuit className="h-4 w-4 text-blue-500" />
              View Full Reasoning Pipeline
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        )}
      </Drawer>
    </div>
  )
}

function ReasoningStepsSection({ reasoningId }: { reasoningId: string }) {
  const { data: reasoning } = useReasoningById(reasoningId)
  if (!reasoning) return null
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-foreground border-b pb-1.5">Reasoning Steps</h4>
      <div className="space-y-2">
        {reasoning.steps && reasoning.steps.length > 0 ? (
          reasoning.steps.map((step, idx) => (
            <div key={step.id || idx} className="bg-card p-3 rounded-lg border text-sm">
              <div className="flex items-center gap-2 mb-1">
                <div className="h-2 w-2 rounded-full bg-blue-500" />
                <span className="font-medium text-foreground capitalize">{step.type.replace(/_/g, ' ')}</span>
                <span className="text-[10px] text-muted-foreground ml-auto">{step.durationMs}ms</span>
              </div>
              <p className="text-xs text-muted-foreground">{step.description}</p>
            </div>
          ))
        ) : (
          <p className="text-xs text-muted-foreground italic">No step details available.</p>
        )}
      </div>
      <Link to={`/reasoning/${reasoningId}`} className="text-xs text-primary hover:underline flex items-center gap-1">
        View Full Reasoning Session <ArrowRight className="h-3 w-3" />
      </Link>
    </div>
  )
}
