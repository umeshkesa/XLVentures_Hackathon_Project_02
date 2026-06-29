import { useParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useKnowledgeById } from '@/services/knowledgeApiService'
import type { KnowledgeCategory } from '@/types/knowledge'

const CATEGORY_CONFIG: Record<KnowledgeCategory, { label: string; color: string; icon: string }> = {
  manual: { label: 'Manuals', color: '#3b82f6', icon: 'MAN' },
  sop: { label: 'SOPs', color: '#8b5cf6', icon: 'SOP' },
  best_practice: { label: 'Best Practices', color: '#06b6d4', icon: 'BP' },
  contract: { label: 'Contracts', color: '#f59e0b', icon: 'CTR' },
  compliance: { label: 'Compliance', color: '#22c55e', icon: 'CMP' },
  policy: { label: 'Policies', color: '#ef4444', icon: 'POL' },
  article: { label: 'Articles', color: '#f97316', icon: 'ART' },
  playbook: { label: 'Playbooks', color: '#ec4899', icon: 'PLY' },
  pdf_document: { label: 'PDF Docs', color: '#6366f1', icon: 'PDF' },
}

export default function KnowledgeDetail() {
  const { id } = useParams()
  const knowledgeQuery = useKnowledgeById(id || '')

  if (knowledgeQuery.isLoading) return <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
  if (knowledgeQuery.error) return <ErrorState message={knowledgeQuery.error.message} onRetry={() => knowledgeQuery.refetch()} />
  if (!knowledgeQuery.data) return <EmptyState title="Document not found" description="The requested document could not be found." />

  const { data: doc } = knowledgeQuery
  const cfg = CATEGORY_CONFIG[doc.category]

  return (
    <div className="max-w-5xl space-y-6">
      <Link to="/knowledge" className="inline-flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
        Back to Knowledge Center
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-flex h-8 min-w-8 items-center justify-center rounded border border-slate-200 dark:border-slate-700 text-[10px] font-bold" style={{ color: cfg.color }}>{cfg.icon}</span>
              <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
              {doc.status !== 'published' && <span className="text-xs px-2 py-0.5 rounded bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 capitalize">{doc.status}</span>}
            </div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-2">{doc.title}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">{doc.summary}</p>
            <div className="flex flex-wrap gap-2 mb-4">
              <button onClick={() => document.getElementById('doc-content')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1">
                Show document content
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </button>
              {doc.sourceUrl && <a href={doc.sourceUrl} download className="text-sm text-blue-600 dark:text-blue-400 hover:underline">Download</a>}
            </div>
            <div id="doc-content" className="prose prose-slate dark:prose-invert max-w-none text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap border-t border-slate-200 dark:border-slate-700 pt-4">{doc.content}</div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 className="font-semibold mb-3 text-sm">Document Info</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Version</span><span className="font-medium">v{doc.version}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Author</span><span className="font-medium">{doc.author}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Pages</span><span className="font-medium">{doc.pageCount}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Language</span><span className="font-medium">{doc.language.toUpperCase()}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">File Size</span><span className="font-medium">{(doc.fileSize / 1024).toFixed(0)} KB</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Created</span><span className="font-medium">{new Date(doc.createdAt).toLocaleDateString()}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Updated</span><span className="font-medium">{new Date(doc.updatedAt).toLocaleDateString()}</span></div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
            <h3 className="font-semibold mb-3 text-sm">Tags</h3>
            <div className="flex flex-wrap gap-1.5">
              {doc.tags.map((tag) => <span key={tag} className="text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded">{tag}</span>)}
            </div>
          </div>

          {doc.relatedAssets.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Assets</h3>
              <div className="space-y-1.5">{doc.relatedAssets.map((asset) => <Link key={asset} to={`/assets/${asset}`} className="block text-sm text-blue-600 dark:text-blue-400 hover:underline">{asset}</Link>)}</div>
            </div>
          )}

          {doc.relatedEvidence.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Evidence</h3>
              <div className="space-y-1.5">{doc.relatedEvidence.map((evidence) => <Link key={evidence} to={`/evidence/${evidence}`} className="block text-sm text-blue-600 dark:text-blue-400 hover:underline">{evidence}</Link>)}</div>
            </div>
          )}

          {doc.relatedRecommendations.length > 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-semibold mb-3 text-sm">Related Recommendations</h3>
              <div className="space-y-1.5">{doc.relatedRecommendations.map((recommendation) => <Link key={recommendation} to={`/recommendations?id=${recommendation}`} className="block text-sm text-blue-600 dark:text-blue-400 hover:underline">{recommendation}</Link>)}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
