import { Link, useSearchParams } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useInteractions, useInteractionsTimeline } from '@/services/interactionApiService'
import type { InteractionType, InteractionStatus } from '@/types/interactions'

const TYPE_LABELS: Record<InteractionType, string> = { email: 'Email', meeting: 'Meeting', crm_update: 'CRM Update', call_transcript: 'Call Transcript', chat: 'Chat', complaint: 'Complaint', feedback: 'Feedback', service_request: 'Service Request' }
const TYPE_COLORS: Record<InteractionType, string> = { email: '#3b82f6', meeting: '#8b5cf6', crm_update: '#06b6d4', call_transcript: '#10b981', chat: '#f59e0b', complaint: '#ef4444', feedback: '#22c55e', service_request: '#f97316' }
const STATUS_BADGES: Record<InteractionStatus, { label: string; class: string }> = { resolved: { label: 'Resolved', class: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' }, pending: { label: 'Pending', class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' }, escalated: { label: 'Escalated', class: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' } }
const isInteractionType = (value: string): value is InteractionType => value in TYPE_LABELS
const isInteractionStatus = (value: string): value is InteractionStatus => value in STATUS_BADGES
const INTERACTION_TYPES: { value: string; label: string }[] = [
  { value: '', label: 'All Types' }, { value: 'email', label: 'Email' }, { value: 'meeting', label: 'Meeting' },
  { value: 'crm_update', label: 'CRM Update' }, { value: 'call_transcript', label: 'Call Transcript' },
  { value: 'chat', label: 'Chat' }, { value: 'complaint', label: 'Complaint' }, { value: 'feedback', label: 'Feedback' },
  { value: 'service_request', label: 'Service Request' },
]

export default function InteractionsList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const type = searchParams.get('type') || ''
  const statusParam = searchParams.get('status') || ''
  const search = searchParams.get('search') || ''
  const page = parseInt(searchParams.get('page') || '1')
  const viewMode = searchParams.get('view') || 'list'

  const interactionsQuery = useInteractions({
    type: isInteractionType(type) ? type : undefined,
    status: isInteractionStatus(statusParam) ? statusParam : undefined,
    search: search || undefined,
    page,
    limit: 12,
  })

  const timelineQuery = useInteractionsTimeline({
    type: isInteractionType(type) ? type : undefined,
  })

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => { if (v) next.set(k, v); else next.delete(k) })
    if (updates.type !== undefined || updates.status !== undefined || updates.search !== undefined || updates.view !== undefined) next.delete('page')
    setSearchParams(next)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Customer Interactions</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Track and manage all customer communications</p>
        </div>
        <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-700 rounded-lg p-1">
          <button onClick={() => updateParams({ view: 'list' })} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${viewMode === 'list' ? 'bg-white dark:bg-slate-600 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'}`}>List</button>
          <button onClick={() => updateParams({ view: 'timeline' })} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${viewMode === 'timeline' ? 'bg-white dark:bg-slate-600 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'}`}>Timeline</button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <input type="text" placeholder="Search interactions..." value={search} onChange={(e) => updateParams({ search: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm min-w-[280px] focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <select value={type} onChange={(e) => updateParams({ type: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          {INTERACTION_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <select value={statusParam} onChange={(e) => updateParams({ status: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Status</option>
          <option value="resolved">Resolved</option>
          <option value="pending">Pending</option>
          <option value="escalated">Escalated</option>
        </select>
      </div>

      {interactionsQuery.error && <ErrorState message={interactionsQuery.error.message} onRetry={() => interactionsQuery.refetch()} />}
      {interactionsQuery.isLoading && <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>}

      {!interactionsQuery.isLoading && !interactionsQuery.error && viewMode === 'list' && (
        <>
          {interactionsQuery.data?.items?.length === 0 ? <EmptyState title="No interactions found" description="Try adjusting your filters or search terms." />
            : <div className="space-y-3">
                {interactionsQuery.data?.items?.map((item) => (
                  <Link key={item.id} to={`/interactions/${item.id}`} className="block bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="w-2 h-2 rounded-full mt-2 shrink-0" style={{ backgroundColor: TYPE_COLORS[item.type as InteractionType] || '#94a3b8' }} />
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: TYPE_COLORS[item.type as InteractionType] }}>{TYPE_LABELS[item.type as InteractionType] || item.type}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${STATUS_BADGES[item.status as InteractionStatus]?.class || ''}`}>{STATUS_BADGES[item.status as InteractionStatus]?.label || item.status}</span>
                          </div>
                          <h3 className="font-medium text-slate-900 dark:text-white">{item.subject}</h3>
                          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">{item.content}</p>
                          <div className="flex items-center gap-3 mt-2 text-xs text-slate-400 dark:text-slate-500">
                            <span>{item.customerName}</span>
                            <span>{item.agent}</span>
                            <span>{new Date(item.date).toLocaleString()}</span>
                            {item.attachments.length > 0 && <span>{item.attachments.length} attachment(s)</span>}
                          </div>
                        </div>
                      </div>
                      <svg className="w-5 h-5 text-slate-300 dark:text-slate-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                    </div>
                  </Link>
                ))}
              </div>}
          {interactionsQuery.data?.total && interactionsQuery.data.total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-4">
              <button disabled={page <= 1} onClick={() => updateParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Previous</button>
              <span className="text-sm text-slate-500 dark:text-slate-400">Page {page} of {Math.ceil(interactionsQuery.data.total / 12)}</span>
              <button disabled={page >= Math.ceil(interactionsQuery.data.total / 12)} onClick={() => updateParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Next</button>
            </div>
          )}
        </>
      )}

      {!interactionsQuery.isLoading && !interactionsQuery.error && viewMode === 'timeline' && (
        <>
          {timelineQuery.data?.groups?.length === 0 ? <EmptyState title="No interactions found" description="No interactions match your current filters." />
            : <div className="space-y-8">
                {timelineQuery.data?.groups?.map((group) => (
                  <div key={group.date}>
                    <h3 className="text-sm font-semibold text-slate-400 dark:text-slate-500 mb-3 sticky top-0 bg-slate-50 dark:bg-slate-900 py-2">{group.date}</h3>
                    <div className="space-y-3">
                      {group.interactions.map((item) => (
                        <Link key={item.id} to={`/interactions/${item.id}`} className="block bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 hover:shadow-md transition-shadow">
                          <div className="flex items-start gap-4">
                            <div className="w-2 h-2 rounded-full mt-2 shrink-0" style={{ backgroundColor: TYPE_COLORS[item.type as InteractionType] || '#94a3b8' }} />
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: TYPE_COLORS[item.type as InteractionType] }}>{TYPE_LABELS[item.type as InteractionType] || item.type}</span>
                                <span className={`text-xs px-2 py-0.5 rounded ${STATUS_BADGES[item.status as InteractionStatus]?.class || ''}`}>{STATUS_BADGES[item.status as InteractionStatus]?.label || item.status}</span>
                                <span className="text-xs text-slate-400 ml-auto">{new Date(item.date).toLocaleTimeString()}</span>
                              </div>
                              <h4 className="font-medium text-slate-900 dark:text-white">{item.subject}</h4>
                              <p className="text-sm text-slate-500 mt-1 line-clamp-1">{item.content}</p>
                              <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
                                <span>{item.customerName}</span>
                                <span>{item.agent}</span>
                              </div>
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
              </div>}
        </>
      )}
    </div>
  )
}
