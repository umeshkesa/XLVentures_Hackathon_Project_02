import { useEffect, useState } from 'react'
import { useEvidenceFrontendService } from '@/services/evidenceFrontendService'
import { Badge } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Modal } from '@/components/Modal'

const CUSTOMER_ID = 'C-1001'

const typeColors: Record<string, string> = {
  sensor: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  incident: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  maintenance: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  compliance: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  customer: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  alarm: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  knowledge: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
  recommendation: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
  email: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
  report: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
}

export default function CustomerEvidence() {
  const svc = useEvidenceFrontendService()
  const [items, setItems] = useState<{ id: string; type: string; title: string; severity: string; status: string; confidence: number; timestamp: string; description: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    svc.list({ page: 1, limit: 100 }).then((res) => {
      setItems(
        res.items
          .filter((e) => e.relatedCustomers.includes(CUSTOMER_ID))
          .map((e) => ({ id: e.id, type: e.type, title: e.title, severity: e.severity, status: e.status, confidence: e.confidence, timestamp: e.timestamp, description: e.description })),
      )
    }).catch(() => {
      // silent
    }).finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const selectedItem = items.find((i) => i.id === selected)

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Evidence</h1>
        <p className="text-muted-foreground">{items.length} evidence items related to your account</p>
      </div>

      {items.length === 0 ? (
        <EmptyState title="No evidence" description="No evidence items are currently associated with your account." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((e) => (
            <button
              key={e.id}
              type="button"
              onClick={() => setSelected(e.id)}
              className="rounded-md border bg-card p-4 text-left transition-colors hover:bg-accent"
            >
              <div className="flex items-start justify-between gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium capitalize ${typeColors[e.type] ?? 'bg-muted text-muted-foreground'}`}>
                  {e.type}
                </span>
                <Badge variant={e.severity === 'critical' ? 'destructive' : e.severity === 'high' ? 'default' : 'secondary'} className="shrink-0 text-[10px]">
                  {e.severity}
                </Badge>
              </div>
              <p className="mt-2 text-sm font-medium line-clamp-2">{e.title}</p>
              <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                <span>{new Date(e.timestamp).toLocaleDateString()}</span>
                <span>Conf: {Math.round(e.confidence * 100)}%</span>
              </div>
            </button>
          ))}
        </div>
      )}

      <Modal open={!!selectedItem} onOpenChange={(open) => { if (!open) setSelected(null) }} title={selectedItem?.title ?? ''}>
        {selectedItem && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-medium capitalize ${typeColors[selectedItem.type] ?? 'bg-muted text-muted-foreground'}`}>
                {selectedItem.type}
              </span>
              <Badge variant={selectedItem.severity === 'critical' ? 'destructive' : 'secondary'} className="text-[10px]">{selectedItem.severity}</Badge>
              <Badge variant="outline" className="text-[10px]">{selectedItem.status}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{selectedItem.description}</p>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>{new Date(selectedItem.timestamp).toLocaleString()}</span>
              <span>Confidence: {Math.round(selectedItem.confidence * 100)}%</span>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
