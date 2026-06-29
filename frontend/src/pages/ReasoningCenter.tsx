import { Link, useSearchParams } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useReasoningList, useReasoningSummary } from '@/services/reasoningApiService'

const STATUS_CONFIG: Record<string, { label: string; class: string }> = {
  in_progress: { label: 'In Progress', class: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  completed: { label: 'Completed', class: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  failed: { label: 'Failed', class: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
}

const DOMAIN_COLORS: Record<string, string> = {
  energy: '#3b82f6',
  maintenance: '#f59e0b',
  safety: '#ef4444',
  compliance: '#8b5cf6',
  operations: '#06b6d4',
  customer: '#22c55e',
  general: '#6366f1',
}

const STATUS_OPTIONS = [
  { value: '', label: 'All Status' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
]

const DOMAIN_OPTIONS = [
  { value: '', label: 'All Domains' },
  { value: 'energy', label: 'Energy' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'safety', label: 'Safety' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'operations', label: 'Operations' },
  { value: 'customer', label: 'Customer' },
  { value: 'general', label: 'General' },
]

export default function ReasoningCenter() {
  const [searchParams, setSearchParams] = useSearchParams()

  const status = searchParams.get('status') || ''
  const domain = searchParams.get('domain') || ''
  const search = searchParams.get('search') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const { data: listData, isLoading: listLoading, error: listError } = useReasoningList({
    status: (status as any) || undefined,
    domain: (domain as any) || undefined,
    search: search || undefined,
    page,
    limit: 12,
  })
  const { data: summary } = useReasoningSummary()

  const items = listData?.items ?? []
  const total = listData?.total ?? 0
  const loading = listLoading
  const error = listError ? (listError as Error).message : null

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => { if (v) next.set(k, v); else next.delete(k) })
    if (updates.status !== undefined || updates.domain !== undefined || updates.search !== undefined) next.delete('page')
    setSearchParams(next)
  }

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reasoning Center</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Monitor AI reasoning sessions, review conclusions, and trace decision logic</p>
      </div>

      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-1">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              Active
            </div>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{summary.activeCount}</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-1">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Completed
            </div>
            <p className="text-2xl font-bold text-green-600">{summary.completedCount}</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-1">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
              Failed
            </div>
            <p className="text-2xl font-bold text-red-600">{summary.failedCount}</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-1">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              Avg Confidence
            </div>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{(summary.averageConfidence * 100).toFixed(0)}%</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-1">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Avg Risk Score
            </div>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{(summary.averageRiskScore * 100).toFixed(0)}%</p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <input type="text" placeholder="Search reasoning sessions..." value={search} onChange={(e) => updateParams({ search: e.target.value })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm min-w-[280px] focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <select value={status} onChange={(e) => updateParams({ status: e.target.value })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          {STATUS_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select value={domain} onChange={(e) => updateParams({ domain: e.target.value })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          {DOMAIN_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      {error && <ErrorState message={error} onRetry={() => window.location.reload()} />}
      {loading && <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>}

      {!loading && !error && (
        <>
          {items.length === 0 ? <EmptyState title="No reasoning sessions found" description="Try adjusting your filters or search terms." />
            : <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 dark:bg-slate-700/50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Session</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Status</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Domain</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Confidence</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Risk Score</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Time</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Triggered By</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Date</th>
                      <th className="w-10 px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                    {items.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                        <td className="px-4 py-3 max-w-[200px]">
                          <Link to={`/reasoning/${item.id}`} className="font-medium text-slate-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">
                            {item.query.length > 50 ? `${item.query.slice(0, 50)}...` : item.query}
                          </Link>
                          <div className="text-xs text-slate-400 mt-0.5">{item.id}</div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded ${STATUS_CONFIG[item.status]?.class || ''}`}>{STATUS_CONFIG[item.status]?.label || item.status}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: DOMAIN_COLORS[item.domain] || '#94a3b8' }} />
                            <span className="text-slate-600 dark:text-slate-400 capitalize">{item.domain}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {item.status === 'failed' ? <span className="text-xs text-slate-400">N/A</span>
                            : <div className="flex items-center gap-2">
                                <div className="w-16 h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                                  <div className="h-full rounded-full transition-all" style={{ width: `${item.confidence * 100}%`, backgroundColor: item.confidence > 0.8 ? '#22c55e' : item.confidence > 0.6 ? '#f59e0b' : '#ef4444' }} />
                                </div>
                                <span className="text-xs text-slate-500">{(item.confidence * 100).toFixed(0)}%</span>
                              </div>}
                        </td>
                        <td className="px-4 py-3">
                          {item.status === 'failed' ? <span className="text-xs text-slate-400">N/A</span>
                            : <div className="flex items-center gap-2">
                                <div className="w-16 h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                                  <div className="h-full rounded-full transition-all" style={{ width: `${item.riskScore * 100}%`, backgroundColor: item.riskScore > 0.7 ? '#ef4444' : item.riskScore > 0.4 ? '#f59e0b' : '#22c55e' }} />
                                </div>
                                <span className="text-xs text-slate-500">{(item.riskScore * 100).toFixed(0)}%</span>
                              </div>}
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400">{formatTime(item.processingTimeMs)}</td>
                        <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400 max-w-[120px] truncate">{item.triggeredBy}</td>
                        <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400">{new Date(item.createdAt).toLocaleDateString()}</td>
                        <td className="px-4 py-3">
                          <Link to={`/reasoning/${item.id}`} className="text-blue-600 dark:text-blue-400 hover:text-blue-800">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>}
          {total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-4">
              <button disabled={page <= 1} onClick={() => updateParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Previous</button>
              <span className="text-sm text-slate-500 dark:text-slate-400">Page {page} of {Math.ceil(total / 12)}</span>
              <button disabled={page >= Math.ceil(total / 12)} onClick={() => updateParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
