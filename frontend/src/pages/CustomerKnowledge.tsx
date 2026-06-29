import { useEffect, useState } from 'react'
import { useKnowledgeService } from '@/services/knowledgeFrontendService'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Modal } from '@/components/Modal'

const categoryColors: Record<string, string> = {
  sop: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  manual: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  best_practice: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  compliance: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  policy: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  article: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
  playbook: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
  contract: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  pdf_document: 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200',
}

export default function CustomerKnowledge() {
  const svc = useKnowledgeService()
  const [items, setItems] = useState<{ id: string; title: string; category: string; summary: string; updatedAt: string; tags: string[] }[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  useEffect(() => {
    svc.list({ page: 1, limit: 100 }).then((res) => {
      setItems(res.items.map((d) => ({ id: d.id, title: d.title, category: d.category, summary: d.summary, updatedAt: d.updatedAt, tags: d.tags })))
    }).catch(() => {
      // silent
    }).finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const filtered = search
    ? items.filter((d) => d.title.toLowerCase().includes(search.toLowerCase()) || d.tags.some((t) => t.includes(search.toLowerCase())))
    : items

  const selectedItem = items.find((i) => i.id === selected)

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Center</h1>
        <p className="text-muted-foreground">Access documentation, guides, and best practices</p>
      </div>

      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search knowledge documents..."
        className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
      />

      {filtered.length === 0 ? (
        <EmptyState title="No documents" description={search ? 'No documents match your search.' : 'No knowledge documents available.'} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((d) => (
            <button
              key={d.id}
              type="button"
              onClick={() => setSelected(d.id)}
              className="rounded-md border bg-card p-4 text-left transition-colors hover:bg-accent"
            >
              <div className="mb-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium capitalize ${categoryColors[d.category] ?? 'bg-muted text-muted-foreground'}`}>
                  {d.category.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-sm font-medium line-clamp-2">{d.title}</p>
              <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{d.summary}</p>
              <p className="mt-2 text-[10px] text-muted-foreground">
                Updated {new Date(d.updatedAt).toLocaleDateString()}
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                {d.tags.slice(0, 3).map((t) => (
                  <span key={t} className="rounded bg-muted px-1 py-0.5 text-[10px] text-muted-foreground">{t}</span>
                ))}
              </div>
            </button>
          ))}
        </div>
      )}

      <Modal open={!!selectedItem} onOpenChange={(open) => { if (!open) setSelected(null) }} title={selectedItem?.title ?? ''}>
        {selectedItem && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-medium capitalize ${categoryColors[selectedItem.category] ?? 'bg-muted text-muted-foreground'}`}>
                {selectedItem.category.replace(/_/g, ' ')}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">{selectedItem.summary}</p>
            <p className="text-xs text-muted-foreground">
              Last updated: {new Date(selectedItem.updatedAt).toLocaleDateString()}
            </p>
            <div className="flex flex-wrap gap-1">
              {selectedItem.tags.map((t) => (
                <span key={t} className="rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground">{t}</span>
              ))}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
