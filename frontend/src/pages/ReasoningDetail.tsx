import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useReasoningById } from '@/services/reasoningApiService'

const STATUS_STYLES: Record<string, string> = {
  in_progress: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
}

const DOMAIN_COLORS: Record<string, string> = {
  energy: '#f97316',
  maintenance: '#8b5cf6',
  safety: '#dc2626',
  compliance: '#22c55e',
  operations: '#3b82f6',
  customer: '#6366f1',
  general: '#94a3b8',
}

const STEP_TYPE_COLORS: Record<string, string> = {
  evidence_analysis: '#3b82f6',
  knowledge_retrieval: '#06b6d4',
  rule_evaluation: '#f59e0b',
  hypothesis_generation: '#f97316',
  conclusion: '#22c55e',
}

function ConfidenceRing({ value, size = 80, strokeWidth = 6 }: { value: number; size?: number; strokeWidth?: number }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - value)
  const color = value > 0.8 ? '#22c55e' : value > 0.6 ? '#f59e0b' : '#ef4444'
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="-rotate-90" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="currentColor" strokeWidth={strokeWidth} className="text-slate-200 dark:text-slate-600" />
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={strokeWidth} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" />
      </svg>
      <span className="absolute text-lg font-bold text-slate-900 dark:text-white">{(value * 100).toFixed(0)}%</span>
    </div>
  )
}

