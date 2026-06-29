import { useEffect, useState } from 'react'
import { useInteractionService } from '@/services/interactionService'
import { useSearchParams } from 'react-router-dom'
import { Badge } from '@/components/Badge'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Modal } from '@/components/Modal'

const CUSTOMER_ID = 'C-1001'

const typeColors: Record<string, string> = {
  email: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  meeting: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  complaint: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  feedback: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  service_request: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  call_transcript: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
  crm_update: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
  chat: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
}

export default function CustomerInteractions() {
  const svc = useInteractionService()
  const [searchParams] = useSearchParams()
  const [items, setItems] = useState<{ id: string; type: string; subject: string; date: string; status: string; content: string; agent: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(searchParams.get('id'))

  useEffect(() => {
    svc.list({ customerId: CUSTOMER_ID, page: 1, limit: 100 }).then((res) => {
      setItems(res.items.map((i) => ({ id: i.id, type: i.type, subject: i.subject, date: i.date, status: i.status, content: i.content, agent: i.agent })))
    }).catch(() => {
      // silent
    }).finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const selectedItem = items.find((i) => i.id === selected)

  if (loading) return <div className="flex items-center justify-center py-20"><LoadingSpinner size="lg" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Interactions</h1>
        <p className="text-muted-foreground">{items.length} total interactions</p>
      </div>

      {items.length === 0 ? (
        <EmptyState title="No interactions" description="No interactions found for your account." />
      ) : (
        <div className="space-y-3">
          {items.map((i) => (
            <button
              key={i.id}
              type="button"
              onClick={() => setSelected(i.id)}
              className="w-full rounded-md border bg-card p-4 text-left transition-colors hover:bg-accent"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium capitalize ${typeColors[i.type] ?? 'bg-muted text-muted-foreground'}`}>
                      {i.type.replace(/_/g, ' ')}
                    </span>
                    <p className="truncate text-sm font-medium">{i.subject}</p>
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{new Date(i.date).toLocaleDateString()}</span>
                    <span>{i.agent}</span>
                  </div>
                </div>
                <Badge variant={i.status === 'resolved' ? 'default' : i.status === 'pending' ? 'secondary' : 'destructive'} className="shrink-0 text-[10px]">
                  {i.status}
                </Badge>
              </div>
            </button>
          ))}
        </div>
      )}

      <Modal open={!!selectedItem} onOpenChange={(open) => { if (!open) setSelected(null) }} title={selectedItem?.subject ?? ''}>
        {selectedItem && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-medium capitalize ${typeColors[selectedItem.type] ?? 'bg-muted text-muted-foreground'}`}>
                {selectedItem.type.replace(/_/g, ' ')}
              </span>
              <Badge variant={selectedItem.status === 'resolved' ? 'default' : 'secondary'} className="text-[10px]">{selectedItem.status}</Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {new Date(selectedItem.date).toLocaleString()} &middot; {selectedItem.agent}
            </p>
            <p className="text-sm whitespace-pre-wrap">{selectedItem.content}</p>
          </div>
        )}
      </Modal>
    </div>
  )
}
