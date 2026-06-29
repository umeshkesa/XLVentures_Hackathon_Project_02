import { useParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useEvidenceById, useEvidenceTraceability } from '@/services/evidenceApiService'

const TYPE_COLORS: Record<string, string> = { sensor: '#3b82f6', incident: '#ef4444', maintenance: '#f59e0b', compliance: '#22c55e', customer: '#8b5cf6', alarm: '#dc2626', knowledge: '#06b6d4', recommendation: '#f97316', email: '#6366f1', report: '#14b8a6' }
const STATUS_COLORS: Record<string, string> = { collected: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300', verified: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400', analyzed: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400', fused: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400', rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' }

const STAGE_CONFIG: Record<string, { color: string; label: string }> = {
  source: { color: '#3b82f6', label: 'Source' },
  evidence: { color: '#8b5cf6', label: 'Evidence Collection' },
  knowledge: { color: '#06b6d4', label: 'Knowledge Integration' },
  rules: { color: '#f59e0b', label: 'Rule Evaluation' },
  reasoning: { color: '#f97316', label: 'Reasoning' },
  recommendation: { color: '#22c55e', label: 'Recommendation' },
}

export default function EvidenceDetail() {
  const { id } = useParams()
  const evidenceQuery = useEvidenceById(id || '')
  const traceQuery = useEvidenceTraceability(id || '')

  if (evidenceQuery.isLoading) return <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
  if (evidenceQuery.error) return <ErrorState message={evidenceQuery.error.message} onRetry={() => evidenceQuery.refetch()} />
  if (!evidenceQuery.data) return <EmptyState title="Evidence not found" description="The requested evidence item could not be found." />

  const { data: evidence } = evidenceQuery

  const qualityMetrics = [
    { label: 'Quality Score', value: evidence.qualityScore, color: evidence.qualityScore > 0.8 ? '#22c55e' : evidence.qualityScore > 0.6 ? '#f59e0b' : '#ef4444' },
    { label: 'Freshness', value: evidence.freshness, color: evidence.freshness > 0.8 ? '#22c55e' : evidence.freshness > 0.6 ? '#f59e0b' : '#ef4444' },
    { label: 'Completeness', value: evidence.completeness, color: evidence.completeness > 0.8 ? '#22c55e' : evidence.completeness > 0.6 ? '#f59e0b' : '#ef4444' },
    { label: 'Consistency', value: evidence.consistency, color: evidence.consistency > 0.8 ? '#22c55e' : evidence.consistency > 0.6 ? '#f59e0b' : '#ef4444' },
    { label: 'Reliability', value: evidence.reliability, color: evidence.reliability > 0.8 ? '#22c55e' : evidence.reliability > 0.6 ? '#f59e0b' : '#ef4444' },
  ]

  return (
    <div className="max-w-6xl space-y-6">
      <Link to="/evidence" className="inline-flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
        Back to Evidence Center
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: TYPE_COLORS[evidence.type] || '#94a3b8' }} />
              <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: TYPE_COLORS[evidence.type] || '#94a3b8' }}>{evidence.type}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[evidence.status] || ''}`}>{evidence.status}</span>
              <span className="text-xs text-slate-400 ml-auto">{new Date(evidence.timestamp).toLocaleString()}</span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{evidence.title}</h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">{evidence.description}</p>
            <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
              <span>Source: {evidence.source}</span>
              <span>Type: {evidence.sourceType}</span>
              <span>Domain: {evidence.domain}</span>
            </div>
            {evidence.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-4">
                {evidence.tags.map((t) => <span key={t} className="text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded">{t}</span>)}
              </div>
            )}
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4">Traceability Chain</h2>
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-600" />
              <div className="space-y-6">
                {traceQuery.data?.steps.map((step, index) => {
                  const stageCfg = STAGE_CONFIG[step.stage] || { color: '#94a3b8', label: step.stage }
                  return (
                    <div key={index} className="relative pl-10">
                      <div className="absolute left-2.5 top-1.5 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900" style={{ backgroundColor: step.status === 'completed' ? stageCfg.color : '#94a3b8' }} />
                      <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-semibold" style={{ color: stageCfg.color }}>{stageCfg.label}</span>
                          <span className="text-xs px-1.5 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Completed</span>
                        </div>
                        <h4 className="font-medium text-sm text-slate-900 dark:text-white">{step.label}</h4>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{step.description}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 className="font-semibold mb-4 text-sm">Quality Metrics</h3>
            <div className="space-y-4">
              <div className="flex justify-center mb-4">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="15.5" fill="none" stroke="currentColor" strokeWidth="3" className="text-slate-200 dark:text-slate-600" />
                    <circle cx="18" cy="18" r="15.5" fill="none" stroke="#22c55e" strokeWidth="3" strokeDasharray={`${Math.PI * 31 * evidence.confidence} ${Math.PI * 31 * (1 - evidence.confidence)}`} strokeLinecap="round" />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xl font-bold text-slate-900 dark:text-white">{(evidence.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
              <p className="text-center text-xs text-slate-500 -mt-2 mb-3">Confidence Score</p>
              {qualityMetrics.map((m) => (
                <div key={m.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-500">{m.label}</span>
                    <span className="font-medium">{(m.value * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all" style={{ width: `${m.value * 100}%`, backgroundColor: m.color }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {evidence.relatedAssets.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Assets</h3>
              <div className="space-y-1.5">
                {evidence.relatedAssets.map((a) => (
                  <Link key={a} to={`/assets/${a}`} className="block text-sm text-blue-600 dark:text-blue-400 hover:underline">{a}</Link>
                ))}
              </div>
            </div>
          )}

          {evidence.relatedCustomers.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Customers</h3>
              <div className="space-y-1.5">
                {evidence.relatedCustomers.map((c) => (
                  <Link key={c} to={`/customers/${c}`} className="block text-sm text-blue-600 dark:text-blue-400 hover:underline">{c}</Link>
                ))}
              </div>
            </div>
          )}

          {evidence.relatedKnowledge.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Knowledge</h3>
              <div className="space-y-1.5">
                {evidence.relatedKnowledge.map((k) => (
                  <Link key={k} to={`/knowledge/${k}`} className="block text-sm text-blue-600 dark:text-blue-400 hover:underline">{k}</Link>
                ))}
              </div>
            </div>
          )}

          {evidence.relatedRecommendations.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Recommendations</h3>
              <div className="space-y-1.5">
                {evidence.relatedRecommendations.map((r) => (
                  <div key={r} className="text-sm text-blue-600 dark:text-blue-400">{r}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
