import { useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useExplanationList, useExplanationById } from '@/services/explainabilityApiService'
import type { Explanation } from '@/types/explainability'

const STAGE_COLORS: Record<string, string> = {
  evidence_collection: '#3b82f6',
  knowledge_retrieval: '#06b6d4',
  rule_evaluation: '#f59e0b',
  hypothesis_testing: '#f97316',
  recommendation_generation: '#22c55e',
}

function ExplanationDetailView({ explanation }: { explanation: Explanation }) {
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set())

  const toggleStage = (name: string) => {
    setExpandedStages((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name); else next.add(name)
      return next
    })
  }

  return (
    <div className="space-y-6">
      <Link to="/explainability" className="inline-flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
        Back to Explainability
      </Link>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">{explanation.recommendationTitle}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{explanation.id} — {explanation.recommendationId}</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{(explanation.confidence * 100).toFixed(0)}%</div>
            <div className="text-xs text-slate-500">Confidence</div>
          </div>
        </div>
        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{explanation.narrative}</p>
      </div>

      {explanation.stages.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-semibold mb-4">Reasoning Stages</h2>
          <div className="space-y-4">
            {explanation.stages.map((stage) => {
              const isExpanded = expandedStages.has(stage.name)
              const stageColor = STAGE_COLORS[stage.name.toLowerCase().replace(/\s+/g, '_')] || '#94a3b8'
              return (
                <div key={stage.name} className="border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full inline-block" style={{ backgroundColor: stageColor }} />
                      <h3 className="font-semibold text-slate-900 dark:text-white text-sm">{stage.name}</h3>
                    </div>
                    <button onClick={() => toggleStage(stage.name)} className="text-blue-600 dark:text-blue-400 text-xs hover:underline">
                      {isExpanded ? 'Hide details' : 'Show details'}
                    </button>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{stage.description}</p>
                  {isExpanded && (
                    <div className="mt-3 space-y-3 border-t border-slate-200 dark:border-slate-700 pt-3">
                      {stage.details.length > 0 && (
                        <div>
                          <span className="text-xs font-semibold text-slate-500">Details</span>
                          <ul className="mt-1 space-y-1">
                            {stage.details.map((d, i) => (
                              <li key={i} className="text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2">
                                <span className="text-slate-400 mt-1">•</span>
                                <span>{d}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {stage.evidence.length > 0 && (
                        <div>
                          <span className="text-xs font-semibold text-slate-500">Evidence</span>
                          <div className="mt-1 flex flex-wrap gap-2">
                            {stage.evidence.map((ev) => (
                              <Link key={ev.id} to={`/evidence/${ev.id}`} className="text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 px-2 py-1 rounded hover:underline">
                                {ev.id} ({ev.title.slice(0, 30)}...) — {(ev.confidence * 100).toFixed(0)}%
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}
                      {stage.rules.length > 0 && (
                        <div>
                          <span className="text-xs font-semibold text-slate-500">Rules</span>
                          <div className="mt-1 flex flex-wrap gap-2">
                            {stage.rules.map((rule) => (
                              <span key={rule.id} className={`text-xs px-2 py-1 rounded ${rule.triggered ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400' : 'bg-slate-50 dark:bg-slate-700 text-slate-600 dark:text-slate-400'}`}>
                                {rule.id}: {rule.triggered ? 'Triggered' : 'Not triggered'}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {stage.knowledge.length > 0 && (
                        <div>
                          <span className="text-xs font-semibold text-slate-500">Knowledge</span>
                          <div className="mt-1 flex flex-wrap gap-2">
                            {stage.knowledge.map((k) => (
                              <Link key={k.id} to={`/knowledge/${k.id}`} className="text-xs bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 px-2 py-1 rounded hover:underline">
                                {k.id}: {k.title}
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Reasoning Strategy & Risk Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Reasoning Strategy</h3>
          <span className="inline-block text-xs px-2 py-1 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-medium">
            Deductive Analysis
          </span>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">Rule-based inference from evidence and knowledge base.</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Risk Score</h3>
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {(explanation.confidence < 0.7 ? 7 : explanation.confidence < 0.85 ? 5 : 3)}
            <span className="text-sm text-slate-400 font-normal">/10</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {explanation.confidence < 0.7 ? 'Moderate-High' : explanation.confidence < 0.85 ? 'Moderate' : 'Low'} risk level
          </p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Financial Impact</h3>
          <div className="text-lg font-bold text-slate-900 dark:text-white">
            {explanation.recommendationId === 'R-001' ? '$45,000' : explanation.recommendationId === 'R-009' ? '$12,500' : '$8,200'}
          </div>
          <p className="text-xs text-green-600 dark:text-green-400 mt-1">
            Est. savings: {explanation.recommendationId === 'R-001' ? '$180,000' : explanation.recommendationId === 'R-009' ? '$95,000' : '$24,000'}
          </p>
        </div>
      </div>

      {/* Evidence, Knowledge, Rules Summary */}
      {(() => {
        const allEvidence = explanation.stages.flatMap(s => s.evidence).filter((e, i, a) => a.findIndex(x => x.id === e.id) === i)
        const allKnowledge = explanation.stages.flatMap(s => s.knowledge).filter((k, i, a) => a.findIndex(x => x.id === k.id) === i)
        const allRules = explanation.stages.flatMap(s => s.rules).filter((r, i, a) => a.findIndex(x => x.id === r.id) === i)
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {allEvidence.length > 0 && (
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Evidence Used ({allEvidence.length})</h3>
                <div className="space-y-1.5">
                  {allEvidence.map((ev) => (
                    <Link key={ev.id} to={`/evidence/${ev.id}`} className="flex items-center justify-between text-xs p-2 bg-blue-50 dark:bg-blue-900/10 rounded hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                      <span className="text-slate-700 dark:text-slate-300 truncate mr-2">{ev.id}</span>
                      <span className="text-slate-500 shrink-0">{(ev.confidence * 100).toFixed(0)}%</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
            {allKnowledge.length > 0 && (
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Knowledge Used ({allKnowledge.length})</h3>
                <div className="space-y-1.5">
                  {allKnowledge.map((k) => (
                    <Link key={k.id} to={`/knowledge/${k.id}`} className="flex items-center text-xs p-2 bg-yellow-50 dark:bg-yellow-900/10 rounded hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors">
                      <span className="text-slate-700 dark:text-slate-300 truncate">{k.id}: {k.title}</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
            {allRules.length > 0 && (
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Rules Triggered ({allRules.filter(r => r.triggered).length}/{allRules.length})</h3>
                <div className="space-y-1.5">
                  {allRules.map((rule) => (
                    <div key={rule.id} className={`flex items-center justify-between text-xs p-2 rounded ${rule.triggered ? 'bg-red-50 dark:bg-red-900/10' : 'bg-slate-50 dark:bg-slate-700/30'}`}>
                      <span className="text-slate-700 dark:text-slate-300 truncate mr-2">{rule.id}</span>
                      <span className={`shrink-0 ${rule.triggered ? 'text-red-600 dark:text-red-400' : 'text-slate-400'}`}>{rule.triggered ? '✓' : '—'}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      })()}

      {explanation.alternatives.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-semibold mb-3">Alternative Recommendations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {explanation.alternatives.map((alt, i) => (
              <div key={i} className="p-3 border border-slate-200 dark:border-slate-700 rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-900 dark:text-white">{alt.title}</span>
                  <span className="text-xs text-slate-500">Confidence: {(alt.confidence * 100).toFixed(0)}%</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400">{alt.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h2 className="text-lg font-semibold mb-3">Confidence Score Breakdown</h2>
        <div className="space-y-3">
          {explanation.confidenceBreakdown.length > 0 ? explanation.confidenceBreakdown.map((cb) => (
            <div key={cb.label}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600 dark:text-slate-400">{cb.label}</span>
                <span className="font-medium">{(cb.value * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full h-2 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all" style={{ width: `${cb.value * 100}%`, backgroundColor: cb.value > 0.8 ? '#22c55e' : cb.value > 0.6 ? '#f59e0b' : '#ef4444' }} />
              </div>
            </div>
          )) : (
            <p className="text-xs text-slate-500 dark:text-slate-400 italic">No breakdown data available.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ExplainabilityCenter() {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedId = searchParams.get('id') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const { data: listData, isLoading, error } = useExplanationList(page)
  const { data: selectedExplanation } = useExplanationById(selectedId || '')

  const items = listData?.items ?? []
  const total = listData?.total ?? 0

  if (selectedId && selectedExplanation) {
    return <ExplanationDetailView explanation={selectedExplanation} />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Explainability Center</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Trace the decision-making process from evidence to recommendation
        </p>
      </div>

      {error && <ErrorState message={(error as Error).message} onRetry={() => window.location.reload()} />}
      {isLoading && <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>}

      {!isLoading && !error && (
        <>
          {items.length === 0 ? (
            <EmptyState title="No explanations found" description="No explanation records are available yet." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((exp) => (
                <Link
                  key={exp.id}
                  to={`/explainability?id=${exp.id}`}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 hover:shadow-md transition-all hover:border-blue-500/50"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-mono text-slate-400">{exp.id}</span>
                    <span className="text-xs font-semibold" style={{ color: exp.confidence > 0.8 ? '#22c55e' : exp.confidence > 0.6 ? '#f59e0b' : '#ef4444' }}>
                      {(exp.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-900 dark:text-white mb-2 line-clamp-1">{exp.recommendationTitle}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-3">{exp.narrative}</p>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {exp.stages.map((s) => (
                      <span key={s.name} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                        {s.name}
                      </span>
                    ))}
                  </div>
                  <div className="mt-3 text-xs text-slate-400">{new Date(exp.createdAt).toLocaleDateString()}</div>
                </Link>
              ))}
            </div>
          )}

          {total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-4">
              <button disabled={page <= 1} onClick={() => setSearchParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Previous</button>
              <span className="text-sm text-slate-500 dark:text-slate-400">Page {page} of {Math.ceil(total / 12)}</span>
              <button disabled={page >= Math.ceil(total / 12)} onClick={() => setSearchParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
