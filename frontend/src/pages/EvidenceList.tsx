import { Link, useSearchParams } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useEvidence } from '@/services/evidenceApiService'
import type { EvidenceType, EvidenceStatus, EvidencePriority } from '@/types/evidence'

const TYPE_COLORS: Record<string, string> = { sensor: '#3b82f6', incident: '#ef4444', maintenance: '#f59e0b', compliance: '#22c55e', customer: '#8b5cf6', alarm: '#dc2626', knowledge: '#06b6d4', recommendation: '#f97316', email: '#6366f1', report: '#14b8a6' }
const STATUS_COLORS: Record<string, string> = { collected: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300', verified: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400', analyzed: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400', fused: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400', rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' }
const PRIORITY_VALUES: EvidencePriority[] = ['critical', 'high', 'medium', 'low']
const isEvidenceType = (value: string): value is EvidenceType => value in TYPE_COLORS
const isEvidenceStatus = (value: string): value is EvidenceStatus => value in STATUS_COLORS
const isEvidencePriority = (value: string): value is EvidencePriority => PRIORITY_VALUES.includes(value as EvidencePriority)

const EVIDENCE_TYPES = [
  { value: '', label: 'All Types' }, { value: 'sensor', label: 'Sensor' }, { value: 'incident', label: 'Incident' },
  { value: 'maintenance', label: 'Maintenance' }, { value: 'compliance', label: 'Compliance' },
  { value: 'customer', label: 'Customer' }, { value: 'alarm', label: 'Alarm' },
  { value: 'knowledge', label: 'Knowledge' }, { value: 'recommendation', label: 'Recommendation' },
  { value: 'report', label: 'Report' },
]

export default function EvidenceList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const type = searchParams.get('type') || ''
  const statusFilter = searchParams.get('status') || ''
  const priority = searchParams.get('priority') || ''
  const search = searchParams.get('search') || ''
  const page = parseInt(searchParams.get('page') || '1')
  const sortBy = searchParams.get('sort') || 'confidence'

  const evidenceQuery = useEvidence({
    type: isEvidenceType(type) ? type : undefined,
    status: isEvidenceStatus(statusFilter) ? statusFilter : undefined,
    priority: isEvidencePriority(priority) ? priority : undefined,
    search: search || undefined,
    page,
    limit: 12,
    sort: sortBy as 'confidence' | 'date' | 'priority',
  })

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => { if (v) next.set(k, v); else next.delete(k) })
    if (updates.type !== undefined || updates.status !== undefined || updates.priority !== undefined || updates.search !== undefined || updates.sort !== undefined) next.delete('page')
    setSearchParams(next)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Evidence Center</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Browse, search, and trace evidence across the ADIP platform</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <input type="text" placeholder="Search evidence..." value={search} onChange={(e) => updateParams({ search: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm min-w-[280px] focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <select value={type} onChange={(e) => updateParams({ type: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          {EVIDENCE_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <select value={statusFilter} onChange={(e) => updateParams({ status: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Status</option>
          <option value="collected">Collected</option>
          <option value="verified">Verified</option>
          <option value="analyzed">Analyzed</option>
          <option value="fused">Fused</option>
          <option value="rejected">Rejected</option>
        </select>
        <select value={priority} onChange={(e) => updateParams({ priority: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Priority</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select value={sortBy} onChange={(e) => updateParams({ sort: e.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="confidence">Sort by Confidence</option>
          <option value="date">Sort by Date</option>
          <option value="priority">Sort by Priority</option>
        </select>
      </div>

      {evidenceQuery.error && <ErrorState message={evidenceQuery.error.message} onRetry={() => evidenceQuery.refetch()} />}
      {evidenceQuery.isLoading && <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>}

      {!evidenceQuery.isLoading && !evidenceQuery.error && (
        <>
          {evidenceQuery.data?.items?.length === 0 ? <EmptyState title="No evidence found" description="Try adjusting your filters or search terms." />
            : <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 dark:bg-slate-700/50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Title</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Type</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Status</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Priority</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Confidence</th>
                      <th className="text-left px-4 py-3 font-medium text-slate-500 dark:text-slate-400">Date</th>
                      <th className="w-10 px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                    {evidenceQuery.data?.items?.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                        <td className="px-4 py-3">
                          <Link to={`/evidence/${item.id}`} className="font-medium text-slate-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">{item.title}</Link>
                          <div className="text-xs text-slate-400 mt-0.5">{item.source}</div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: TYPE_COLORS[item.type] || '#94a3b8' }} />
                            <span className="text-slate-600 dark:text-slate-400 capitalize">{item.type}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[item.status] || ''}`}>{item.status}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs font-medium ${item.priority === 'critical' ? 'text-red-600' : item.priority === 'high' ? 'text-orange-600' : item.priority === 'medium' ? 'text-yellow-600' : 'text-slate-500'}`}>{item.priority}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                              <div className="h-full rounded-full transition-all" style={{ width: `${item.confidence * 100}%`, backgroundColor: item.confidence > 0.8 ? '#22c55e' : item.confidence > 0.6 ? '#f59e0b' : '#ef4444' }} />
                            </div>
                            <span className="text-xs text-slate-500">{(item.confidence * 100).toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500 dark:text-slate-400">{new Date(item.timestamp).toLocaleDateString()}</td>
                        <td className="px-4 py-3">
                          <Link to={`/evidence/${item.id}`} className="text-blue-600 dark:text-blue-400 hover:text-blue-800">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>}
          {evidenceQuery.data?.total && evidenceQuery.data.total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-4">
              <button disabled={page <= 1} onClick={() => updateParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Previous</button>
              <span className="text-sm text-slate-500 dark:text-slate-400">Page {page} of {Math.ceil(evidenceQuery.data.total / 12)}</span>
              <button disabled={page >= Math.ceil(evidenceQuery.data.total / 12)} onClick={() => updateParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
