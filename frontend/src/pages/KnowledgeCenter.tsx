import { Link, useSearchParams } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useKnowledge } from '@/services/knowledgeApiService'
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

const isKnowledgeCategory = (value: string): value is KnowledgeCategory => value in CATEGORY_CONFIG

export default function KnowledgeCenter() {
  const [searchParams, setSearchParams] = useSearchParams()
  const category = searchParams.get('category') || ''
  const search = searchParams.get('search') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const knowledgeQuery = useKnowledge({
    category: isKnowledgeCategory(category) ? category : undefined,
    search: search || undefined,
    page,
    limit: 12,
  })

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([key, value]) => { if (value) next.set(key, value); else next.delete(key) })
    if (updates.category !== undefined || updates.search !== undefined) next.delete('page')
    setSearchParams(next)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Knowledge Center</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Browse technical manuals, SOPs, best practices, and compliance documents</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <input type="text" placeholder="Search documents..." value={search} onChange={(event) => updateParams({ search: event.target.value, page: '1' })} className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-sm min-w-[280px] focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <div className="flex flex-wrap gap-2">
        <button onClick={() => updateParams({ category: '' })} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${!category ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200'}`}>All</button>
        {Object.entries(CATEGORY_CONFIG).map(([key, cfg]) => (
          <button key={key} onClick={() => updateParams({ category: key })} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${category === key ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200'}`}>
            <span className="mr-1 text-[10px] font-bold tracking-wide" style={{ color: cfg.color }}>{cfg.icon}</span>{cfg.label}
          </button>
        ))}
      </div>

      {knowledgeQuery.error && <ErrorState message={knowledgeQuery.error.message} onRetry={() => knowledgeQuery.refetch()} />}
      {knowledgeQuery.isLoading && <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>}

      {!knowledgeQuery.isLoading && !knowledgeQuery.error && (
        <>
          {knowledgeQuery.data?.items?.length === 0 ? <EmptyState title="No documents found" description="Try adjusting your search or category filter." />
            : <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {knowledgeQuery.data?.items?.map((doc) => {
                  const cfg = CATEGORY_CONFIG[doc.category]
                  return (
                    <Link key={doc.id} to={`/knowledge/${doc.id}`} className="block bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 hover:shadow-md transition-shadow">
                      <div className="flex items-start gap-3 mb-3">
                        <span className="inline-flex h-8 min-w-8 items-center justify-center rounded border border-slate-200 dark:border-slate-700 text-[10px] font-bold" style={{ color: cfg.color }}>{cfg.icon}</span>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-white px-2 py-0.5 rounded" style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
                            {doc.status === 'draft' && <span className="text-xs px-2 py-0.5 rounded bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">Draft</span>}
                          </div>
                          <h3 className="font-medium text-slate-900 dark:text-white text-sm leading-tight">{doc.title}</h3>
                        </div>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mb-3">{doc.summary}</p>
                      <div className="flex items-center gap-3 text-xs text-slate-400 dark:text-slate-500">
                        <span>v{doc.version}</span>
                        <span>{doc.pageCount} pages</span>
                        <span>{doc.language.toUpperCase()}</span>
                        <span className="ml-auto">{new Date(doc.updatedAt).toLocaleDateString()}</span>
                      </div>
                    </Link>
                  )
                })}
              </div>}
          {knowledgeQuery.data?.total && knowledgeQuery.data.total > 12 && (
            <div className="flex justify-center items-center gap-2 pt-4">
              <button disabled={page <= 1} onClick={() => updateParams({ page: String(page - 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Previous</button>
              <span className="text-sm text-slate-500 dark:text-slate-400">Page {page} of {Math.ceil(knowledgeQuery.data.total / 12)}</span>
              <button disabled={page >= Math.ceil(knowledgeQuery.data.total / 12)} onClick={() => updateParams({ page: String(page + 1) })} className="px-3 py-1.5 text-sm border border-slate-300 dark:border-slate-600 rounded-lg disabled:opacity-50 bg-white dark:bg-slate-800">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