export default function ReasoningDetail() {
  const { id } = useParams()
  const { data: session, isLoading: loading, error: queryError } = useReasoningById(id ?? '')
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set())
  const error = queryError ? (queryError as Error).message : (id && !loading && !session ? 'Reasoning not found' : null)

  const toggleStep = (stepId: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev)
      if (next.has(stepId)) next.delete(stepId); else next.add(stepId)
      return next
    })
  }

  if (loading) return <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!session) return <EmptyState title="Reasoning not found" description="The requested reasoning session could not be found." />

  const isCompleted = session.status === 'completed'
  const isInProgress = session.status === 'in_progress'
  const domainColor = DOMAIN_COLORS[session.domain] || '#94a3b8'

  return (
    <div className="max-w-5xl space-y-6">
      <Link to="/reasoning" className="inline-flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
        Back to Reasoning
      </Link>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-0.5 rounded ${STATUS_STYLES[session.status] || ''}`}>{session.status.replace('_', ' ')}</span>
          <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: domainColor }}>{session.domain}</span>
        </div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">{session.query}</h1>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-500 dark:text-slate-400">
          <div><span className="block text-slate-400">ID</span><span className="font-medium text-slate-700 dark:text-slate-300">{session.id}</span></div>
          <div><span className="block text-slate-400">Triggered By</span><span className="font-medium text-slate-700 dark:text-slate-300">{session.triggeredBy}</span></div>
          <div><span className="block text-slate-400">Strategy</span><span className="font-medium text-slate-700 dark:text-slate-300">{session.strategy}</span></div>
          <div><span className="block text-slate-400">Started</span><span className="font-medium text-slate-700 dark:text-slate-300">{new Date(session.createdAt).toLocaleString()}</span></div>
          {session.completedAt && (
            <div><span className="block text-slate-400">Completed</span><span className="font-medium text-slate-700 dark:text-slate-300">{new Date(session.completedAt).toLocaleString()}</span></div>
          )}
        </div>
        {session.conclusion && (
          <div className="pt-2 border-t border-slate-200 dark:border-slate-700">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Conclusion</h3>
            <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{session.conclusion}</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-center">
          <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">Confidence</h3>
          {isCompleted ? (
            <ConfidenceRing value={session.confidence} />
          ) : (
            <span className="text-sm text-slate-400">N/A</span>
          )}
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-center">
          <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">Risk Score</h3>
          {isCompleted ? (
            <div className="flex flex-col items-center">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">{(session.riskScore * 100).toFixed(0)}%</span>
              <div className="w-full max-w-[80px] h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full mt-1 overflow-hidden">
                <div className="h-full rounded-full transition-all" style={{ width: `${session.riskScore * 100}%`, backgroundColor: session.riskScore > 0.7 ? '#ef4444' : session.riskScore > 0.4 ? '#f59e0b' : '#22c55e' }} />
              </div>
            </div>
          ) : (
            <span className="text-sm text-slate-400">N/A</span>
          )}
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-center">
          <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">Processing Time</h3>
          {isInProgress ? (
            <span className="text-sm text-slate-400">In progress...</span>
          ) : (
            <div className="flex flex-col items-center">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">{(session.processingTimeMs / 1000).toFixed(1)}s</span>
              <span className="text-xs text-slate-400">{session.processingTimeMs.toLocaleString()} ms</span>
            </div>
          )}
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 text-center">
          <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">References</h3>
          <div className="flex justify-center gap-4 text-sm">
            <div><span className="block text-2xl font-bold text-slate-900 dark:text-white">{session.evidenceCount}</span><span className="text-xs text-slate-400">Evidence</span></div>
            <div><span className="block text-2xl font-bold text-slate-900 dark:text-white">{session.ruleCount}</span><span className="text-xs text-slate-400">Rules</span></div>
            <div><span className="block text-2xl font-bold text-slate-900 dark:text-white">{session.knowledgeCount}</span><span className="text-xs text-slate-400">Knowledge</span></div>
          </div>
        </div>
      </div>

      {session.steps.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-semibold mb-4">Reasoning Steps</h2>
          <div className="relative">
            <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-slate-200 dark:bg-slate-600" />
            <div className="space-y-4">
              {session.steps.map((step, index) => {
                const isExpanded = expandedSteps.has(step.id)
                const stepColor = STEP_TYPE_COLORS[step.type] || '#94a3b8'
                return (
                  <div key={step.id} className="relative pl-10">
                    <div className="absolute left-2.5 top-2 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900" style={{ backgroundColor: stepColor }} />
                    <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold" style={{ color: stepColor }}>{step.type.replace(/_/g, ' ')}</span>
                          <span className="text-xs text-slate-400">Step {index + 1}</span>
                        </div>
                        <span className="text-xs text-slate-400">{(step.durationMs / 1000).toFixed(2)}s</span>
                      </div>
                      <p className="text-sm text-slate-700 dark:text-slate-300">{step.description}</p>
                      <button
                        onClick={() => toggleStep(step.id)}
                        className="mt-2 inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        <svg className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                        {isExpanded ? 'Hide details' : 'Show details'}
                      </button>
                      {isExpanded && (
                        <div className="mt-3 space-y-2 border-t border-slate-200 dark:border-slate-700 pt-3">
                          <div>
                            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Input</span>
                            <p className="text-xs text-slate-700 dark:text-slate-300 mt-0.5 whitespace-pre-wrap bg-slate-50 dark:bg-slate-900/50 rounded p-2">{step.input}</p>
                          </div>
                          <div>
                            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Output</span>
                            <p className="text-xs text-slate-700 dark:text-slate-300 mt-0.5 whitespace-pre-wrap bg-slate-50 dark:bg-slate-900/50 rounded p-2">{step.output}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {session.steps.length === 0 && (
        <EmptyState title="No reasoning steps" description="No steps were recorded for this reasoning session." />
      )}

      {session.relatedRecommendations.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-semibold mb-3">Related Recommendations</h2>
          <div className="space-y-2">
            {session.relatedRecommendations.map((r) => (
              <Link key={r} to={`/recommendations/${r}`} className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                {r}
              </Link>
            ))}
          </div>
        </div>
      )}

      {session.relatedRecommendations.length === 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-semibold mb-1">Related Recommendations</h2>
          <p className="text-sm text-slate-400">No related recommendations for this reasoning session.</p>
        </div>
      )}
    </div>
  )
}

