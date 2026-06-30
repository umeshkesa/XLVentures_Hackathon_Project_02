import { useParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useInteractionById } from '@/services/interactionApiService'
import { ClipboardList } from 'lucide-react'

const TYPE_LABELS: Record<string, string> = { email: 'Email', meeting: 'Meeting', crm_update: 'CRM Update', call_transcript: 'Call Transcript', chat: 'Chat', complaint: 'Complaint', feedback: 'Feedback', service_request: 'Service Request' }
const TYPE_COLORS: Record<string, string> = { email: '#3b82f6', meeting: '#8b5cf6', crm_update: '#06b6d4', call_transcript: '#10b981', chat: '#f59e0b', complaint: '#ef4444', feedback: '#22c55e', service_request: '#f97316' }
const STATUS_BADGES: Record<string, string> = { resolved: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400', escalated: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }

export default function InteractionDetail() {
  const { id } = useParams()
  const interactionQuery = useInteractionById(id || '')

  if (interactionQuery.isLoading) return <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
  if (interactionQuery.error) return <ErrorState message={interactionQuery.error.message} onRetry={() => interactionQuery.refetch()} />
  if (!interactionQuery.data) return <EmptyState title="Interaction not found" description="The requested interaction could not be found." />

  const { data: interaction } = interactionQuery

  return (
    <div className="max-w-4xl space-y-6">
      <Link to="/interactions" className="inline-flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
        Back to Interactions
      </Link>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: TYPE_COLORS[interaction.type] || '#94a3b8' }}>{TYPE_LABELS[interaction.type] || interaction.type}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${STATUS_BADGES[interaction.status] || ''}`}>{interaction.status}</span>
          <span className="text-xs text-slate-400 ml-auto">{new Date(interaction.date).toLocaleString()}</span>
        </div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{interaction.subject}</h1>
        <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400 mb-6">
          <Link to={`/customers/${interaction.customerId}`} className="hover:text-blue-500">{interaction.customerName}</Link>
          <span>Agent: {interaction.agent}</span>
          <span>ID: {interaction.id}</span>
        </div>
        <div className="prose prose-slate dark:prose-invert max-w-none text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{interaction.content}</div>
      </div>

      {interaction.attachments.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-semibold mb-4">Attachments ({interaction.attachments.length})</h2>
          <div className="space-y-2">
            {interaction.attachments.map((att, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                <span className="text-sm text-slate-700 dark:text-slate-300 flex-1">{att.name}</span>
                <span className="text-xs text-slate-400">{(att.size / 1024).toFixed(0)} KB</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {interaction.relatedAssets.length > 0 && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4">Related Assets ({interaction.relatedAssets.length})</h2>
            <div className="space-y-2">
              {interaction.relatedAssets.map((a) => (
                <Link key={a} to={`/assets/${a}`} className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                  {a}
                </Link>
              ))}
            </div>
          </div>
        )}
        {interaction.relatedEvidence.length > 0 && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4">Related Evidence ({interaction.relatedEvidence.length})</h2>
            <div className="space-y-2">
              {interaction.relatedEvidence.map((e) => (
                <Link key={e} to={`/evidence/${e}`} className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {e}
                </Link>
              ))}
            </div>
          </div>
        )}
        {interaction.relatedRecommendations.length > 0 && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4">Related Recommendations ({interaction.relatedRecommendations.length})</h2>
            <div className="space-y-2">
              {interaction.relatedRecommendations.map((r) => (
                <Link key={r} to={`/recommendations`} className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {r}
                </Link>
              ))}
            </div>
          </div>
        )}
        {interaction.relatedPlannerRun && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-semibold mb-4">Planner Run</h2>
            <Link to={`/planner?id=${interaction.relatedPlannerRun}`} className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline">
              <ClipboardList className="h-4 w-4" />
              {interaction.relatedPlannerRun}
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
