import { useSearchParams } from 'react-router-dom'
import { useEvidence } from '@/services/evidenceApiService'
import type { EvidenceType } from '@/types/evidence'

const TYPE_COLORS: Record<string, string> = { sensor: '#3b82f6', incident: '#ef4444', maintenance: '#f59e0b', compliance: '#22c55e', customer: '#8b5cf6', alarm: '#dc2626', knowledge: '#06b6d4', recommendation: '#f97316', email: '#6366f1', report: '#14b8a6' }

const TYPE_LABELS: Record<string, string> = { sensor: 'Sensor Data', incident: 'Incident Report', maintenance: 'Maintenance Report', compliance: 'Compliance Report', customer: 'Customer Report', alarm: 'Alarm Alert', knowledge: 'Knowledge Document', recommendation: 'Recommendation', email: 'Email Message', report: 'Summary Report' }

const EVIDENCE_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'sensor', label: 'Sensor Data' },
  { value: 'incident', label: 'Incident Report' },
  { value: 'maintenance', label: 'Maintenance Report' },
  { value: 'compliance', label: 'Compliance Report' },
  { value: 'customer', label: 'Customer Report' },
  { value: 'alarm', label: 'Alarm Alert' },
  { value: 'knowledge', label: 'Knowledge Document' },
  { value: 'recommendation', label: 'Recommendation' },
]

const STAGE_CONFIG: Record<string, { color: string; label: string }> = {
  source: { color: '#3b82f6', label: 'Source' },
  evidence: { color: '#8b5cf6', label: 'Evidence Collection' },
  knowledge: { color: '#06b6d4', label: 'Knowledge Integration' },
  rules: { color: '#f59e0b', label: 'Rule Evaluation' },
  reasoning: { color: '#f97316', label: 'Reasoning' },
  recommendation: { color: '#22c55e', label: 'Recommendation' },
}

export default function TraceabilityView() {
  const [searchParams, setSearchParams] = useSearchParams()
  const type = searchParams.get('type') || ''

  const evidenceQuery = useEvidence({
    type: type as EvidenceType | undefined,
    status: undefined,
    priority: undefined,
    search: undefined,
    page: 1,
    limit: 20,
    sort: 'date',
  })

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => { if (v) next.set(k, v); else next.delete(k) })
    setSearchParams(next)
  }

  const getTraceabilityFlow = (evidence: any) => {
    const flow = [
      { stage: 'source', label: evidence.source, description: `Source: ${evidence.sourceType}`, status: 'completed' as const },
      { stage: 'evidence', label: evidence.title, description: evidence.description, status: 'completed' as const },
    ]

    if (evidence.relatedKnowledge.length > 0) {
      flow.push({ stage: 'knowledge', label: `${evidence.relatedKnowledge.length} Knowledge Docs`, description: 'Related knowledge documents for context', status: 'completed' as const })
    }

    if (evidence.relatedRules.length > 0) {
      flow.push({ stage: 'rules', label: `${evidence.relatedRules.length} Rules Applied`, description: 'Relevant rules and policies evaluated', status: 'completed' as const })
    }

    flow.push({ stage: 'reasoning', label: 'Reasoning Complete', description: 'Multi-strategy reasoning executed', status: 'completed' as const })

    if (evidence.relatedRecommendations.length > 0) {
      flow.push({ stage: 'recommendation', label: `${evidence.relatedRecommendations.length} Recommendations`, description: 'Evidence-based recommendations generated', status: 'completed' as const })
    }

    return flow
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Evidence Traceability</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Visualize how evidence evolves through the ADIP platform</p>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h2 className="text-lg font-semibold mb-4">Evidence Flow Visualization</h2>
        <div className="flex flex-wrap gap-2 mb-6">
          {EVIDENCE_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => updateParams({ type: t.value })}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${type === t.value ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200'}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {evidenceQuery.isLoading ? (
          <div className="flex justify-center py-12">
            <div className="text-center text-slate-500 dark:text-slate-400">
              <div className="w-12 h-12 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
              Loading evidence...
            </div>
          </div>
        ) : evidenceQuery.data?.items.length === 0 ? (
          <div className="text-center py-12 text-slate-500 dark:text-slate-400">
            <p>No evidence found for this type.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {evidenceQuery.data?.items.map((evidence) => (
              <div key={evidence.id} className="bg-slate-50 dark:bg-slate-700/50 rounded-xl border border-slate-200 dark:border-slate-600 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: TYPE_COLORS[evidence.type] || '#94a3b8' }} />
                      <span className="text-sm font-semibold" style={{ color: TYPE_COLORS[evidence.type] || '#94a3b8' }}>
                        {TYPE_LABELS[evidence.type] || evidence.type}
                      </span>
                      <span className="text-xs text-slate-500 ml-auto">{new Date(evidence.timestamp).toLocaleDateString()}</span>
                    </div>
                    <h3 className="text-lg font-medium text-slate-900 dark:text-white">{evidence.title}</h3>
                  </div>
                </div>

                <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">{evidence.description}</p>

                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Traceability Flow</h4>
                  <div className="relative pl-6">
                    <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-slate-300 dark:bg-slate-500" />
                    <div className="space-y-3">
                      {getTraceabilityFlow(evidence).map((step, index) => (
                        <div key={index} className="relative">
                          <div className="absolute left-[-19px] top-0 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900" style={{ backgroundColor: STAGE_CONFIG[step.stage]?.color || '#94a3b8' }} />
                          <div className="bg-white dark:bg-slate-700 rounded-lg p-3 border border-slate-200 dark:border-slate-600">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-semibold" style={{ color: STAGE_CONFIG[step.stage]?.color || '#94a3b8' }}>{STAGE_CONFIG[step.stage]?.label || step.stage}</span>
                              <span className="text-xs px-1.5 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Completed</span>
                            </div>
                            <p className="text-sm text-slate-700 dark:text-slate-300">{step.label}</p>
                            <p className="text-xs text-slate-500 mt-1">{step.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
